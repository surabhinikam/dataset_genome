"use client";

/**
 * components/dataset-metadata.tsx — Display panel for CSV analysis results.
 *
 * Shows key metrics (rows, columns, dataset ID) and the full column list
 * in a clean card layout with animated entrance.
 */

import type { DatasetMetadata } from "@/types/dataset";

interface DatasetMetadataProps {
  data: DatasetMetadata;
}

export default function DatasetMetadataPanel({ data }: DatasetMetadataProps) {
  const stats = [
    {
      label: "Rows",
      value: data.num_rows.toLocaleString(),
      icon: (
        <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75.125v-1.875c0-.621.504-1.125 1.125-1.125M3.375 14.25v-1.875c0-.621.504-1.125 1.125-1.125M3.375 14.25h1.5c.621 0 1.125.504 1.125 1.125m0-2.25v-1.875c0-.621.504-1.125 1.125-1.125M6 11.25h.008v.008H6v-.008zm0 0H3.375M6 11.25v-.375" />
        </svg>
      ),
      gradient: "from-violet-500/20 to-violet-600/10",
      textColor: "text-violet-300",
      borderColor: "border-violet-500/20",
    },
    {
      label: "Columns",
      value: data.num_cols.toLocaleString(),
      icon: (
        <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M9 4.5v15m6-15v15m-10.875 0h15.75c.621 0 1.125-.504 1.125-1.125V5.625c0-.621-.504-1.125-1.125-1.125H4.125C3.504 4.5 3 5.004 3 5.625v12.75c0 .621.504 1.125 1.125 1.125z" />
        </svg>
      ),
      gradient: "from-indigo-500/20 to-indigo-600/10",
      textColor: "text-indigo-300",
      borderColor: "border-indigo-500/20",
    },
    {
      label: "Dataset ID",
      value: data.dataset_id.split("-")[0] + "…",
      fullValue: data.dataset_id,
      icon: (
        <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M9.568 3H5.25A2.25 2.25 0 003 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 005.223-5.223c.542-.827.369-1.908-.33-2.607L9.568 3z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 6h.008v.008H6V6z" />
        </svg>
      ),
      gradient: "from-sky-500/20 to-sky-600/10",
      textColor: "text-sky-300",
      borderColor: "border-sky-500/20",
    },
  ];

  return (
    <div className="animate-slide-up space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        <div className="flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
          <span className="text-xs font-medium text-emerald-300">Analysis Complete</span>
        </div>
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      </div>

      {/* Filename */}
      <div className="rounded-2xl border border-white/8 bg-white/[0.03] px-5 py-4">
        <p className="text-xs font-medium uppercase tracking-widest text-white/30">Filename</p>
        <p className="mt-1 font-semibold text-white">{data.filename}</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-3 gap-3">
        {stats.map((stat) => (
          <div
            key={stat.label}
            title={stat.fullValue}
            className={`rounded-2xl border bg-gradient-to-br ${stat.gradient} ${stat.borderColor} p-4 transition-all duration-200 hover:scale-[1.02]`}
          >
            <div className={`mb-2 ${stat.textColor}`}>{stat.icon}</div>
            <p className={`text-xl font-bold ${stat.textColor}`}>{stat.value}</p>
            <p className="mt-0.5 text-xs text-white/40">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Column names */}
      <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-5">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white/80">Column Names</h3>
          <span className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs text-white/40">
            {data.column_names.length} columns
          </span>
        </div>
        <div className="flex flex-wrap gap-2">
          {data.column_names.map((col, index) => (
            <span
              key={col}
              className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-white/70 transition-colors hover:border-violet-500/30 hover:bg-violet-500/10 hover:text-violet-300"
            >
              <span className="text-xs font-mono text-white/25">{index}</span>
              {col}
            </span>
          ))}
        </div>
      </div>

      {/* Full UUID */}
      <div className="rounded-xl border border-white/5 bg-white/[0.02] px-4 py-3">
        <p className="mb-1 text-xs font-medium uppercase tracking-widest text-white/20">Full Dataset ID</p>
        <code className="break-all font-mono text-xs text-white/40">{data.dataset_id}</code>
      </div>
    </div>
  );
}
