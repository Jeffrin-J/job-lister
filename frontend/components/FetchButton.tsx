"use client";

import { useState } from "react";
import { triggerFetch } from "@/lib/api";

export default function FetchButton({ onDone }: { onDone: () => void }) {
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [result, setResult] = useState<{ fetched: number; saved: number } | null>(null);

  const handleFetch = async () => {
    setStatus("loading");
    setResult(null);
    try {
      const data = await triggerFetch();
      setResult(data);
      setStatus("done");
      onDone();
      setTimeout(() => setStatus("idle"), 5000);
    } catch {
      setStatus("error");
      setTimeout(() => setStatus("idle"), 4000);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={handleFetch}
        disabled={status === "loading"}
        className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
      >
        {status === "loading" ? (
          <>
            <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            Fetching…
          </>
        ) : (
          <>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Fetch Latest Jobs
          </>
        )}
      </button>

      {status === "done" && result && (
        <span className="text-sm text-emerald-600 font-medium">
          ✓ {result.saved} jobs saved ({result.fetched} fetched)
        </span>
      )}
      {status === "error" && (
        <span className="text-sm text-red-500">Failed — check backend is running</span>
      )}
    </div>
  );
}
