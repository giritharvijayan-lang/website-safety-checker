import pytest
from backend.app.modules.connection import check_connection_security
from backend.app.modules.malware import check_malware
from backend.app.modules.phishing import check_phishing, detect_brand_lookalike, scan_html_for_sensitive_inputs
from backend.app.modules.reputation import check_reputation
from backend.app.modules.shopping_trust import check_shopping_trust
from backend.app.schemas import RiskLevel


@pytest.mark.asyncio
async def test_connection_security_hsts_detection(monkeypatch):
    """Verify connection module detects HSTS headers and handles HTTPS."""
    def mock_tls_cert(hostname, port, timeout):
        return {
            "cert": {
                "notAfter": "Dec 21 18:38:32 2026 GMT",
                "issuer": ((("organizationName", "Google Trust Services"),),),
            },
            "tls_version": "TLSv1.3",
            "cipher": ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256),
        }

    monkeypatch.setattr("backend.app.modules.connection._inspect_tls_cert", mock_tls_cert)

    headers_with_hsts = {"strict-transport-security": "max-age=31536000; includeSubDomains"}
    res = await check_connection_security("https://google.com", "google.com", headers=headers_with_hsts)
    assert any(s.name == "hsts_enabled" for s in res.signals)
    assert any(s.name == "valid_tls_certificate" for s in res.signals)
    assert res.score >= 80

    # Plain HTTP should flag no_https
    res_http = await check_connection_security("http://insecure-example.com", "insecure-example.com")
    assert any(s.name == "no_https" for s in res_http.signals)
    assert res_http.score <= 50


@pytest.mark.asyncio
async def test_reputation_domain_age_flags():
    """Verify reputation module flags <30 days as DOMAIN_VERY_NEW and <90 days as DOMAIN_NEW."""
    # Test < 30 days
    res_very_new = await check_reputation("https://brandnew.com", "brandnew.com", domain_age_days=15)
    assert any(s.name == "DOMAIN_VERY_NEW" for s in res_very_new.signals)
    assert res_very_new.risk_level == RiskLevel.NOT_ENOUGH_INFO.value

    # Test < 90 days
    res_new = await check_reputation("https://newsite.com", "newsite.com", domain_age_days=60)
    assert any(s.name == "DOMAIN_NEW" for s in res_new.signals)
    assert res_new.risk_level == RiskLevel.NOT_ENOUGH_INFO.value

    # Test established domain
    res_old = await check_reputation("https://google.com", "google.com", domain_age_days=3000)
    assert any(s.name == "ESTABLISHED_DOMAIN" for s in res_old.signals)
    assert res_old.risk_level == RiskLevel.SAFE.value


@pytest.mark.asyncio
async def test_phishing_lookalike_and_credential_form():
    """Verify phishing module flags brand lookalike domains and credential harvesting forms."""
    # Brand lookalike detection for Flipkart, Paytm, SBI
    signals = detect_brand_lookalike("fl1pkart.com")
    assert any(s.name == "brand_lookalike_levenshtein" for s in signals)

    signals_paytm = detect_brand_lookalike("paytmm.com")
    assert any(s.name == "brand_lookalike_levenshtein" for s in signals_paytm)

    # Legitimate official domain should NOT trigger lookalike
    clean_flipkart = detect_brand_lookalike("flipkart.com")
    assert len(clean_flipkart) == 0

    # HTML Form asking for UPI PIN, ATM PIN, CVV, OTP
    phishing_html = """
    <html>
        <body>
            <form action="/steal">
                <label>Enter UPI PIN</label>
                <input type="password" name="upi_pin" placeholder="Enter 6-digit UPI PIN" />
                <label>Card CVV</label>
                <input type="text" name="cvv" />
                <label>Enter OTP</label>
                <input type="text" name="otp" />
                <button type="submit">Verify Now</button>
            </form>
        </body>
    </html>
    """
    form_signals = scan_html_for_sensitive_inputs(phishing_html)
    assert any(s.name == "credential_harvesting_form_detected" for s in form_signals)
    detected = form_signals[0].details["solicited_credentials"]
    assert "UPI PIN" in detected
    assert "CVV" in detected
    assert "OTP" in detected

    res = await check_phishing("https://fake-sbi-portal.com", "fake-sbi-portal.com", html_content=phishing_html)
    assert res.risk_level == RiskLevel.CRITICAL.value
    assert res.score <= 15


@pytest.mark.asyncio
async def test_malware_forced_downloads_and_hidden_iframes():
    """Verify malware module inspects forced executable downloads, hidden iframes, and obfuscated scripts."""
    headers = {"Content-Disposition": 'attachment; filename="update.apk"'}
    malicious_html = """
    <html>
        <body>
            <iframe src="http://evil.com" style="display:none; width:0; height:0;"></iframe>
            <script>
                eval(unescape("%77%69%6E%64%6F%77%2E%6C%6F%63%61%74%69%6F%6E"));
            </script>
        </body>
    </html>
    """
    res = await check_malware("https://badsite.com", "badsite.com", html_content=malicious_html, headers=headers)
    assert any(s.name == "forced_executable_download_header" for s in res.signals)
    assert any(s.name == "hidden_iframe_detected" for s in res.signals)
    assert any(s.name == "obfuscated_script_detected" for s in res.signals)
    assert res.risk_level == RiskLevel.CRITICAL.value
    assert res.score <= 10


@pytest.mark.asyncio
async def test_shopping_trust_discounts_and_fake_urgency():
    """Verify shopping trust module detects extreme discount patterns, fake urgency timers, and missing GST."""
    store_html = """
    <html>
        <body>
            <h1>Special Clearance Sale</h1>
            <p>Hurry! 80% - 95% off on all items! Buy now!</p>
            <div id="sale-timer" class="countdown">Offer ends in 02:45</div>
            <button>Add to Cart</button>
        </body>
    </html>
    """
    res = await check_shopping_trust(
        "https://scamdealz.xyz",
        "scamdealz.xyz",
        html_content=store_html,
        site_type="e-commerce",
    )
    assert any(s.name == "extreme_discount_pattern" for s in res.signals)
    assert any(s.name == "fake_urgency_timer" for s in res.signals)
    assert any(s.name == "missing_business_contact_and_gst" for s in res.signals)
    # 2+ independent signals allows HIGH risk
    assert res.risk_level == RiskLevel.HIGH.value
    assert res.score <= 35
