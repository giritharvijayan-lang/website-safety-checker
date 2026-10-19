import re
from typing import Optional
from bs4 import BeautifulSoup
import httpx

from backend.app.schemas import CategoryName, CategoryResult, RiskLevel, Signal

CURATED_BRANDS = {
    "sbi": {"official_domains": ["onlinesbi.sbi", "sbi.co.in", "sbi.bank"], "names": ["sbi", "onlinesbi"]},
    "hdfc": {"official_domains": ["hdfcbank.com", "hdfc.com"], "names": ["hdfc", "hdfcbank"]},
    "icici": {"official_domains": ["icicibank.com", "icicidirect.com"], "names": ["icici", "icicibank"]},
    "axis": {"official_domains": ["axisbank.com"], "names": ["axisbank", "axis"]},
    "paytm": {"official_domains": ["paytm.com", "paytmmall.com"], "names": ["paytm"]},
    "phonepe": {"official_domains": ["phonepe.com"], "names": ["phonepe"]},
    "gpay": {"official_domains": ["pay.google.com", "google.com"], "names": ["gpay", "googlepay"]},
    "amazon": {"official_domains": ["amazon.in", "amazon.com"], "names": ["amazon"]},
    "flipkart": {"official_domains": ["flipkart.com"], "names": ["flipkart"]},
    "meesho": {"official_domains": ["meesho.com"], "names": ["meesho"]},
    "indiapost": {"official_domains": ["indiapost.gov.in", "indiapostgdsonline.gov.in"], "names": ["indiapost"]},
    "irctc": {"official_domains": ["irctc.co.in"], "names": ["irctc"]},
}

# Common Cyrillic / Greek homoglyphs used in phishing
HOMOGLYPH_CHARS = {
    '\u0430': 'a', '\u0435': 'e', '\u043e': 'o', '\u0440': 'p',
    '\u0441': 'c', '\u0443': 'y', '\u0445': 'x', '\u0456': 'i',
    '\u03bf': 'o', '\u03c5': 'u', '\u03bd': 'v', '\u0455': 's',
}


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def is_official_brand_domain(domain: str, brand_data: dict) -> bool:
    """Check if domain is legitimately owned by the brand."""
    for official in brand_data["official_domains"]:
        if domain == official or domain.endswith("." + official):
            return True
    return False


def detect_brand_lookalike(domain: str) -> list[Signal]:
    """Inspect domain for homographs and Levenshtein lookalikes against curated brands."""
    signals: list[Signal] = []
    lower_domain = domain.lower()

    # Extract base domain name without TLD (e.g., 'flipkart' from 'flipkart.com' or 'flipk4rt' from 'flipk4rt.org')
    parts = lower_domain.split(".")
    base_labels = parts[:-1] if len(parts) > 1 else parts

    # 1. Homograph Detection (Punycode / IDN or Cyrillic homoglyphs)
    if "xn--" in lower_domain:
        signals.append(
            Signal(
                name="punycode_homograph_domain",
                description=f"Domain uses Punycode/IDN internationalized characters: {domain}",
                severity="CRITICAL",
                details={"domain": domain},
            )
        )
    else:
        has_homoglyphs = any(ch in domain for ch in HOMOGLYPH_CHARS)
        if has_homoglyphs:
            signals.append(
                Signal(
                    name="homoglyph_brand_spoofing",
                    description=f"Domain contains mixed-script homoglyphs resembling Latin letters: {domain}",
                    severity="CRITICAL",
                    details={"domain": domain},
                )
            )

    # 2. Levenshtein & Lookalike detection against curated brands
    for brand_key, brand_info in CURATED_BRANDS.items():
        if is_official_brand_domain(lower_domain, brand_info):
            continue  # Legitimate domain, skip

        for brand_name in brand_info["names"]:
            for label in base_labels:
                # 1. Levenshtein distance check on domain tokens (typosquatting e.g. fl1pkart, paytmm, amzn)
                if abs(len(label) - len(brand_name)) <= 2 and label != brand_name:
                    dist = levenshtein_distance(label, brand_name)
                    if 1 <= dist <= 2 and len(brand_name) >= 3:
                        signals.append(
                            Signal(
                                name="brand_lookalike_levenshtein",
                                description=(
                                    f"Domain label '{label}' is a typosquatting lookalike "
                                    f"of '{brand_key.upper()}' (edit distance {dist})"
                                ),
                                severity="CRITICAL",
                                details={"brand": brand_key, "label": label, "distance": dist},
                            )
                        )
                        break

                # 2. Check compound brand keyword impersonation in untrusted domain (e.g. paytm-rewards.com)
                if brand_name in label:
                    signals.append(
                        Signal(
                            name="brand_keyword_impersonation",
                            description=f"Domain impersonates official brand '{brand_key.upper()}': {domain}",
                            severity="HIGH",
                            details={"brand": brand_key, "domain": domain},
                        )
                    )
                    break

    return signals


def scan_html_for_sensitive_inputs(html_content: str) -> list[Signal]:
    """Scan HTML form tags for suspicious inputs asking for 'UPI PIN', 'ATM PIN', 'CVV', or 'OTP'."""
    signals: list[Signal] = []
    if not html_content:
        return signals

    soup = BeautifulSoup(html_content, "html.parser")
    forms = soup.find_all("form")

    sensitive_patterns = {
        "UPI PIN": re.compile(r"\bupi[-_\s]*pin\b", re.IGNORECASE),
        "ATM PIN": re.compile(r"\batm[-_\s]*pin\b|\bcard[-_\s]*pin\b", re.IGNORECASE),
        "CVV": re.compile(r"\bcvv\b|\bcvc\b|\bsecurity[-_\s]*code\b|\bcard[-_\s]*verification\b", re.IGNORECASE),
        "OTP": re.compile(r"\botp\b|\bone[-_\s]*time[-_\s]*password\b", re.IGNORECASE),
    }

    detected_targets: set[str] = set()

    for form in forms:
        form_text = form.get_text()
        inputs = form.find_all(["input", "textarea", "select"])

        for input_tag in inputs:
            # Check name, id, placeholder, and aria-label attributes
            attributes_str = " ".join([
                str(input_tag.get("name", "")),
                str(input_tag.get("id", "")),
                str(input_tag.get("placeholder", "")),
                str(input_tag.get("aria-label", "")),
            ])

            for target_name, pattern in sensitive_patterns.items():
                if pattern.search(attributes_str) or pattern.search(form_text):
                    detected_targets.add(target_name)

    if detected_targets:
        targets_list = sorted(list(detected_targets))
        signals.append(
            Signal(
                name="credential_harvesting_form_detected",
                description=f"HTML form solicits sensitive credentials: {', '.join(targets_list)}",
                severity="CRITICAL",
                details={"solicited_credentials": targets_list},
            )
        )

    return signals


async def check_phishing(
    url: str,
    domain: str,
    html_content: Optional[str] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> CategoryResult:
    """Phishing detection module implementing homograph/Levenshtein lookalike detection
    against top Indian and global brands, and scanning HTML <form> tags for sensitive credential inputs.
    """
    signals: list[Signal] = []
    score = 100
    risk = RiskLevel.SAFE.value

    # 1. Homograph & Lookalike check
    brand_signals = detect_brand_lookalike(domain)
    signals.extend(brand_signals)

    for s in brand_signals:
        if s.severity == "CRITICAL":
            score = min(score, 15)
            risk = RiskLevel.CRITICAL.value
        elif s.severity == "HIGH":
            score = min(score, 35)
            if risk != RiskLevel.CRITICAL.value:
                risk = RiskLevel.HIGH.value

    # 2. HTML Form Inspection for UPI PIN, ATM PIN, CVV, OTP
    if html_content:
        form_signals = scan_html_for_sensitive_inputs(html_content)
        signals.extend(form_signals)

        for s in form_signals:
            if s.severity == "CRITICAL":
                score = min(score, 10)
                risk = RiskLevel.CRITICAL.value

    # 3. Heuristic URL checks
    suspicious_phishing_paths = ["login", "verify", "secure", "update-account", "signin", "banking"]
    matched_paths = [kw for kw in suspicious_phishing_paths if f"/{kw}" in url.lower() or f"={kw}" in url.lower()]
    if matched_paths and risk == RiskLevel.SAFE.value:
        signals.append(
            Signal(
                name="suspicious_login_path",
                description=f"Path contains sensitive authentication keywords: {', '.join(matched_paths)}",
                severity="LOW",
                details={"paths": matched_paths},
            )
        )
        score -= 15
        risk = RiskLevel.LOW.value

    return CategoryResult(
        name=CategoryName.PHISHING.value,
        score=max(0, score),
        risk_level=risk,
        signals=signals,
        details={"scanned_domain": domain, "signals_count": len(signals)},
    )
