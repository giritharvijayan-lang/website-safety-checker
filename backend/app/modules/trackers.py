import re
from typing import Optional
from bs4 import BeautifulSoup
import httpx

from backend.app.schemas import CategoryName, CategoryResult, RiskLevel, Signal

KNOWN_TRACKER_PATTERNS = {
    "google_analytics": re.compile(r"google-analytics\.com|googletagmanager\.com", re.IGNORECASE),
    "facebook_pixel": re.compile(r"connect\.facebook\.net|fbevents\.js", re.IGNORECASE),
    "criteo": re.compile(r"criteo\.com|criteo\.net", re.IGNORECASE),
    "taboola": re.compile(r"taboola\.com", re.IGNORECASE),
    "outbrain": re.compile(r"outbrain\.com", re.IGNORECASE),
    "hotjar": re.compile(r"hotjar\.com|static\.hotjar\.com", re.IGNORECASE),
    "tiktok_pixel": re.compile(r"analytics\.tiktok\.com", re.IGNORECASE),
    "doubleclick": re.compile(r"doubleclick\.net", re.IGNORECASE),
}


async def check_trackers(
    url: str,
    domain: str,
    html_content: Optional[str] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> CategoryResult:
    """Trackers & privacy module analyzing ad tech, tracking beacons, and cross-site scripts."""
    signals: list[Signal] = []
    score = 100
    risk = RiskLevel.SAFE.value
    detected_trackers: list[str] = []

    # 1. Check domain itself
    for tracker_name, pattern in KNOWN_TRACKER_PATTERNS.items():
        if pattern.search(domain):
            detected_trackers.append(tracker_name)

    # 2. Check HTML scripts and pixel tags
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        scripts = soup.find_all("script", src=True)
        img_pixels = soup.find_all("img", src=True)

        all_sources = [s["src"] for s in scripts] + [i["src"] for i in img_pixels]
        for src in all_sources:
            for tracker_name, pattern in KNOWN_TRACKER_PATTERNS.items():
                if pattern.search(src) and tracker_name not in detected_trackers:
                    detected_trackers.append(tracker_name)

    if detected_trackers:
        signals.append(
            Signal(
                name="third_party_trackers_detected",
                description=f"Detected {len(detected_trackers)} third-party tracking network(s): {', '.join(detected_trackers)}",
                severity="INFO" if len(detected_trackers) <= 2 else "MEDIUM",
                details={"trackers": detected_trackers, "count": len(detected_trackers)},
            )
        )
        if len(detected_trackers) > 4:
            score = 65
            risk = RiskLevel.MEDIUM.value
        elif len(detected_trackers) > 0:
            score = 85
            risk = RiskLevel.SAFE.value

    return CategoryResult(
        name=CategoryName.TRACKERS.value,
        score=score,
        risk_level=risk,
        signals=signals,
        details={"scanned_domain": domain, "tracker_count": len(detected_trackers)},
    )
