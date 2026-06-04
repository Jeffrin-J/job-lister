"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { getJob, generateCoverLetter, Job } from "@/lib/api";

const visaLabel = (visa: Job["visa_sponsorship"]) => {
  if (visa === "yes") return { text: "Visa Sponsored ✓", cls: "bg-blue-100 text-blue-700" };
  if (visa === "no") return { text: "No Visa Sponsorship", cls: "bg-red-100 text-red-600" };
  return { text: "Visa Status Unknown", cls: "bg-slate-100 text-slate-500" };
};

const regionLabel = (region: string) => {
  const map: Record<string, string> = { europe: "🇪🇺 Europe", uae: "🇦🇪 UAE", india: "🇮🇳 India", remote: "🌐 Remote" };
  return map[region] || region;
};

export default function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [job, setJob] = useState<Job | null>(null);
  const [coverLetter, setCoverLetter] = useState<string>("");
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    getJob(id).then((j) => {
      setJob(j);
      if (j.cover_letter) setCoverLetter(j.cover_letter);
    });
  }, [id]);

  const handleGenerate = async () => {
    setGenerating(true);
    setGenError(null);
    try {
      const cl = await generateCoverLetter(id);
      setCoverLetter(cl);
      if (job) setJob({ ...job, cover_letter: cl });
    } catch (e: unknown) {
      setGenError(e instanceof Error ? e.message : "Failed to generate");
    } finally {
      setGenerating(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(coverLetter);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!job) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-400 animate-pulse text-sm">Loading job…</div>
      </div>
    );
  }

  const visa = visaLabel(job.visa_sponsorship);

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 flex items-center gap-3">
          <Link href="/" className="text-slate-400 hover:text-slate-700 transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </Link>
          <div>
            <h1 className="text-sm font-semibold text-slate-900 leading-tight">{job.title}</h1>
            <p className="text-xs text-slate-400">{job.company}</p>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Left: Job details */}
        <div className="lg:col-span-3 space-y-5">
          {/* Job header card */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <h2 className="text-xl font-bold text-slate-900">{job.title}</h2>
                <p className="text-slate-600 mt-1">{job.company}</p>
              </div>
              <span className="shrink-0 text-lg font-bold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-lg">
                {job.relevance_score}%
              </span>
            </div>

            <div className="flex flex-wrap gap-2 mb-4">
              <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${visa.cls}`}>{visa.text}</span>
              <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 text-slate-600">{regionLabel(job.region)}</span>
              {job.location && (
                <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 text-slate-600">📍 {job.location}</span>
              )}
              {job.salary && (
                <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 font-medium">{job.salary}</span>
              )}
              <span className="text-xs px-2.5 py-1 rounded-full bg-slate-50 text-slate-400">{job.source}</span>
            </div>

            {job.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {job.tags.map((tag) => (
                  <span key={tag} className="text-xs px-2 py-0.5 bg-slate-50 border border-slate-200 text-slate-500 rounded">
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {job.apply_url && (
              <a
                href={job.apply_url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-5 flex items-center justify-center gap-2 w-full py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Apply Now
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            )}
          </div>

          {/* Description */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-sm font-semibold text-slate-700 mb-3">Job Description</h3>
            <div
              className="text-sm text-slate-600 leading-relaxed prose prose-sm max-w-none prose-headings:text-slate-800 prose-a:text-indigo-600"
              dangerouslySetInnerHTML={{ __html: job.description || "<p>No description available.</p>" }}
            />
          </div>
        </div>

        {/* Right: Cover letter */}
        <div className="lg:col-span-2">
          <div className="bg-white border border-slate-200 rounded-xl p-5 sticky top-20">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-slate-700">Cover Letter</h3>
              {coverLetter && (
                <button
                  onClick={handleCopy}
                  className="text-xs text-slate-400 hover:text-slate-700 flex items-center gap-1 transition-colors"
                >
                  {copied ? "Copied!" : (
                    <>
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      Copy
                    </>
                  )}
                </button>
              )}
            </div>

            {coverLetter ? (
              <textarea
                value={coverLetter}
                onChange={(e) => setCoverLetter(e.target.value)}
                className="w-full text-xs text-slate-700 leading-relaxed border border-slate-200 rounded-lg p-3 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-300 font-mono"
                rows={28}
              />
            ) : (
              <div className="text-center py-10 text-slate-400">
                <svg className="w-10 h-10 mx-auto mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-xs mb-4">No cover letter yet.<br />Click below to generate one tailored to this job.</p>
              </div>
            )}

            {genError && (
              <p className="text-xs text-red-500 mt-2">{genError}</p>
            )}

            <button
              onClick={handleGenerate}
              disabled={generating}
              className="mt-3 w-full flex items-center justify-center gap-2 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
            >
              {generating ? (
                <>
                  <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Generating…
                </>
              ) : coverLetter ? "Regenerate Cover Letter" : "Generate Cover Letter"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
