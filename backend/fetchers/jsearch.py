"""
JSearch API via RapidAPI — aggregates LinkedIn, Indeed, Glassdoor, Zip Recruiter.
Free tier: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
Set RAPIDAPI_KEY in .env
"""
import hashlib
import os
import httpx

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")
BASE_URL = "https://jsearch.p.rapidapi.com/search"
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
}

UAE_KEYWORDS = ["uae", "dubai", "abu dhabi", "sharjah", "united arab emirates"]
INDIA_KEYWORDS = ["india", "bangalore", "bengaluru", "mumbai", "hyderabad", "pune", "chennai", "delhi", "noida", "gurgaon"]
EUROPE_KEYWORDS = [
    "london", "berlin", "amsterdam", "paris", "dublin", "munich", "barcelona",
    "madrid", "milan", "stockholm", "oslo", "copenhagen", "zurich", "vienna",
    "warsaw", "prague", "lisbon", "brussels", "uk", "germany", "netherlands",
    "france", "spain", "sweden", "norway", "ireland", "austria", "switzerland",
    "poland", "czech", "europe",
]


def _detect_region(location: str) -> str:
    loc = location.lower()
    if any(k in loc for k in UAE_KEYWORDS):
        return "uae"
    if any(k in loc for k in INDIA_KEYWORDS):
        return "india"
    if any(k in loc for k in EUROPE_KEYWORDS):
        return "europe"
    return "remote"


def _detect_visa(job: dict) -> str:
    # JSearch sometimes has an explicit field
    if job.get("job_is_remote") is False:
        # Check description keywords
        pass
    desc = (job.get("job_description") or "").lower()
    highlights = str(job.get("job_highlights") or "").lower()
    text = desc + highlights
    if any(p in text for p in ["visa sponsorship", "sponsor visa", "work permit", "we sponsor", "visa support"]):
        return "yes"
    if any(n in text for n in ["no visa", "must be authorized", "cannot sponsor", "no sponsorship"]):
        return "no"
    return "unknown"


def _normalize(job: dict) -> dict:
    job_id = "jsearch-" + hashlib.md5((job.get("job_id") or "").encode()).hexdigest()[:12]
    location_parts = [
        job.get("job_city", ""),
        job.get("job_state", ""),
        job.get("job_country", ""),
    ]
    location = ", ".join(p for p in location_parts if p)
    salary = None
    sal_min = job.get("job_min_salary")
    sal_max = job.get("job_max_salary")
    sal_currency = job.get("job_salary_currency", "USD")
    if sal_min and sal_max:
        salary = f"{sal_currency} {int(sal_min):,} – {int(sal_max):,}"
    return {
        "id": job_id,
        "title": job.get("job_title", ""),
        "company": job.get("employer_name", ""),
        "location": location,
        "description": job.get("job_description", ""),
        "apply_url": job.get("job_apply_link") or job.get("job_google_link", ""),
        "source": f"JSearch ({job.get('job_publisher', 'Indeed')})",
        "region": _detect_region(location),
        "visa_sponsorship": _detect_visa(job),
        "tags": [],
        "salary": salary,
    }


async def fetch_jobs() -> list[dict]:
    if not RAPIDAPI_KEY:
        print("[JSearch] Skipped — RAPIDAPI_KEY not set in .env")
        return []

    searches = [
        "python developer Europe",
        "backend developer Europe",
        "AI engineer Europe",
        "machine learning engineer Europe",
        "cloud developer UAE Dubai",
        "software developer UAE",
        "AI engineer India Bangalore",
        "backend developer India",
        "full stack developer Europe",
    ]

    seen_ids = set()
    results = []
    async with httpx.AsyncClient(timeout=20) as client:
        for query in searches:
            try:
                resp = await client.get(
                    BASE_URL,
                    headers=HEADERS,
                    params={"query": query, "page": "1", "num_pages": "1", "date_posted": "month"},
                )
                resp.raise_for_status()
                for job in resp.json().get("data", []):
                    jid = "jsearch-" + hashlib.md5((job.get("job_id") or "").encode()).hexdigest()[:12]
                    if jid not in seen_ids:
                        seen_ids.add(jid)
                        results.append(_normalize(job))
            except Exception as e:
                print(f"[JSearch] '{query}' error: {e}")

    print(f"[JSearch] fetched {len(results)} jobs")
    return results
