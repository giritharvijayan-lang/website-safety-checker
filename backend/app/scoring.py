from typing import Optional
from backend.app.schemas import (
    CategoryName,
    CategoryResult,
    OverallResult,
    OverallVerdict,
    RiskLevel,
)

SOFT_CATEGORIES = {
    CategoryName.SHOPPING_TRUST.value,
    CategoryName.SCAM_OFFER.value,
    CategoryName.REPUTATION.value,
}

CRITICAL_OVERRIDE_CATEGORIES = {
    CategoryName.MALWARE.value,
    CategoryName.PHISHING.value,
}


def sanitize_category(cat: CategoryResult) -> CategoryResult:
    """Enforce guardrails on individual categories, notably soft categories."""
    # Guardrail: Soft categories MUST have at least 2 independent signals before being marked HIGH or CRITICAL risk
    if cat.name in SOFT_CATEGORIES:
        # Count independent non-info signals or signals in general
        meaningful_signals = [
            s for s in cat.signals if s.severity.upper() not in {"INFO", "UNKNOWN"}
        ]
        signal_count = len(meaningful_signals) if meaningful_signals else len(cat.signals)

        if signal_count < 2 and cat.risk_level in {RiskLevel.HIGH.value, RiskLevel.CRITICAL.value}:
            # Downgrade to MEDIUM risk and clamp score
            cat.risk_level = RiskLevel.MEDIUM.value
            cat.score = max(50, cat.score)
    return cat


def evaluate_scan(
    categories: list[CategoryResult],
    domain_age_days: Optional[int] = None,
) -> tuple[OverallResult, list[CategoryResult]]:
    """Evaluates category results according to AGENTS.md scoring rules:
    1. Worst-Category-Wins Scoring (min score minus minor secondary penalties, never simple average).
    2. Critical hit in malware or phishing immediately sets overall.verdict to DANGEROUS and caps score at <= 25.
    3. Soft categories (shopping_trust, scam_offer, reputation) MUST have at least 2 independent signals before being marked HIGH risk.
    4. A newly registered domain (<90 days) with no other scam signals must return NOT_ENOUGH_INFO, NOT HIGH risk.
    5. Top verdict must be LOOKS_OK with label 'Looks OK (No known threats found)', never 'Safe' or '100% Safe'.
    """
    # 1. Sanitize each category with anti-false-positive guardrails
    sanitized_categories: list[CategoryResult] = []
    for cat in categories:
        sanitized_categories.append(sanitize_category(cat))

    # Detect if any domain age signal is present if domain_age_days wasn't explicitly passed
    if domain_age_days is None:
        for cat in sanitized_categories:
            for s in cat.signals:
                if s.name in {"domain_age", "new_domain", "whois_age", "DOMAIN_VERY_NEW", "DOMAIN_NEW"} and s.details:
                    age = s.details.get("age_days") or s.details.get("days")
                    if isinstance(age, (int, float)):
                        domain_age_days = int(age)
                        break

    # Check for scam/phishing/malware signals across all categories
    has_critical_or_scam_signals = False
    has_critical_override = False

    for cat in sanitized_categories:
        if cat.name in CRITICAL_OVERRIDE_CATEGORIES:
            is_critical = (
                cat.risk_level == RiskLevel.CRITICAL.value
                or cat.score <= 25
                or any(s.severity.upper() == "CRITICAL" for s in cat.signals)
            )
            if is_critical:
                has_critical_override = True
                has_critical_or_scam_signals = True

        for s in cat.signals:
            if s.severity.upper() in {"CRITICAL", "HIGH"} and s.name != "new_domain":
                has_critical_or_scam_signals = True
            if "scam" in s.name.lower() or "malware" in s.name.lower() or "phish" in s.name.lower():
                if s.severity.upper() not in {"INFO", "UNKNOWN"}:
                    has_critical_or_scam_signals = True

    # Check domain age condition (<90 days and no other scam signals)
    is_new_domain_without_scam = (
        domain_age_days is not None
        and domain_age_days < 90
        and not has_critical_or_scam_signals
    )

    # 2. Score calculation (Worst-Category-Wins)
    # Filter out UNKNOWN categories for min score computation unless all are UNKNOWN
    scorable_cats = [
        c for c in sanitized_categories
        if c.risk_level not in {RiskLevel.UNKNOWN.value, RiskLevel.NOT_ENOUGH_INFO.value}
    ]

    if not scorable_cats:
        # All modules are UNKNOWN or NOT_ENOUGH_INFO
        overall = OverallResult(
            score=70,
            verdict=OverallVerdict.NOT_ENOUGH_INFO.value,
            label="Not enough information",
            summary="All scanning checks returned unknown or inconclusive results.",
            max_risk_category=None,
        )
        return overall, sanitized_categories

    # Worst category score
    worst_cat = min(scorable_cats, key=lambda c: c.score)
    min_score = worst_cat.score

    # Minor secondary penalties: small deduction for other categories below 80
    secondary_penalties = 0
    for cat in scorable_cats:
        if cat != worst_cat and cat.score < 80:
            secondary_penalties += max(1, int((80 - cat.score) * 0.05))

    calculated_score = max(0, min(100, min_score - secondary_penalties))

    # Determine verdict and labels
    if has_critical_override:
        # Rule: A single critical hit in malware or phishing immediately sets overall.verdict to "DANGEROUS" and caps score at <= 25
        final_score = min(25, calculated_score)
        overall = OverallResult(
            score=final_score,
            verdict=OverallVerdict.DANGEROUS.value,
            label="Dangerous (Critical threat detected)",
            summary="Critical security threats detected in malware or phishing analysis.",
            max_risk_category=worst_cat.name,
        )
    elif is_new_domain_without_scam:
        # Rule: A newly registered domain (<90 days) with no other scam signals must return "NOT_ENOUGH_INFO", NOT "HIGH" risk.
        for cat in sanitized_categories:
            if cat.name == CategoryName.REPUTATION.value and cat.risk_level in {RiskLevel.HIGH.value, RiskLevel.CRITICAL.value}:
                cat.risk_level = RiskLevel.NOT_ENOUGH_INFO.value

        overall = OverallResult(
            score=max(calculated_score, 70),
            verdict=OverallVerdict.NOT_ENOUGH_INFO.value,
            label="Not enough information",
            summary=f"Domain registered recently ({domain_age_days} days ago) with no known scam signals.",
            max_risk_category=CategoryName.REPUTATION.value,
        )
    elif calculated_score < 40 or worst_cat.risk_level in {RiskLevel.CRITICAL.value, RiskLevel.HIGH.value}:
        overall = OverallResult(
            score=calculated_score,
            verdict=OverallVerdict.DANGEROUS.value,
            label="Dangerous (High risk detected)",
            summary=f"High risk detected, driven by {worst_cat.name}.",
            max_risk_category=worst_cat.name,
        )
    elif calculated_score < 80 or worst_cat.risk_level == RiskLevel.MEDIUM.value:
        overall = OverallResult(
            score=calculated_score,
            verdict=OverallVerdict.SUSPICIOUS.value,
            label="Suspicious (Proceed with caution)",
            summary=f"Elevated risk detected in {worst_cat.name}.",
            max_risk_category=worst_cat.name,
        )
    else:
        # Rule: Never output the string "Safe" or "100% Safe" as the top verdict. Use "LOOKS_OK" with label "Looks OK (No known threats found)".
        overall = OverallResult(
            score=calculated_score,
            verdict=OverallVerdict.LOOKS_OK.value,
            label="Looks OK (No known threats found)",
            summary="No known threats detected across analyzed security categories.",
            max_risk_category=worst_cat.name,
        )

    return overall, sanitized_categories
