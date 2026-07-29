"use client";

/**
 * components/genome-analysis/column-analytics.tsx — Column Analytics & Distribution Charts.
 *
 * Shows IQR Outliers per column and Missing value proportions across features.
 */

import type { CompletenessMetrics, NoiseMetrics } from "@/types/intelligence";

interface ColumnAnalyticsProps {
  completeness: CompletenessMetrics;
  noise: NoiseMetrics;
}

export default function ColumnAnalytics({ completeness, noise }: ColumnAnalyticsProps) {
  const missingEntries = Object.entries(completeness.column_missing_rates);
  const outlierEntries = Object.entries(noise.column_outliers);

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* 1. Missing Value Distribution */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5 backdrop-blur-md">
        <h3 className="text-sm font-semibold text-white mb-1">Missing Value Rates per Column</h3>
        <p className="text-xs text-white/40 mb-4">Percentage of missing values per column</p>

        {missingEntries.length === 0 ? (
          <p className="text-xs text-white/30">No missing data found.</p>
        ) : (
          <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
            {missingEntries.map(([col, rate]) => {
              const pct = (rate * 100).toFixed(1);
              return (
                <div key={col} className="space-y-1">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-white/80 truncate">{col}</span>
                    <span className={rate > 0.4 ? "text-red-400 font-bold" : rate > 0.1 ? "text-amber-400 font-bold" : "text-emerald-400"}>
                      {pct}% ({rate === 0 ? "Clean" : "Missing"})
                    </span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-white/5 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        rate > 0.4 ? "bg-red-500" : rate > 0.1 ? "bg-amber-500" : "bg-emerald-500"
                      }`}
                      style={{ width: `${Math.max(rate * 100, 2)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 2. IQR Outliers per Column */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5 backdrop-blur-md">
        <h3 className="text-sm font-semibold text-white mb-1">IQR Outlier Breakdown</h3>
        <p className="text-xs text-white/40 mb-4">Statistical outliers detected outside [Q1-1.5*IQR, Q3+1.5*IQR]</p>

        {outlierEntries.length === 0 ? (
          <p className="text-xs text-white/30">No numeric columns with outliers detected.</p>
        ) : (
          <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
            {outlierEntries.map(([col, detail]) => {
              const pct = (detail.outlier_ratio * 100).toFixed(1);
              return (
                <div key={col} className="rounded-xl border border-white/5 bg-white/[0.02] p-3 text-xs">
                  <div className="flex items-center justify-between font-mono mb-1">
                    <span className="font-semibold text-violet-300 truncate">{col}</span>
                    <span className={`font-bold ${detail.outlier_count > 0 ? "text-amber-400" : "text-emerald-400"}`}>
                      {detail.outlier_count} outliers ({pct}%)
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-white/40 font-mono mt-1 pt-1 border-t border-white/5">
                    <span>Q1: {detail.q1}</span>
                    <span>Q3: {detail.q3}</span>
                    <span>IQR: {detail.iqr}</span>
                    <span>Bounds: [{detail.lower_bound}, {detail.upper_bound}]</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
