"""
Jobicy API — remote jobs, free, no auth.
https://jobicy.com/api/v2/remote-jobs
"""
import hashlib
import httpx

API_URL = "https://jobicy.com/api/v2/remote-jobs"

UAE_KEYWORDS = ["uae", "dubai", "abu dhabi", "sharjah", "united arab emirates"]
INDIA_KEYWORDS = ["india", "bangalore", "bengaluru", "mumbai", "hyderabad", "pune", "chennai", "delhi"]
EUROPE_KEYWORDS = [
    "europe", "germany", "uk", "france", "netherlands", "spain", "italy",
    "sweden", "norway", "denmark", "finland", "austria", "switzerland",
    "portugal", "ireland", "poland", "czech", "belgium", "worldwide",
]


def _detect_region(geo: str) -> str:
    g = geo.lower()
    if any(k in g for k in UAE_KEYWORDS):
        return "uae"
    if any(k in g for k in INDIA_KEYWORDS):
        return "india"
    if any(k in g for k in EUROPE_KEYWORDS):
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
    raw_id = str(job.get("id", job.get("jobTitle", "")))
    job_id = "jobicy-" + hashlib.md5(raw_id.encode()).hexdigest()[:12]
    geo = job.get("jobGeo", "Worldwide")
    description = job.get("jobDescription", job.get("jobExcerpt", ""))
    salary = None
    sal_min = job.get("annualSalaryMin")
    sal_max = job.get("annualSalaryMax")
    currency = job.get("salaryCurrency", "USD")
    if sal_min and sal_max:
        salary = f"{currency} {sal_min:,} – {sal_max:,}"
    return {
        "id": job_id,
        "title": job.get("jobTitle", ""),
        "company": job.get("companyName", ""),
        "location": geo,
        "description": description,
        "apply_url": job.get("url", ""),
        "source": "Jobicy",
        "region": _detect_region(geo),
        "visa_sponsorship": _detect_visa(description),
        "tags": [],
        "salary": salary,
    }


async def fetch_jobs() -> list[dict]:
    results = []
    searches = [
        {"tag": "python", "count": 20},
        {"tag": "react", "count": 20},
        {"tag": "machine-learning", "count": 20},
        {"tag": "cloud", "count": 20},
        {"tag": "backend", "count": 20},
    ]
    seen_ids = set()
    async with httpx.AsyncClient(timeout=20) as client:
        for params in searches:
            try:
                resp = await client.get(API_URL, params={**params, "industry": "engineering"})
                resp.raise_for_status()
                jobs = resp.json().get("jobs", [])
                for job in jobs:
                    raw_id = str(job.get("id", job.get("jobTitle", "")))
                    jid = "jobicy-" + hashlib.md5(raw_id.encode()).hexdigest()[:12]
                    if jid not in seen_ids:
                        seen_ids.add(jid)
                        results.append(_normalize(job))
            except Exception as e:
                print(f"[Jobicy] tag '{params.get('tag')}' error: {e}")
    print(f"[Jobicy] fetched {len(results)} jobs")
    return results
