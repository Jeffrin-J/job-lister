"use client";

import { useState } from "react";
import FetchButton from "@/components/FetchButton";
import JobsGrid from "@/components/JobsGrid";

export default function HomePage() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-lg font-bold text-slate-900 leading-tight">Job Lister</h1>
            <p className="text-xs text-slate-400">AI-powered · Jeffrin Jacob</p>
          </div>
          <FetchButton onDone={() => setRefreshKey((k) => k + 1)} />
        </div>
      </header>

      {/* Main */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {/* Info banner */}
        <div className="mb-6 grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
            <p className="text-xs font-semibold text-blue-600 uppercase tracking-wide mb-1">Europe</p>
            <p className="text-xs text-blue-500">Jobs split by visa sponsorship status. Requires sponsorship.</p>
          </div>
          <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
            <p className="text-xs font-semibold text-amber-600 uppercase tracking-wide mb-1">UAE</p>
            <p className="text-xs text-amber-500">Dubai, Abu Dhabi & UAE-based opportunities.</p>
          </div>
          <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-4">
            <p className="text-xs font-semibold text-emerald-600 uppercase tracking-wide mb-1">India</p>
            <p className="text-xs text-emerald-500">Indian citizen — no visa required. Open access.</p>
          </div>
        </div>

        <JobsGrid refreshKey={refreshKey} />
      </main>
    </div>
  );
}
