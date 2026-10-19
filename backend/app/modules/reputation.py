import datetime
from typing import Optional
import httpx

from backend.app.schemas import CategoryName, CategoryResult, RiskLevel, Signal


def _parse_iso_date(date_str: str) -> Optional[datetime.datetime]:
    """Parse various ISO date formats returned by RDAP servers."""
    date_str = date_str.strip()
    # Normalize Z to +00:00
    if date_str.endswith("Z"):
        date_str = date_str[:-1] + "+00:00"

    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            parsed = datetime.datetime.strptime(date_str, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=datetime.timezone.utc)
            return parsed
        except ValueError:
            continue
    return None


async def fetch_rdap_registration_date(domain: str, client: httpx.AsyncClient) -> Optional[datetime.datetime]:
    """Query RDAP asynchronously to find domain registration timestamp."""
    # Strip subdomains down to registrable domain heuristic if possible
    parts = domain.split(".")
    domain_to_query = domain
    if len(parts) > 2 and parts[-2] not in {"co", "com", "gov", "org", "net", "edu", "ac"}:
        domain_to_query = ".".join(parts[-2:])

    rdap_url = f"https://rdap.org/domain/{domain_to_query}"
    try:
        resp = await client.get(rdap_url, timeout=3.0, follow_redirects=True)
        if resp.status_code == 200:
            data = resp.json()
            events = data.get("events", [])
            for event in events:
                action = event.get("eventAction", "").lower()
                if action in {"registration", "created", "registered"}:
                    date_str = event.get("eventDate")
                    if date_str:
                        return _parse_iso_date(date_str)
    except Exception:
        pass
    return None


async def check_reputation(
    url: str,
    domain: str,
    client: Optional[httpx.AsyncClient] = None,
    domain_age_days: Optional[int] = None,
) -> CategoryResult:
    """Reputation module querying RDAP/WHOIS asynchronously to extract real registration date,
    calculate domain age in days, and flag <30 days as DOMAIN_VERY_NEW and <90 days as DOMAIN_NEW.
    """
    signals: list[Signal] = []
    score = 100
    risk = RiskLevel.SAFE.value
    details: dict = {"domain": domain}

    reg_date: Optional[datetime.datetime] = None

    # Use explicitly passed domain age if provided (e.g. testing)
    if domain_age_days is None and client is not None:
        reg_date = await fetch_rdap_registration_date(domain, client)
        if reg_date is not None:
            now = datetime.datetime.now(datetime.timezone.utc)
            domain_age_days = (now - reg_date).days
            details["registration_date"] = reg_date.isoformat()

    if domain_age_days is not None:
        details["age_days"] = domain_age_days

        if domain_age_days < 30:
            # Flag <30 days as DOMAIN_VERY_NEW
            signals.append(
                Signal(
                    name="DOMAIN_VERY_NEW",
                    description=f"Domain registered less than 30 days ago ({domain_age_days} days old)",
                    severity="INFO",
                    details={"age_days": domain_age_days},
                )
            )
            score = 70
            risk = RiskLevel.NOT_ENOUGH_INFO.value

        elif domain_age_days < 90:
            # Flag <90 days as DOMAIN_NEW
            signals.append(
                Signal(
                    name="DOMAIN_NEW",
                    description=f"Domain registered less than 90 days ago ({domain_age_days} days old)",
                    severity="INFO",
                    details={"age_days": domain_age_days},
                )
            )
            score = 75
            risk = RiskLevel.NOT_ENOUGH_INFO.value

        else:
            signals.append(
                Signal(
                    name="ESTABLISHED_DOMAIN",
                    description=f"Domain has an established history ({domain_age_days} days old)",
                    severity="INFO",
                    details={"age_days": domain_age_days},
                )
            )
            score = 100
            risk = RiskLevel.SAFE.value
    else:
        # Inconclusive/lookup failed
        signals.append(
            Signal(
                name="rdap_lookup_inconclusive",
                description="Unable to retrieve authoritative WHOIS/RDAP registration date",
                severity="INFO",
            )
        )
        score = 80
        risk = RiskLevel.UNKNOWN.value

    return CategoryResult(
        name=CategoryName.REPUTATION.value,
        score=score,
        risk_level=risk,
        signals=signals,
        details=details,
    )
