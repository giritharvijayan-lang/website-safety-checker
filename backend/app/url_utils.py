from typing import Optional
from urllib.parse import urlparse, urlunparse
import httpx

KNOWN_SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "adf.ly",
    "bl.ink",
    "lnkd.in",
    "rebrand.ly",
    "cutt.ly",
    "shorturl.at",
}


def normalize_url(raw_url: str) -> str:
    """Normalize input URL: add scheme if missing, strip spaces, lowercase host."""
    url = raw_url.strip()
    if not url:
        raise ValueError("URL cannot be empty")

    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"

    return urlunparse((scheme, netloc, path, parsed.params, parsed.query, parsed.fragment))


def extract_domain(url: str) -> str:
    """Extract domain hostname from URL without port."""
    parsed = urlparse(url)
    host = parsed.hostname or ""
    return host.lower()


async def unroll_shortened_url(url: str, client: Optional[httpx.AsyncClient] = None, timeout: float = 2.0) -> tuple[str, str]:
    """Follow redirects to unroll shortened or redirected URLs gracefully.
    Returns (final_url, final_domain).
    """
    normalized = normalize_url(url)
    domain = extract_domain(normalized)

    # Check if domain looks like a shortener or we want to follow redirects
    should_unroll = any(shortener in domain for shortener in KNOWN_SHORTENERS)

    if not should_unroll:
        return normalized, domain

    try:
        if client is not None:
            resp = await client.head(normalized, follow_redirects=True, timeout=timeout)
            final_url = str(resp.url)
            return normalize_url(final_url), extract_domain(final_url)
        else:
            async with httpx.AsyncClient() as new_client:
                resp = await new_client.head(normalized, follow_redirects=True, timeout=timeout)
                final_url = str(resp.url)
                return normalize_url(final_url), extract_domain(final_url)
    except Exception:
        # Graceful fallback: return normalized original
        return normalized, domain
