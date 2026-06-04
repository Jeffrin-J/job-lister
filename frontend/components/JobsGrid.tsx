"use client";

import { useEffect, useState, useCallback } from "react";
import { fetchJobs, Job } from "@/lib/api";
import JobCard from "./JobCard";

type Tab = "europe-visa" | "europe-no-visa" | "uae" | "india" | "remote";

const TABS: { id: Tab; label: string; emoji: string }[] = [
  { id: "europe-visa", label: "Europe — Visa Sponsored", emoji: "🇪🇺" },
  { id: "europe-no-visa", label: "Europe — No Visa Info", emoji: "🌍" },
  { id: "uae", label: "UAE", emoji: "🇦🇪" },
  { id: "india", label: "India", emoji: "🇮🇳" },
  { id: "remote", label: "Remote / Global", emoji: "🌐" },
];

export default function JobsGrid({ refreshKey }: { refreshKey: number }) {
  const [activeTab, setActiveTab] = useState<Tab>("europe-visa");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [counts, setCounts] = useState<Record<Tab, number>>({
    "europe-visa": 0,
    "europe-no-visa": 0,
    uae: 0,
    india: 0,
    remote: 0,
  });

  const loadJobs = useCallback(async () => {
    setLoading(true);
    try {
      // Load all jobs once and split into buckets for counts
      const all = await fetchJobs();
      const buckets: Record<Tab, Job[]> = {
        "europe-visa": all.filter((j) => j.region === "europe" && j.visa_sponsorship === "yes"),
        "europe-no-visa": all.filter((j) => j.region === "europe" && j.visa_sponsorship !== "yes"),
        uae: all.filter((j) => j.region === "uae"),
        india: all.filter((j) => j.region === "india"),
        remote: all.filter((j) => j.region === "remote"),
      };
      setCounts({
        "europe-visa": buckets["europe-visa"].length,
        "europe-no-visa": buckets["europe-no-visa"].length,
        uae: buckets.uae.length,
        india: buckets.india.length,
        remote: buckets.remote.length,
      });
      setJobs(buckets[activeTab]);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [activeTab, refreshKey]);

  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  return (
    <div>
      {/* Tab bar */}
      <div className="flex gap-1 border-b border-slate-200 mb-6 overflow-x-auto pb-px">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-1.5 px-3 py-2.5 text-sm font-medium whitespace-nowrap rounded-t-lg transition-colors border-b-2 ${
              activeTab === tab.id
                ? "border-indigo-600 text-indigo-700 bg-indigo-50"
                : "border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-50"
            }`}
          >
            <span>{tab.emoji}</span>
            <span>{tab.label}</span>
            {counts[tab.id] > 0 && (
              <span className={`text-xs px-1.5 py-0.5 rounded-full font-semibold ${
                activeTab === tab.id ? "bg-indigo-100 text-indigo-700" : "bg-slate-100 text-slate-500"
              }`}>
                {counts[tab.id]}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Jobs grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white border border-slate-200 rounded-xl p-5 animate-pulse">
              <div className="h-4 bg-slate-200 rounded w-3/4 mb-2" />
              <div className="h-3 bg-slate-100 rounded w-1/2 mb-4" />
              <div className="h-3 bg-slate-100 rounded w-full" />
            </div>
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <svg className="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <p className="text-sm">No jobs yet — click "Fetch Latest Jobs" to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}
    </div>
  );
}
