import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            description TEXT,
            apply_url TEXT,
            source TEXT,
            region TEXT,
            visa_sponsorship TEXT DEFAULT 'unknown',
            relevance_score INTEGER DEFAULT 0,
            tags TEXT DEFAULT '[]',
            salary TEXT,
            fetched_at TEXT,
            cover_letter TEXT
        )
    """)
    conn.commit()
    conn.close()


def upsert_job(job: dict):
    conn = get_db()
    conn.execute("""
        INSERT OR REPLACE INTO jobs
        (id, title, company, location, description, apply_url, source, region,
         visa_sponsorship, relevance_score, tags, salary, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job["id"], job["title"], job["company"],
        job.get("location"), job.get("description"),
        job.get("apply_url"), job.get("source"), job.get("region"),
        job.get("visa_sponsorship", "unknown"),
        job.get("relevance_score", 0),
        json.dumps(job.get("tags", [])),
        job.get("salary"),
        datetime.utcnow().isoformat(),
    ))
    conn.commit()
    conn.close()


def get_all_jobs(region: str = None, visa: str = None):
    conn = get_db()
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []
    if region:
        query += " AND region = ?"
        params.append(region)
    if visa:
        query += " AND visa_sponsorship = ?"
        params.append(visa)
    query += " ORDER BY relevance_score DESC, fetched_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["tags"] = json.loads(d.get("tags") or "[]")
        result.append(d)
    return result


def get_job(job_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["tags"] = json.loads(d.get("tags") or "[]")
    return d


def save_cover_letter(job_id: str, cover_letter: str):
    conn = get_db()
    conn.execute("UPDATE jobs SET cover_letter = ? WHERE id = ?", (cover_letter, job_id))
    conn.commit()
    conn.close()


def get_stats():
    conn = get_db()
    rows = conn.execute("""
        SELECT region, visa_sponsorship, COUNT(*) as count
        FROM jobs GROUP BY region, visa_sponsorship
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
