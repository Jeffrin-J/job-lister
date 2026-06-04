import os
import anthropic
from profile import CANDIDATE_PROFILE

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def generate_cover_letter(job: dict) -> str:
    job_title = job.get("title", "")
    company = job.get("company", "")
    location = job.get("location", "")
    description = job.get("description", "")[:4000]
    tags = ", ".join(job.get("tags", []))

    prompt = f"""You are a professional cover letter writer. Write a compelling, personalized cover letter for the following job application.

CANDIDATE PROFILE:
{CANDIDATE_PROFILE}

JOB DETAILS:
Title: {job_title}
Company: {company}
Location: {location}
Tags/Skills required: {tags}
Job Description:
{description}

INSTRUCTIONS:
- Write a professional cover letter in 3-4 paragraphs
- Opening: Express enthusiasm for the specific role at this specific company
- Middle paragraphs: Draw direct connections between Jeffrin's experience (HPE Cloud Developer, AI patent, MSc AI at Edinburgh) and the job requirements
- Highlight the most relevant skills and projects from his profile that match this job
- Mention his current MSc AI at Edinburgh as a strength
- Closing: Express eagerness to discuss further, confidence about contributing
- Tone: Professional but personable, not generic
- Do NOT use placeholder text like [Your Name] — fill everything in using Jeffrin's actual details
- Sign off as: Jeffrin Jacob | jeffrinjacob02@gmail.com | +447799184091 | linkedin.com/in/jeffrin-jacob-b90820193

Write only the cover letter, no preamble or explanation."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
