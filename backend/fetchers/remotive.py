"""
Remotive API — remote jobs globally, free, no auth.
https://remotive.com/api/remote-jobs
"""
import hashlib
import httpx
from profile import TARGET_ROLES

API_URL = "https://remotive.com/api/remote-jobs"

UAE_KEYWORDS = ["uae", "dubai", "abu dhabi", "sharjah", "united arab emirates"]
INDIA_KEYWORDS = ["india", "bangalore", "bengaluru", "mumbai", "hyderabad", "pune", "chennai", "delhi"]
EUROPE_KEYWORDS = [
    "europe", "germany", "uk", "france", "netherlands", "spain", "italy",
    "sweden", "norway", "denmark", "finland", "austria", "switzerland",
    "portugal", "ireland", "poland", "czech", "belgium", "amsterdam",
    "berlin", "paris", "london", "munich", "barcelona", "remote (europe)",
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


def _detect_visa(description: str) -> str:
    desc = description.lower()
    positive = ["visa sponsorship", "sponsor visa", "work permit", "we sponsor", "sponsoring visa"]
    negative = ["no visa", "must be authorized", "must already", "no sponsorship", "cannot sponsor"]
    if any(p in desc for p in positive):
        return "yes"
    if any(n in desc for n in negative):
        return "no"
    return "unknown"


def _normalize(job: dict) -> dict:
    job_id = "remotive-" + hashlib.md5(str(job.get("id", "")).encode()).hexdigest()[:12]
    location = job.get("candidate_required_location", "Worldwide")
    region = _detect_region(location)
    description = job.get("description", "")
    return {
        "id": job_id,
        "title": job.get("title", ""),
        "company": job.get("company_name", ""),
        "location": location,
        "description": description,
        "apply_url": job.get("url", ""),
        "source": "Remotive",
        "region": region,
        "visa_sponsorship": _detect_visa(description),
        "tags": [t.lower() for t in job.get("tags", [])],
        "salary": job.get("salary", None),
    }


async def fetch_jobs() -> list[dict]:
    results = []
    searches = ["python developer", "backend developer", "AI engineer", "machine learning", "cloud developer", "full stack"]
    seen_ids = set()
    async with httpx.AsyncClient(timeout=20) as client:
        for search in searches:
            try:
                resp = await client.get(API_URL, params={"search": search, "limit": 20})
                resp.raise_for_status()
                jobs = resp.json().get("jobs", [])
                for job in jobs:
                    jid = "remotive-" + hashlib.md5(str(job.get("id", "")).encode()).hexdigest()[:12]
                    if jid not in seen_ids:
                        seen_ids.add(jid)
                        results.append(_normalize(job))
            except Exception as e:
                print(f"[Remotive] search '{search}' error: {e}")
    print(f"[Remotive] fetched {len(results)} jobs")
    return results
