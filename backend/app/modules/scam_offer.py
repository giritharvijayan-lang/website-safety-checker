import httpx
from typing import Optional
from backend.app.schemas import CategoryName, CategoryResult, RiskLevel, Signal


async def check_scam_offer(
    url: str,
    domain: str,
    html_content: Optional[str] = None,
    site_type: Optional[str] = "general",
    client: Optional[httpx.AsyncClient] = None,
) -> CategoryResult:
    """Scam offer module analyzing prize scams, unrealistic discounts, and artificial urgency."""
    signals: list[Signal] = []
    score = 100
    risk = RiskLevel.SAFE.value

    scam_keywords = ["lottery-winner", "claim-reward", "free-iphone", "crypto-giveaway", "act-fast-urgent"]
    detected = [kw for kw in scam_keywords if kw in url.lower() or kw in domain.lower()]

    if detected:
        signals.append(
            Signal(
                name="scam_keyword_in_url",
                description=f"Suspicious scam offer keyword in URL/domain: {', '.join(detected)}",
                severity="HIGH",
                details={"keywords": detected},
            )
        )
        score -= 40

    if html_content:
        lower_html = html_content.lower()
        html_scam_phrases = ["you won a lottery", "congratulations! you have been selected", "claim your prize now", "spin to win cash"]
        matched_html = [p for p in html_scam_phrases if p in lower_html]
        if matched_html:
            signals.append(
                Signal(
                    name="scam_prize_claim_in_page",
                    description=f"Page claims fraudulent prize/lottery reward: {', '.join(matched_html)}",
                    severity="HIGH",
                    details={"phrases": matched_html},
                )
            )
            score -= 40

    # Anti-False-Positive guardrail for soft categories
    meaningful_signals = [s for s in signals if s.severity.upper() not in {"INFO", "UNKNOWN"}]
    if len(meaningful_signals) >= 2 and score <= 40:
        risk = RiskLevel.HIGH.value
    elif len(meaningful_signals) >= 1:
        risk = RiskLevel.MEDIUM.value
        score = max(50, score)
    elif score < 100:
        risk = RiskLevel.LOW.value

    return CategoryResult(
        name=CategoryName.SCAM_OFFER.value,
        score=max(0, score),
        risk_level=risk,
        signals=signals,
        details={"scam_indicators_checked": len(scam_keywords)},
    )
