"""
Arbeitnow API — European jobs with native visa_sponsorship field.
Free, no auth required. https://arbeitnow.com/api/job-board-api
"""
import hashlib
import httpx
from profile import RELEVANT_TAGS

API_URL = "https://arbeitnow.com/api/job-board-api"


def _is_relevant(job: dict) -> bool:
    tags = [t.lower() for t in job.get("tags", [])]
    title = job.get("title", "").lower()
    text = title + " " + " ".join(tags)
    return any(kw in text for kw in RELEVANT_TAGS)


def _normalize(job: dict) -> dict:
    slug = job.get("slug", "")
    job_id = "arbeitnow-" + hashlib.md5(slug.encode()).hexdigest()[:12]
    visa = "yes" if job.get("visa_sponsorship") else "no"
    tags = [t.lower() for t in job.get("tags", [])]
    return {
        "id": job_id,
        "title": job.get("title", ""),
        "company": job.get("company_name", ""),
        "location": job.get("location", "Europe"),
        "description": job.get("description", ""),
        "apply_url": job.get("url", ""),
        "source": "Arbeitnow",
        "region": "europe",
        "visa_sponsorship": visa,
        "tags": tags,
        "salary": None,
    }


async def fetch_jobs(pages: int = 3) -> list[dict]:
    results = []
    async with httpx.AsyncClient(timeout=20) as client:
        for page in range(1, pages + 1):
            try:
                resp = await client.get(API_URL, params={"page": page})
                resp.raise_for_status()
                data = resp.json()
                jobs = data.get("data", [])
                if not jobs:
                    break
                for job in jobs:
                    if _is_relevant(job):
                        results.append(_normalize(job))
            except Exception as e:
                print(f"[Arbeitnow] page {page} error: {e}")
                break
    print(f"[Arbeitnow] fetched {len(results)} relevant jobs")
    return results
