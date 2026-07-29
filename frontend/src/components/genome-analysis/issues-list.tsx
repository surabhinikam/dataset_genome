"use client";

/**
 * components/genome-analysis/issues-list.tsx — Categorized Issues & Remediation List.
 *
 * Displays dataset issues with filter tabs by severity (All/Critical/Warning/Info)
 * and step-by-step fix recommendations.
 */

import { useState } from "react";
import type { DatasetIssue, IssueSeverity } from "@/types/intelligence";

interface IssuesListProps {
  issues: DatasetIssue[];
}

export default function IssuesList({ issues }: IssuesListProps) {
  const [filter, setFilter] = useState<"all" | IssueSeverity>("all");

  const filteredIssues = issues.filter(
    (issue) => filter === "all" || issue.severity === filter
  );

  const severityBadge = (severity: IssueSeverity) => {
    switch (severity) {
      case "critical":
        return "bg-red-500/10 text-red-300 border-red-500/30";
      case "warning":
        return "bg-amber-500/10 text-amber-300 border-amber-500/30";
      case "info":
        return "bg-sky-500/10 text-sky-300 border-sky-500/30";
    }
  };

  const criticalCount = issues.filter((i) => i.severity === "critical").length;
  const warningCount = issues.filter((i) => i.severity === "warning").length;
  const infoCount = issues.filter((i) => i.severity === "info").length;

  return (
    <div className="space-y-4">
      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-base font-semibold text-white">Detected Issues &amp; Remediation</h3>
          <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-0.5 text-xs font-mono text-white/50">
            {issues.length} total
          </span>
        </div>

        <div className="flex rounded-xl border border-white/10 bg-white/[0.03] p-1">
          {[
            { id: "all", label: "All", count: issues.length },
            { id: "critical", label: "Critical", count: criticalCount, color: "text-red-400" },
            { id: "warning", label: "Warning", count: warningCount, color: "text-amber-400" },
            { id: "info", label: "Info", count: infoCount, color: "text-sky-400" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilter(tab.id as any)}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-medium transition-all ${
                filter === tab.id
                  ? "bg-white/10 text-white shadow-sm"
                  : "text-white/40 hover:text-white/70"
              }`}
            >
              <span>{tab.label}</span>
              <span className={`text-[10px] font-mono ${tab.color || "text-white/40"}`}>
                ({tab.count})
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Issues Cards */}
      {filteredIssues.length === 0 ? (
        <div className="flex h-40 flex-col items-center justify-center rounded-2xl border border-white/5 bg-white/[0.02] text-center">
          <svg className="mb-2 h-8 w-8 text-emerald-400/60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm font-medium text-white/60">No issues found in this category!</p>
          <p className="text-xs text-white/30">Your dataset passes all checks for this severity filter.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredIssues.map((issue) => (
            <div
              key={issue.id}
              className="group rounded-2xl border border-white/8 bg-white/[0.02] p-4 backdrop-blur-md transition-all hover:border-white/15 hover:bg-white/[0.04]"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span className={`rounded-md border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${severityBadge(issue.severity)}`}>
                    {issue.severity}
                  </span>
                  <h4 className="text-sm font-semibold text-white">{issue.title}</h4>
                </div>

                {issue.column_name && (
                  <span className="rounded-md border border-violet-500/30 bg-violet-500/10 px-2 py-0.5 text-[10px] font-mono text-violet-300">
                    {issue.column_name}
                  </span>
                )}
              </div>

              <p className="mt-2 text-xs leading-relaxed text-white/60">{issue.description}</p>

              {/* Actionable recommendation */}
              <div className="mt-3 flex items-start gap-2 rounded-xl border border-indigo-500/20 bg-indigo-500/10 p-2.5">
                <svg className="mt-0.5 h-4 w-4 shrink-0 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.516 0c.85.493 1.508 1.333 1.508 2.316V18" />
                </svg>
                <div className="text-xs">
                  <span className="font-semibold text-indigo-300">Remediation: </span>
                  <span className="text-indigo-200/80">{issue.recommendation}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
