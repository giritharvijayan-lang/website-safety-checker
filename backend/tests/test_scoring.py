import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app, execute_module_with_timeout
from backend.app.schemas import (
    CategoryName,
    CategoryResult,
    OverallVerdict,
    RiskLevel,
    Signal,
)
from backend.app.scoring import evaluate_scan


def test_single_malware_flag_overrides_clean_categories():
    """Requirement (a): A single malware flag overrides 4 clean categories.
    Verifies Worst-Category-Wins rule and immediate DANGEROUS verdict capped at <= 25.
    """
    # 4 clean categories with score 100
    clean_categories = [
        CategoryResult(
            name=CategoryName.CONNECTION_SECURITY.value,
            score=100,
            risk_level=RiskLevel.SAFE.value,
            signals=[],
        ),
        CategoryResult(
            name=CategoryName.TRACKERS.value,
            score=100,
            risk_level=RiskLevel.SAFE.value,
            signals=[],
        ),
        CategoryResult(
            name=CategoryName.SHOPPING_TRUST.value,
            score=100,
            risk_level=RiskLevel.SAFE.value,
            signals=[],
        ),
        CategoryResult(
            name=CategoryName.REPUTATION.value,
            score=100,
            risk_level=RiskLevel.SAFE.value,
            signals=[],
        ),
    ]

    # 1 critical malware category
    malware_category = CategoryResult(
        name=CategoryName.MALWARE.value,
        score=10,
        risk_level=RiskLevel.CRITICAL.value,
        signals=[
            Signal(
                name="executable_download_detected",
                description="Direct link to ransomware / trojan payload",
                severity="CRITICAL",
            )
        ],
    )

    all_categories = clean_categories + [malware_category]

    overall, _ = evaluate_scan(all_categories)

    # Simple average would be (100*4 + 10) / 5 = 82 (which would incorrectly look OK)
    # Worst-Category-Wins MUST force DANGEROUS and cap score at <= 25
    assert overall.verdict == OverallVerdict.DANGEROUS.value, (
        f"Expected verdict '{OverallVerdict.DANGEROUS.value}', got '{overall.verdict}'"
    )
    assert overall.score <= 25, (
        f"Overall score must be <= 25 due to critical malware, got {overall.score}"
    )
    assert overall.max_risk_category == CategoryName.MALWARE.value


def test_ten_day_old_blog_gets_not_enough_info_instead_of_high_risk():
    """Requirement (b): A 10-day-old blog with no scam signals gets NOT_ENOUGH_INFO
    instead of HIGH risk (Anti-False-Positive guardrail).
    """
    categories = [
        CategoryResult(
            name=CategoryName.PHISHING.value,
            score=100,
            risk_level=RiskLevel.SAFE.value,
            signals=[],
        ),
        CategoryResult(
            name=CategoryName.MALWARE.value,
            score=100,
            risk_level=RiskLevel.SAFE.value,
            signals=[],
        ),
        CategoryResult(
            name=CategoryName.SHOPPING_TRUST.value,
            score=100,
            risk_level=RiskLevel.SAFE.value,
            signals=[],
        ),
        CategoryResult(
            name=CategoryName.SCAM_OFFER.value,
            score=100,
            risk_level=RiskLevel.SAFE.value,
            signals=[],
        ),
        CategoryResult(
            name=CategoryName.CONNECTION_SECURITY.value,
            score=100,
            risk_level=RiskLevel.SAFE.value,
            signals=[],
        ),
        CategoryResult(
            name=CategoryName.TRACKERS.value,
            score=100,
            risk_level=RiskLevel.SAFE.value,
            signals=[],
        ),
        CategoryResult(
            name=CategoryName.REPUTATION.value,
            score=75,
            risk_level=RiskLevel.NOT_ENOUGH_INFO.value,
            signals=[
                Signal(
                    name="domain_age",
                    description="Domain registered 10 days ago",
                    severity="INFO",
                    details={"age_days": 10},
                )
            ],
        ),
    ]

    overall, sanitized = evaluate_scan(categories, domain_age_days=10)

    # Must NOT be marked HIGH risk
    assert overall.verdict == OverallVerdict.NOT_ENOUGH_INFO.value, (
        f"Expected verdict '{OverallVerdict.NOT_ENOUGH_INFO.value}', got '{overall.verdict}'"
    )
    assert overall.label == "Not enough information"
    assert overall.verdict != OverallVerdict.DANGEROUS.value

    # Verify no category is erroneously set to HIGH or CRITICAL
    for cat in sanitized:
        assert cat.risk_level not in {RiskLevel.HIGH.value, RiskLevel.CRITICAL.value}


@pytest.mark.asyncio
async def test_timed_out_module_does_not_crash_endpoint():
    """Requirement (c): A timed-out module doesn't crash the endpoint.
    Verifies graceful degradation returns UNKNOWN and endpoint returns HTTP 200.
    """
    # 1. Direct timeout runner verification
    async def slow_mock_check():
        await asyncio.sleep(0.5)
        return CategoryResult(
            name="mock",
            score=100,
            risk_level=RiskLevel.SAFE.value,
        )

    # Enforce strict 0.1s timeout to trigger timeout
    res = await execute_module_with_timeout("mock_category", slow_mock_check(), timeout=0.1)
    assert res.risk_level == RiskLevel.UNKNOWN.value
    assert any(s.name == "module_timeout" for s in res.signals)

    # 2. Endpoint integration test with httpx ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/scan", json={"url": "https://example.com"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "scan_id" in data
        assert "overall" in data
        assert "categories" in data
        assert len(data["categories"]) == 7


def test_soft_category_requires_two_signals_for_high_risk():
    """Anti-False-Positive guardrail: Soft categories (shopping_trust, scam_offer, reputation)
    MUST have at least 2 independent signals before being marked HIGH risk.
    """
    # 1 signal only - should be downgraded from HIGH to MEDIUM
    single_signal_cat = CategoryResult(
        name=CategoryName.SHOPPING_TRUST.value,
        score=35,
        risk_level=RiskLevel.HIGH.value,
        signals=[
            Signal(
                name="missing_return_policy",
                description="No return policy found on store page",
                severity="HIGH",
            )
        ],
    )

    other_cat = CategoryResult(
        name=CategoryName.CONNECTION_SECURITY.value,
        score=100,
        risk_level=RiskLevel.SAFE.value,
        signals=[],
    )

    overall, sanitized = evaluate_scan([single_signal_cat, other_cat])
    shopping_cat = next(c for c in sanitized if c.name == CategoryName.SHOPPING_TRUST.value)

    # Must be downgraded from HIGH to MEDIUM because it only has 1 signal
    assert shopping_cat.risk_level == RiskLevel.MEDIUM.value
    assert shopping_cat.score >= 50


def test_top_verdict_is_never_safe_always_looks_ok():
    """Rule: Never output the string 'Safe' or '100% Safe' as the top verdict.
    Use 'LOOKS_OK' with label 'Looks OK (No known threats found)'.
    """
    all_clean = [
        CategoryResult(name=cat.value, score=100, risk_level=RiskLevel.SAFE.value, signals=[])
        for cat in CategoryName
    ]

    overall, _ = evaluate_scan(all_clean)

    assert overall.verdict == OverallVerdict.LOOKS_OK.value
    assert overall.label == "Looks OK (No known threats found)"
    assert "safe" not in overall.verdict.lower()
    assert overall.label != "Safe"
    assert overall.label != "100% Safe"
