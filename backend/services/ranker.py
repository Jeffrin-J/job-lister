"""
Keyword-based relevance scoring — fast, no API cost.
Score 0-100 based on how well the job matches Jeffrin's profile.
"""
from profile import RELEVANT_TAGS

HIGH_VALUE_TAGS = [
    "python", "react", "reactjs", "ai", "ml", "machine learning",
    "llm", "tensorflow", "pytorch", "cloud", "backend",
    "full stack", "fullstack", "deep learning", "rag",
]

BONUS_TAGS = [
    "django", "fastapi", "flask", "postgresql", "mongodb",
    "docker", "kubernetes", "aws", "gcp", "azure",
    "github actions", "typescript", "javascript",
]


def score_job(job: dict) -> int:
    title = job.get("title", "").lower()
    description = job.get("description", "").lower()[:3000]
    tags = [t.lower() for t in job.get("tags", [])]
    text = title + " " + " ".join(tags) + " " + description

    score = 0

    # Title match is worth a lot
    for kw in HIGH_VALUE_TAGS:
        if kw in title:
            score += 15
    for kw in BONUS_TAGS:
        if kw in title:
            score += 8

    # Tag match
    for kw in HIGH_VALUE_TAGS:
        if any(kw in t for t in tags):
            score += 8
    for kw in BONUS_TAGS:
        if any(kw in t for t in tags):
            score += 4

    # Description match (lower weight)
    for kw in HIGH_VALUE_TAGS:
        if kw in description:
            score += 3
    for kw in BONUS_TAGS:
        if kw in description:
            score += 1

    # Bonus for senior/AI/cloud roles (Jeffrin's sweet spot)
    if any(k in text for k in ["ai engineer", "ml engineer", "machine learning engineer", "cloud developer"]):
        score += 10
    if "patent" in text or "llm" in text or "rag" in text:
        score += 5

    return min(score, 100)
