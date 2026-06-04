"""
Himalayas API — remote-first jobs, free, no auth.
https://himalayas.app/jobs/api
"""
import hashlib
import httpx

API_URL = "https://himalayas.app/jobs/api"

UAE_KEYWORDS = ["uae", "dubai", "abu dhabi", "united arab emirates"]
INDIA_KEYWORDS = ["india", "bangalore", "bengaluru", "mumbai", "hyderabad", "pune"]
EUROPE_KEYWORDS = [
    "europe", "uk", "germany", "netherlands", "france", "spain", "sweden",
    "ireland", "portugal", "austria", "switzerland", "poland", "denmark",
    "norway", "finland", "belgium", "worldwide", "anywhere",
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
    job_id = "himalayas-" + hashlib.md5(str(job.get("id", "")).encode()).hexdigest()[:12]
    location = job.get("location", "Remote")
    description = job.get("description", "")
    tags = [t.lower() for t in (job.get("skills") or [])]
    salary = None
    sal_min = job.get("salaryMin")
    sal_max = job.get("salaryMax")
    if sal_min and sal_max:
        salary = f"${int(sal_min):,} – ${int(sal_max):,}"
    return {
        "id": job_id,
        "title": job.get("title", ""),
        "company": job.get("company", {}).get("name", "") if isinstance(job.get("company"), dict) else "",
        "location": location,
        "description": description,
        "apply_url": job.get("applicationLink", ""),
        "source": "Himalayas",
        "region": _detect_region(location),
        "visa_sponsorship": _detect_visa(description),
        "tags": tags,
        "salary": salary,
    }


async def fetch_jobs() -> list[dict]:
    queries = [
        "python", "backend", "machine learning", "AI", "cloud", "full stack", "software engineer"
    ]
    seen_ids = set()
    results = []
    async with httpx.AsyncClient(timeout=20) as client:
        for q in queries:
            try:
                resp = await client.get(API_URL, params={"q": q, "limit": 20})
                resp.raise_for_status()
                jobs = resp.json().get("jobs", [])
                for job in jobs:
                    jid = "himalayas-" + hashlib.md5(str(job.get("id", "")).encode()).hexdigest()[:12]
                    if jid not in seen_ids:
                        seen_ids.add(jid)
                        results.append(_normalize(job))
            except Exception as e:
                print(f"[Himalayas] '{q}' error: {e}")
    print(f"[Himalayas] fetched {len(results)} jobs")
    return results
