"use client";

/**
 * components/genome-analysis/stitch-dashboard.tsx — Google Stitch Genome Analysis Screen.
 *
 * Full Google Stitch-inspired dashboard displaying live Dataset Intelligence Engine output:
 * Overall Health Score, 6 Profiler Metric Cards, Categorized Issues & Remediation,
 * Pearson Correlation Heatmap, Column Outliers/Missingness charts, and disabled Sprint 3 button.
 */

import { useState } from "react";
import type { GenomeReport } from "@/types/intelligence";
import HealthScoreGauge from "./health-score-gauge";
import MetricCard from "./metric-card";
import IssuesList from "./issues-list";
import CorrelationHeatmap from "./correlation-heatmap";
import ColumnAnalytics from "./column-analytics";
import RawJsonViewer from "./raw-json-viewer";

interface StitchDashboardProps {
  report: GenomeReport;
  onReAnalyze?: () => void;
  isAnalyzing?: boolean;
}

export default function StitchDashboard({
  report,
  onReAnalyze,
  isAnalyzing = false,
}: StitchDashboardProps) {
  const [activeTab, setActiveTab] = useState<"issues" | "heatmap" | "analytics" | "json">("issues");

  const {
    health_score,
    completeness,
    consistency,
    balance,
    noise,
    correlation,
    feature_quality,
    issues,
  } = report;

  return (
    <div className="animate-fade-in space-y-8">
      {/* Top Banner & Control Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-3xl border border-white/10 bg-white/[0.03] p-6 backdrop-blur-xl">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500 to-indigo-600 shadow-lg shadow-violet-500/20">
            <svg className="h-6 w-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-white">{report.filename}</h2>
              <span className="rounded-full border border-violet-500/30 bg-violet-500/10 px-2.5 py-0.5 text-[10px] font-semibold text-violet-300">
                Genome Analyzed
              </span>
            </div>
            <p className="mt-0.5 text-xs text-white/40">
              ID: <code className="font-mono text-white/60">{report.dataset_id}</code> · {report.num_rows.toLocaleString()} rows · {report.num_cols} columns
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          {onReAnalyze && (
            <button
              onClick={onReAnalyze}
              disabled={isAnalyzing}
              className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-xs font-semibold text-white/80 transition-all hover:bg-white/10 hover:text-white"
            >
              <svg className={`h-4 w-4 text-violet-400 ${isAnalyzing ? "animate-spin" : ""}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
              <span>{isAnalyzing ? "Re-Analyzing..." : "Re-Analyze"}</span>
            </button>
          )}

          {/* Disabled Button until Sprint 3 */}
          <div className="relative group">
            <button
              disabled
              className="flex cursor-not-allowed items-center gap-2 rounded-xl border border-white/5 bg-white/5 px-5 py-2.5 text-xs font-semibold text-white/30"
            >
              <svg className="h-4 w-4 text-white/30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
              </svg>
              <span>Continue to AI Scientist</span>
              <span className="rounded-full bg-violet-500/20 px-2 py-0.5 text-[9px] font-bold text-violet-400">Sprint 3</span>
            </button>
            {/* Tooltip */}
            <div className="absolute right-0 top-full mt-2 hidden w-56 rounded-xl border border-white/10 bg-[#0d0d1a] p-2.5 text-[11px] text-white/60 shadow-2xl group-hover:block z-50">
              🔒 AI Experiment Generation & Reasoning engine will be unlocked in Sprint 3.
            </div>
          </div>
        </div>
      </div>

      {/* Hero: Health Score Gauge */}
      <HealthScoreGauge healthScore={health_score} />

      {/* 6 Profiler Metric Cards Grid */}
      <div>
        <h3 className="mb-4 text-xs font-bold uppercase tracking-wider text-white/40">
          Dataset Intelligence Profilers
        </h3>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {/* 1. Completeness */}
          <MetricCard
            title="Completeness"
            score={completeness.score}
            subtitle={`${(completeness.missing_cell_ratio * 100).toFixed(1)}% missing cells`}
            accentColor="bg-emerald-500/10 text-emerald-400"
            details={[
              `${completeness.missing_cells.toLocaleString()} missing cells`,
              `${(completeness.complete_row_ratio * 100).toFixed(1)}% complete rows`,
            ]}
            icon={
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          />

          {/* 2. Consistency */}
          <MetricCard
            title="Consistency"
            score={consistency.score}
            subtitle={`${consistency.duplicate_rows} duplicate rows`}
            accentColor="bg-indigo-500/10 text-indigo-400"
            details={[
              `${(consistency.duplicate_ratio * 100).toFixed(1)}% duplicate ratio`,
              `${consistency.mixed_type_columns.length} mixed-type column(s)`,
            ]}
            icon={
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
            }
          />

          {/* 3. Balance */}
          <MetricCard
            title="Balance"
            score={balance.score}
            subtitle={`${balance.imbalanced_columns.length} imbalanced feature(s)`}
            accentColor="bg-violet-500/10 text-violet-400"
            details={[
              `Shannon Entropy evaluated across categories`,
              balance.imbalanced_columns.length > 0
                ? `Imbalanced: ${balance.imbalanced_columns.join(", ")}`
                : `Balanced categorical distribution`,
            ]}
            icon={
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
              </svg>
            }
          />

          {/* 4. Noise (IQR Method) */}
          <MetricCard
            title="Noise (IQR Method)"
            score={noise.score}
            subtitle={`${noise.total_outliers} statistical outliers`}
            accentColor="bg-amber-500/10 text-amber-400"
            details={[
              `IQR bounds: [Q1 - 1.5*IQR, Q3 + 1.5*IQR]`,
              `${(noise.outlier_ratio * 100).toFixed(1)}% overall outlier ratio`,
            ]}
            icon={
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
            }
          />

          {/* 5. Correlation (Pearson) */}
          <MetricCard
            title="Correlation (Pearson)"
            score={correlation.score}
            subtitle={`${correlation.high_correlation_pairs.length} collinear pair(s)`}
            accentColor="bg-sky-500/10 text-sky-400"
            details={[
              `${correlation.numeric_columns.length} numeric columns evaluated`,
              correlation.high_correlation_pairs.length > 0
                ? `Collinear: ${correlation.high_correlation_pairs.map((p) => `${p.column_1}-${p.column_2}`).join(", ")}`
                : `No severe multicollinearity (|r| < 0.85)`,
            ]}
            icon={
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 14.25m-2.25 0a2.25 2.25 0 104.5 0a2.25 2.25 0 10-4.5 0zm10.5-6m-2.25 0a2.25 2.25 0 104.5 0a2.25 2.25 0 10-4.5 0zM6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
              </svg>
            }
          />

          {/* 6. Feature Quality */}
          <MetricCard
            title="Feature Quality"
            score={feature_quality.score}
            subtitle={`${feature_quality.total_features} total features`}
            accentColor="bg-teal-500/10 text-teal-400"
            details={[
              `${feature_quality.constant_columns.length} zero-variance constant column(s)`,
              `${feature_quality.id_like_columns.length} ID-like unique string feature(s)`,
            ]}
            icon={
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
            }
          />
        </div>
      </div>

      {/* Main Tabbed Detail Section */}
      <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6 backdrop-blur-xl">
        {/* Navigation Tabs */}
        <div className="mb-6 flex border-b border-white/10">
          {[
            { id: "issues", label: `Issues & Remediation (${issues.length})` },
            { id: "heatmap", label: "Correlation Heatmap" },
            { id: "analytics", label: "Column Distributions" },
            { id: "json", label: "Raw Genome JSON" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`border-b-2 px-5 py-3 text-xs font-semibold transition-all ${
                activeTab === tab.id
                  ? "border-violet-400 text-white"
                  : "border-transparent text-white/40 hover:text-white/70"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content Panels */}
        {activeTab === "issues" && <IssuesList issues={issues} />}
        {activeTab === "heatmap" && <CorrelationHeatmap correlation={correlation} />}
        {activeTab === "analytics" && <ColumnAnalytics completeness={completeness} noise={noise} />}
        {activeTab === "json" && <RawJsonViewer report={report} />}
      </div>
    </div>
  );
}
