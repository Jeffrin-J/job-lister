"""
Adzuna API — broad coverage for Europe, UAE, India.
Free tier: register at https://developer.adzuna.com to get app_id + app_key.
Set ADZUNA_APP_ID and ADZUNA_APP_KEY in .env
"""
import hashlib
import os
import httpx
from profile import TARGET_ROLES

APP_ID = os.environ.get("ADZUNA_APP_ID", "")
APP_KEY = os.environ.get("ADZUNA_APP_KEY", "")

# Adzuna country codes → our region
COUNTRY_MAP = {
    "gb": "europe", "de": "europe", "nl": "europe", "fr": "europe",
    "es": "europe", "it": "europe", "at": "europe", "be": "europe",
    "pl": "europe", "se": "europe", "ch": "europe", "pt": "europe",
    "ae": "uae",
    "in": "india",
}

BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def _detect_visa(description: str) -> str:
    desc = description.lower()
    if any(p in desc for p in ["visa sponsorship", "sponsor visa", "work permit", "we sponsor", "relocation"]):
        return "yes"
    if any(n in desc for n in ["no visa", "must be authorized", "cannot sponsor", "no sponsorship", "right to work"]):
        return "no"
    return "unknown"


def _normalize(job: dict, region: str) -> dict:
    job_id = "adzuna-" + hashlib.md5(str(job.get("id", "")).encode()).hexdigest()[:12]
    salary = None
    sal_min = job.get("salary_min")
    sal_max = job.get("salary_max")
    if sal_min and sal_max:
        salary = f"£{int(sal_min):,} – £{int(sal_max):,}"
    elif sal_min:
        salary = f"from £{int(sal_min):,}"
    description = job.get("description", "")
    return {
        "id": job_id,
        "title": job.get("title", ""),
        "company": job.get("company", {}).get("display_name", "Unknown"),
        "location": job.get("location", {}).get("display_name", ""),
        "description": description,
        "apply_url": job.get("redirect_url", ""),
        "source": "Adzuna",
        "region": region,
        "visa_sponsorship": _detect_visa(description),
        "tags": [],
        "salary": salary,
    }


async def _fetch_country(client: httpx.AsyncClient, country: str, region: str, query: str) -> list[dict]:
    results = []
    try:
        resp = await client.get(
            f"{BASE_URL}/{country}/search/1",
            params={
                "app_id": APP_ID,
                "app_key": APP_KEY,
                "results_per_page": 20,
                "what": query,
                "content-type": "application/json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        for job in resp.json().get("results", []):
            results.append(_normalize(job, region))
    except Exception as e:
        print(f"[Adzuna] {country}/{query} error: {e}")
    return results


async def fetch_jobs() -> list[dict]:
    if not APP_ID or not APP_KEY:
        print("[Adzuna] Skipped — ADZUNA_APP_ID/ADZUNA_APP_KEY not set in .env")
        return []

    searches = [
        ("python developer", ["gb", "de", "nl", "ae", "in"]),
        ("backend developer", ["gb", "de", "nl", "ae", "in"]),
        ("AI engineer", ["gb", "de", "ae", "in"]),
        ("machine learning engineer", ["gb", "de", "in"]),
        ("cloud developer", ["gb", "de", "ae", "in"]),
        ("full stack developer", ["gb", "nl", "ae", "in"]),
    ]

    seen_ids = set()
    results = []
    async with httpx.AsyncClient() as client:
        for query, countries in searches:
            for country in countries:
                region = COUNTRY_MAP.get(country, "europe")
                jobs = await _fetch_country(client, country, region, query)
                for job in jobs:
                    if job["id"] not in seen_ids:
                        seen_ids.add(job["id"])
                        results.append(job)

    print(f"[Adzuna] fetched {len(results)} jobs")
    return results
