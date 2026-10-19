import asyncio
import uuid
from typing import Any, Coroutine, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import httpx

from backend.app.web_ui import INDEX_HTML

from backend.app.schemas import (
    CategoryName,
    CategoryResult,
    RiskLevel,
    ScanRequest,
    ScanResponse,
    Signal,
)
from backend.app.scoring import evaluate_scan
from backend.app.url_utils import extract_domain, normalize_url, unroll_shortened_url
from backend.app.modules.connection import check_connection_security
from backend.app.modules.malware import check_malware
from backend.app.modules.phishing import check_phishing
from backend.app.modules.reputation import check_reputation
from backend.app.modules.scam_offer import check_scam_offer
from backend.app.modules.shopping_trust import check_shopping_trust
from backend.app.modules.trackers import check_trackers

app = FastAPI(
    title="Website Safety Checker API",
    version="1.0.0",
    description="Modular Website Safety Checker API evaluating URLs across 7 security categories.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def execute_module_with_timeout(
    category_name: str,
    coro: Coroutine[Any, Any, CategoryResult],
    timeout: float = 3.5,
) -> CategoryResult:
    """Execute a single check module wrapped in asyncio.wait_for with graceful degradation."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except (asyncio.TimeoutError, TimeoutError):
        return CategoryResult(
            name=category_name,
            score=100,
            risk_level=RiskLevel.UNKNOWN.value,
            signals=[
                Signal(
                    name="module_timeout",
                    description=f"Check module '{category_name}' timed out after {timeout}s",
                    severity="UNKNOWN",
                )
            ],
            details={"error": "timeout", "timeout_seconds": timeout},
        )
    except Exception as exc:
        return CategoryResult(
            name=category_name,
            score=100,
            risk_level=RiskLevel.UNKNOWN.value,
            signals=[
                Signal(
                    name="module_error",
                    description=f"Check module '{category_name}' encountered an error: {str(exc)}",
                    severity="UNKNOWN",
                )
            ],
            details={"error": str(exc)},
        )


async def fetch_target_page(url: str, client: httpx.AsyncClient) -> tuple[str, dict[str, str]]:
    """Quickly fetch target page HTML and headers for inspection, with graceful fallback."""
    try:
        resp = await client.get(url, timeout=2.5, follow_redirects=True)
        headers_dict = {k: v for k, v in resp.headers.items()}
        return resp.text, headers_dict
    except Exception:
        return "", {}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve sleek mobile-responsive Web App UI directly for immediate in-browser testing."""
    return HTMLResponse(content=INDEX_HTML)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/v1/scan", response_model=ScanResponse)
async def scan_url(request: ScanRequest):
    # 1. URL Normalization
    try:
        raw_normalized = normalize_url(request.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Unroll shortened links
    async with httpx.AsyncClient(timeout=2.0) as client:
        unrolled_url, domain = await unroll_shortened_url(raw_normalized, client=client)

    site_type = request.site_type or "general"

    # 3. Fetch target page HTML and response headers
    async with httpx.AsyncClient(timeout=3.5, verify=False) as scan_client:
        html_content, response_headers = await fetch_target_page(unrolled_url, scan_client)

        # 4. Concurrently execute all 7 category checks with strict 3.5s timeout per module
        tasks = [
            execute_module_with_timeout(
                CategoryName.CONNECTION_SECURITY.value,
                check_connection_security(
                    unrolled_url, domain, headers=response_headers, client=scan_client
                ),
            ),
            execute_module_with_timeout(
                CategoryName.REPUTATION.value,
                check_reputation(unrolled_url, domain, client=scan_client),
            ),
            execute_module_with_timeout(
                CategoryName.PHISHING.value,
                check_phishing(unrolled_url, domain, html_content=html_content, client=scan_client),
            ),
            execute_module_with_timeout(
                CategoryName.MALWARE.value,
                check_malware(
                    unrolled_url,
                    domain,
                    html_content=html_content,
                    headers=response_headers,
                    client=scan_client,
                ),
            ),
            execute_module_with_timeout(
                CategoryName.SHOPPING_TRUST.value,
                check_shopping_trust(
                    unrolled_url,
                    domain,
                    html_content=html_content,
                    site_type=site_type,
                    client=scan_client,
                ),
            ),
            execute_module_with_timeout(
                CategoryName.SCAM_OFFER.value,
                check_scam_offer(
                    unrolled_url,
                    domain,
                    html_content=html_content,
                    site_type=site_type,
                    client=scan_client,
                ),
            ),
            execute_module_with_timeout(
                CategoryName.TRACKERS.value,
                check_trackers(
                    unrolled_url, domain, html_content=html_content, client=scan_client
                ),
            ),
        ]

        category_results = await asyncio.gather(*tasks)

    # 5. Run scoring engine with worst-category-wins & guardrails
    overall_result, evaluated_categories = evaluate_scan(list(category_results))

    scan_id = str(uuid.uuid4())
    return ScanResponse(
        scan_id=scan_id,
        url=unrolled_url,
        domain=domain,
        site_type=site_type,
        overall=overall_result,
        categories=evaluated_categories,
    )
