const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string | null;
  description: string | null;
  apply_url: string | null;
  source: string | null;
  region: "europe" | "uae" | "india" | "remote";
  visa_sponsorship: "yes" | "no" | "unknown";
  relevance_score: number;
  tags: string[];
  salary: string | null;
  fetched_at: string | null;
  cover_letter: string | null;
}

export interface Stats {
  total: number;
  breakdown: { region: string; visa_sponsorship: string; count: number }[];
}

export async function fetchJobs(region?: string, visa?: string): Promise<Job[]> {
  const params = new URLSearchParams();
  if (region) params.set("region", region);
  if (visa) params.set("visa", visa);
  const url = `${API_BASE}/api/jobs${params.size ? "?" + params : ""}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return res.json();
}

export async function getJob(id: string): Promise<Job> {
  const res = await fetch(`${API_BASE}/api/jobs/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Job not found");
  return res.json();
}

export async function triggerFetch(): Promise<{ fetched: number; saved: number }> {
  const res = await fetch(`${API_BASE}/api/fetch`, { method: "POST" });
  if (!res.ok) throw new Error("Fetch failed");
  return res.json();
}

export async function generateCoverLetter(jobId: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/jobs/${jobId}/cover-letter`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to generate cover letter");
  }
  const data = await res.json();
  return data.cover_letter;
}

export async function getStats(): Promise<Stats> {
  const res = await fetch(`${API_BASE}/api/stats`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to get stats");
  return res.json();
}
