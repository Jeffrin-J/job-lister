"""
Working Nomads API — curated remote tech jobs, free, no auth.
https://www.workingnomads.com/api/exposed_jobs/
"""
import hashlib
import httpx

API_URL = "https://www.workingnomads.com/api/exposed_jobs/"

UAE_KEYWORDS = ["uae", "dubai", "abu dhabi", "united arab emirates"]
INDIA_KEYWORDS = ["india", "bangalore", "bengaluru", "mumbai", "hyderabad"]
EUROPE_KEYWORDS = [
    "europe", "uk", "germany", "netherlands", "france", "spain", "sweden",
    "ireland", "portugal", "austria", "switzerland", "poland", "worldwide", "anywhere",
]

RELEVANT_CATEGORIES = [
    "back-end-programming", "full-stack-programming", "front-end-programming",
    "dev-ops-sysadmin", "data-science", "machine-learning",
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
    if any(p in desc for p in ["visa sponsorship", "sponsor visa", "work permit", "we sponsor"]):
        return "yes"
    if any(n in desc for n in ["no visa", "must be authorized", "cannot sponsor", "no sponsorship"]):
        return "no"
    return "unknown"


def _normalize(job: dict) -> dict:
    job_id = "nomads-" + hashlib.md5(str(job.get("id", "")).encode()).hexdigest()[:12]
    location = job.get("location", "Remote")
    description = job.get("description", "")
    tags = [t.lower() for t in (job.get("tags") or [])]
    return {
        "id": job_id,
        "title": job.get("title", ""),
        "company": job.get("company_name", ""),
        "location": location,
        "description": description,
        "apply_url": job.get("url", ""),
        "source": "Working Nomads",
        "region": _detect_region(location),
        "visa_sponsorship": _detect_visa(description),
        "tags": tags,
        "salary": None,
    }


async def fetch_jobs() -> list[dict]:
    results = []
    seen_ids = set()
    async with httpx.AsyncClient(timeout=20) as client:
        for category in RELEVANT_CATEGORIES:
            try:
                resp = await client.get(API_URL, params={"category": category})
                resp.raise_for_status()
                jobs = resp.json() if isinstance(resp.json(), list) else resp.json().get("jobs", [])
                for job in jobs:
                    jid = "nomads-" + hashlib.md5(str(job.get("id", "")).encode()).hexdigest()[:12]
                    if jid not in seen_ids:
                        seen_ids.add(jid)
                        results.append(_normalize(job))
            except Exception as e:
                print(f"[WorkingNomads] '{category}' error: {e}")
    print(f"[WorkingNomads] fetched {len(results)} jobs")
    return results
