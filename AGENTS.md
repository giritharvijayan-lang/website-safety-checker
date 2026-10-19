# AGENTS.md — Website Safety Checker Architecture & Rules

## 1. Project Overview
A modular Website Safety Checker mobile app and backend API. Given any URL, the system evaluates safety across distinct categories (Phishing, Malware, Shopping/E-Commerce Trust, Scam Offers, Connection Security, Trackers, Reputation) and returns a category-by-category breakdown plus an overall verdict.

## 2. Tech Stack & Monorepo Structure
- `/backend`: Python 3.12+, FastAPI, Pydantic v2, `httpx` (async HTTP), `beautifulsoup4`, `python-whois` / RDAP, `redis` (caching), `pytest`.
- `/mobile`: Flutter (Dart) with Riverpod for state management, `receive_sharing_intent` for OS share sheet handling.
- `/shared`: JSON sample payloads and API contract schemas.

## 3. Core Engineering Rules (Strict Enforcement)
1. **Parallel Execution & Timeouts:** All modules inside `/scan` MUST execute concurrently using `asyncio.gather()`. Every individual check module must enforce a strict `3.5s` timeout (`asyncio.wait_for`).
2. **Graceful Degradation:** If a module (e.g., WHOIS or VirusTotal) times out or errors out, catch the exception and return `risk_level: "UNKNOWN"` for that module. NEVER fail the entire `/scan` request because a single module failed.
3. **Worst-Category-Wins Scoring:** 
   - Overall score is driven by `min(category_scores)` minus minor secondary penalties—NEVER use a simple average.
   - A single critical hit in `malware` or `phishing` immediately sets `overall.verdict` to `"DANGEROUS"` and caps the score at `<= 25`.
4. **Anti-False-Positive Guardrails:**
   - Soft categories (`shopping_trust`, `scam_offer`, `reputation`) MUST have at least **2 independent signals** before being marked `HIGH` risk.
   - A newly registered domain (<90 days) with no other scam signals must return `"NOT_ENOUGH_INFO"` ("Not enough information"), NOT `"HIGH"` risk.
   - Never output the string "Safe" or "100% Safe" as the top verdict. Use `"LOOKS_OK"` with label `"Looks OK (No known threats found)"`.
