import asyncio
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import db
from fetchers import arbeitnow, remotive, jobicy, adzuna, jsearch, himalayas, workingnomads
from services.ranker import score_job
from services.cover_letter import generate_cover_letter


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Job Lister API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/jobs")
def list_jobs(region: str = None, visa: str = None):
    return db.get_all_jobs(region=region, visa=visa)


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/api/fetch")
async def fetch_jobs():
    """Fetch latest jobs from all sources and store them."""
    arb, rem, jcy, adz, jsr, him, nom = await asyncio.gather(
        arbeitnow.fetch_jobs(pages=5),
        remotive.fetch_jobs(),
        jobicy.fetch_jobs(),
        adzuna.fetch_jobs(),
        jsearch.fetch_jobs(),
        himalayas.fetch_jobs(),
        workingnomads.fetch_jobs(),
        return_exceptions=True,
    )

    all_jobs = []
    for result in [arb, rem, jcy, adz, jsr, him, nom]:
        if isinstance(result, list):
            all_jobs.extend(result)
        else:
            print(f"Fetcher error: {result}")

    saved = 0
    for job in all_jobs:
        job["relevance_score"] = score_job(job)
        if job["relevance_score"] >= 10:  # filter out completely irrelevant
            db.upsert_job(job)
            saved += 1

    return {"fetched": len(all_jobs), "saved": saved}


@app.post("/api/jobs/{job_id}/cover-letter")
def get_cover_letter(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Return cached cover letter if it exists
    if job.get("cover_letter"):
        return {"cover_letter": job["cover_letter"]}

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

    cover_letter = generate_cover_letter(job)
    db.save_cover_letter(job_id, cover_letter)
    return {"cover_letter": cover_letter}


@app.get("/api/stats")
def get_stats():
    raw = db.get_stats()
    total = sum(r["count"] for r in raw)
    return {"total": total, "breakdown": raw}
