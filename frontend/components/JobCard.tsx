"use client";

import Link from "next/link";
import { Job } from "@/lib/api";

const scoreColor = (score: number) => {
  if (score >= 70) return "bg-emerald-100 text-emerald-800";
  if (score >= 40) return "bg-amber-100 text-amber-800";
  return "bg-slate-100 text-slate-600";
};

const visaBadge = (visa: Job["visa_sponsorship"]) => {
  if (visa === "yes") return <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 font-medium">Visa ✓</span>;
  if (visa === "no") return <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-600 font-medium">No Visa</span>;
  return <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">Visa ?</span>;
};

export default function JobCard({ job }: { job: Job }) {
  const displayTags = job.tags.slice(0, 5);

  return (
    <Link href={`/jobs/${job.id}`} className="block group">
      <div className="bg-white border border-slate-200 rounded-xl p-5 hover:border-indigo-300 hover:shadow-md transition-all duration-200 cursor-pointer">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-slate-900 group-hover:text-indigo-700 truncate text-sm leading-snug">
              {job.title}
            </h3>
            <p className="text-slate-500 text-xs mt-0.5 truncate">{job.company}</p>
          </div>
          <span className={`text-xs font-bold px-2 py-1 rounded-lg shrink-0 ${scoreColor(job.relevance_score)}`}>
            {job.relevance_score}%
          </span>
        </div>

        <div className="flex items-center gap-2 mt-2 flex-wrap">
          {visaBadge(job.visa_sponsorship)}
          {job.location && (
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {job.location}
            </span>
          )}
          {job.salary && (
            <span className="text-xs text-emerald-600 font-medium">{job.salary}</span>
          )}
        </div>

        {displayTags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-3">
            {displayTags.map((tag) => (
              <span key={tag} className="text-xs px-1.5 py-0.5 bg-slate-50 border border-slate-200 text-slate-500 rounded">
                {tag}
              </span>
            ))}
            {job.tags.length > 5 && (
              <span className="text-xs text-slate-400">+{job.tags.length - 5}</span>
            )}
          </div>
        )}

        <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100">
          <span className="text-xs text-slate-400">{job.source}</span>
          {job.cover_letter && (
            <span className="text-xs text-indigo-500 font-medium">Cover letter ready ✓</span>
          )}
        </div>
      </div>
    </Link>
  );
}
