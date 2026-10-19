import asyncio
import datetime
import socket
import ssl
from typing import Optional
import httpx

from backend.app.schemas import CategoryName, CategoryResult, RiskLevel, Signal


def _inspect_tls_cert(hostname: str, port: int = 443, timeout: float = 3.0) -> dict:
    """Synchronously connect and inspect the TLS certificate using standard ssl/socket."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            version = ssock.version()
            cipher = ssock.cipher()
            return {
                "cert": cert,
                "tls_version": version,
                "cipher": cipher,
            }


async def check_connection_security(
    url: str,
    domain: str,
    headers: Optional[dict[str, str]] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> CategoryResult:
    """Inspect real HTTPS availability, TLS certificate validity/expiry using ssl/socket,
    and Strict-Transport-Security (HSTS) headers.
    """
    signals: list[Signal] = []
    score = 100
    risk = RiskLevel.SAFE.value
    details: dict = {"domain": domain}

    # 1. Inspect HTTPS Protocol
    is_https = url.lower().startswith("https://")
    if not is_https:
        signals.append(
            Signal(
                name="no_https",
                description="URL does not use HTTPS; traffic is unencrypted plain text",
                severity="HIGH",
            )
        )
        score -= 50
        risk = RiskLevel.MEDIUM.value

    # 2. Inspect TLS Certificate via ssl/socket
    try:
        tls_info = await asyncio.to_thread(_inspect_tls_cert, domain, 443, 3.0)
        cert = tls_info.get("cert", {})
        details["tls_version"] = tls_info.get("tls_version")
        details["cipher"] = tls_info.get("cipher")

        not_after_str = cert.get("notAfter")
        if not_after_str:
            # Parse cert expiry date e.g. 'Dec 21 18:38:32 2026 GMT'
            expiry_dt = datetime.datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z").replace(
                tzinfo=datetime.timezone.utc
            )
            now_dt = datetime.datetime.now(datetime.timezone.utc)
            days_left = (expiry_dt - now_dt).days
            details["cert_days_until_expiry"] = days_left
            details["cert_expiry_date"] = expiry_dt.isoformat()

            if days_left < 0:
                signals.append(
                    Signal(
                        name="certificate_expired",
                        description=f"TLS certificate expired {abs(days_left)} days ago ({not_after_str})",
                        severity="CRITICAL",
                        details={"days_expired": abs(days_left)},
                    )
                )
                score = min(score, 20)
                risk = RiskLevel.CRITICAL.value
            elif days_left < 15:
                signals.append(
                    Signal(
                        name="certificate_expiring_soon",
                        description=f"TLS certificate expires in {days_left} days ({not_after_str})",
                        severity="MEDIUM",
                        details={"days_left": days_left},
                    )
                )
                score -= 20
                if risk != RiskLevel.CRITICAL.value:
                    risk = RiskLevel.MEDIUM.value
            else:
                signals.append(
                    Signal(
                        name="valid_tls_certificate",
                        description=f"Valid TLS certificate expiring in {days_left} days",
                        severity="INFO",
                        details={"days_left": days_left},
                    )
                )

        # Issuer information
        issuer = cert.get("issuer")
        if issuer:
            issuer_dict = {t[0][0]: t[0][1] for t in issuer if t and t[0]}
            details["issuer"] = issuer_dict.get("organizationName") or issuer_dict.get("commonName")

    except ssl.SSLCertVerificationError as ssl_err:
        signals.append(
            Signal(
                name="certificate_verification_failed",
                description=f"TLS certificate validation failed: {str(ssl_err)}",
                severity="HIGH",
                details={"error": str(ssl_err)},
            )
        )
        score = min(score, 30)
        risk = RiskLevel.HIGH.value
    except (socket.error, OSError, TimeoutError) as conn_err:
        if is_https:
            signals.append(
                Signal(
                    name="https_connection_refused",
                    description=f"Unable to establish TLS connection on port 443: {str(conn_err)}",
                    severity="HIGH",
                    details={"error": str(conn_err)},
                )
            )
            score = min(score, 40)
            risk = RiskLevel.HIGH.value

    # 3. Check for Strict-Transport-Security (HSTS) headers
    hsts_found = False
    if headers:
        # Case-insensitive header check
        lower_headers = {k.lower(): v for k, v in headers.items()}
        hsts_value = lower_headers.get("strict-transport-security")
        if hsts_value:
            hsts_found = True
            signals.append(
                Signal(
                    name="hsts_enabled",
                    description=f"Strict-Transport-Security header present: {hsts_value}",
                    severity="INFO",
                    details={"hsts": hsts_value},
                )
            )

    if not hsts_found and is_https:
        signals.append(
            Signal(
                name="hsts_missing",
                description="Strict-Transport-Security (HSTS) header is missing",
                severity="LOW",
            )
        )
        score -= 10

    # Determine final risk level if not already critical/high
    if score >= 80:
        risk = RiskLevel.SAFE.value
    elif score >= 50 and risk not in {RiskLevel.HIGH.value, RiskLevel.CRITICAL.value}:
        risk = RiskLevel.MEDIUM.value

    return CategoryResult(
        name=CategoryName.CONNECTION_SECURITY.value,
        score=max(0, score),
        risk_level=risk,
        signals=signals,
        details=details,
    )
