import re
from typing import Optional
from bs4 import BeautifulSoup
import httpx

from backend.app.schemas import CategoryName, CategoryResult, RiskLevel, Signal

# Indian GSTIN format: 2 digit state code + 10 char PAN + 1 char entity + 1 char Z + 1 char checksum
GSTIN_REGEX = re.compile(r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b")

# Extreme discount patterns: 80% to 95% off or similar unrealistic claims
EXTREME_DISCOUNT_REGEX = re.compile(
    r"(?:8[0-9]|9[0-9])%\s*-\s*(?:8[0-9]|9[0-9])%\s*off|"
    r"(?:flat|upto|up\s*to)\s*(?:8[0-9]|9[0-9])%\s*(?:off|discount)|"
    r"(?:8[0-9]|9[0-9])%\s*off\b|"
    r"save\s*(?:8[0-9]|9[0-9])%",
    re.IGNORECASE,
)

# Fake urgency and artificial scarcity patterns
URGENCY_REGEX = re.compile(
    r"\boffer\s+ends\s+in\b|"
    r"\bsale\s+ends\s+in\b|"
    r"\bdeal\s+expires\s+in\b|"
    r"\bhurry[,\s]+only\s+\d+\s+left\b|"
    r"\bonly\s+\d+\s+items?\s+remaining\b|"
    r"\blimited\s+stock[,\s]+act\s+fast\b",
    re.IGNORECASE,
)

# Business contact indicators
PHONE_REGEX = re.compile(r"(?:\+91[-.\s]?)?[6-9]\d{9}\b")
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def is_shopping_context(url: str, domain: str, html_content: str, site_type: Optional[str]) -> bool:
    """Determine whether the target page represents an e-commerce or shopping experience."""
    if site_type and any(kw in site_type.lower() for kw in ["commerce", "shop", "store", "retail"]):
        return True

    if any(kw in domain.lower() for kw in ["shop", "store", "kart", "bazaar", "deal"]):
        return True

    if html_content:
        lower_html = html_content.lower()
        shopping_markers = [
            "add to cart", "buy now", "order now", "checkout",
            "product-price", "shopping-cart", "add to bag",
            "₹", "rs.", "inr", "free delivery"
        ]
        matched_markers = [m for m in shopping_markers if m in lower_html]
        if len(matched_markers) >= 2:
            return True

    return False


async def check_shopping_trust(
    url: str,
    domain: str,
    html_content: Optional[str] = None,
    site_type: Optional[str] = "general",
    client: Optional[httpx.AsyncClient] = None,
) -> CategoryResult:
    """Shopping & E-Commerce Trust module inspecting extreme discount patterns,
    missing contact/GST details on shopping pages, and fake urgency countdown timers.
    """
    signals: list[Signal] = []
    score = 100
    risk = RiskLevel.SAFE.value
    details: dict = {"site_type": site_type}

    content = html_content or ""
    is_shopping = is_shopping_context(url, domain, content, site_type)
    details["is_shopping_context"] = is_shopping

    if content:
        soup = BeautifulSoup(content, "html.parser")
        page_text = soup.get_text()

        # 1. Inspect Extreme Discount Patterns (e.g. 80% - 95% off)
        discount_matches = EXTREME_DISCOUNT_REGEX.findall(page_text)
        if discount_matches:
            unique_matches = list(set(discount_matches))[:3]
            signals.append(
                Signal(
                    name="extreme_discount_pattern",
                    description=f"Extreme or unrealistic discount claims detected: {', '.join(unique_matches)}",
                    severity="HIGH",
                    details={"matches": unique_matches},
                )
            )
            score -= 40

        # 2. Inspect Fake Urgency and Artificial Scarcity Timers
        urgency_matches = URGENCY_REGEX.findall(page_text)
        timer_elements = soup.find_all(
            attrs={"class": re.compile(r"countdown|timer|hurry", re.IGNORECASE)}
        ) + soup.find_all(
            attrs={"id": re.compile(r"countdown|timer|hurry", re.IGNORECASE)}
        )

        if urgency_matches or timer_elements:
            signals.append(
                Signal(
                    name="fake_urgency_timer",
                    description="Artificial urgency / countdown timer detected pushing immediate purchase",
                    severity="MEDIUM",
                    details={
                        "urgency_matches": urgency_matches[:2],
                        "timer_elements_count": len(timer_elements),
                    },
                )
            )
            score -= 20

        # 3. Inspect Missing Contact / GST / Company details on Shopping Pages
        if is_shopping:
            gstin_matches = GSTIN_REGEX.findall(content)
            phone_matches = PHONE_REGEX.findall(content)
            email_matches = EMAIL_REGEX.findall(content)

            has_address = any(kw in page_text.lower() for kw in ["registered office", "head office", "physical address", "registered address"])

            if gstin_matches:
                signals.append(
                    Signal(
                        name="gstin_identified",
                        description=f"Identified Indian GST registration number: {gstin_matches[0]}",
                        severity="INFO",
                        details={"gstin": gstin_matches[0]},
                    )
                )

            # If no GSTIN, no phone, no email, and no physical address on a store
            if not gstin_matches and not phone_matches and not email_matches and not has_address:
                signals.append(
                    Signal(
                        name="missing_business_contact_and_gst",
                        description="E-Commerce store lacks verifiable business contact information, physical address, or GSTIN",
                        severity="HIGH",
                        details={"checked_elements": ["GSTIN", "Phone", "Email", "Address"]},
                    )
                )
                score -= 35

    # Enforce Anti-False-Positive guardrail for soft categories:
    # Must have at least 2 independent signals before being marked HIGH risk!
    meaningful_signals = [s for s in signals if s.severity.upper() not in {"INFO", "UNKNOWN"}]

    if len(meaningful_signals) >= 2 and any(s.severity == "HIGH" for s in signals):
        risk = RiskLevel.HIGH.value
        score = min(score, 35)
    elif len(meaningful_signals) >= 1:
        # Capped at MEDIUM risk when only 1 signal is present
        risk = RiskLevel.MEDIUM.value
        score = max(50, min(score, 75))
    else:
        risk = RiskLevel.SAFE.value
        score = max(90, score)

    return CategoryResult(
        name=CategoryName.SHOPPING_TRUST.value,
        score=max(0, score),
        risk_level=risk,
        signals=signals,
        details=details,
    )
