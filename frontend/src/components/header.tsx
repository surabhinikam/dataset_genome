"use client";

/**
 * components/header.tsx — Top navigation bar for Dataset Genome.
 *
 * Renders the brand logo/name and a status badge that pings the backend
 * health endpoint to show whether the API is reachable.
 */

import { useEffect, useState } from "react";
import { checkHealth } from "@/lib/api";

export default function Header() {
  const [apiStatus, setApiStatus] = useState<"checking" | "online" | "offline">(
    "checking"
  );

  useEffect(() => {
    checkHealth()
      .then(() => setApiStatus("online"))
      .catch(() => setApiStatus("offline"));
  }, []);

  const statusConfig = {
    checking: { label: "Connecting…", color: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30" },
    online: { label: "API Online", color: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" },
    offline: { label: "API Offline", color: "bg-red-500/20 text-red-300 border-red-500/30" },
  };

  const { label, color } = statusConfig[apiStatus];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-[#0a0a14]/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 shadow-lg shadow-violet-500/25">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              className="h-5 w-5 text-white"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18"
              />
            </svg>
          </div>
          <div>
            <span className="text-sm font-bold tracking-tight text-white">
              Dataset
            </span>
            <span className="text-sm font-bold tracking-tight text-violet-400">
              {" "}Genome
            </span>
          </div>
          <span className="hidden rounded-full border border-violet-500/30 bg-violet-500/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-widest text-violet-400 sm:inline-block">
            Sprint 2
          </span>
        </div>

        {/* API status badge */}
        <div
          className={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-all duration-500 ${color}`}
        >
          <span
            className={`inline-block h-1.5 w-1.5 rounded-full ${
              apiStatus === "online"
                ? "bg-emerald-400 animate-pulse"
                : apiStatus === "offline"
                ? "bg-red-400"
                : "bg-yellow-400 animate-pulse"
            }`}
          />
          {label}
        </div>
      </div>
    </header>
  );
}
