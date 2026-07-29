/**
 * app/page.tsx — Dataset Genome Dashboard homepage.
 *
 * Integrates Sprint 1 CSV Upload with Sprint 2 Google Stitch Genome Analysis Screen.
 */

"use client";

import { useState } from "react";
import Header from "@/components/header";
import CsvUpload from "@/components/csv-upload";
import DatasetMetadataPanel from "@/components/dataset-metadata";
import StitchDashboard from "@/components/genome-analysis/stitch-dashboard";
import { analyzeDataset } from "@/lib/api";
import type { DatasetMetadata } from "@/types/dataset";
import type { GenomeReport } from "@/types/intelligence";

export default function HomePage() {
  const [metadata, setMetadata] = useState<DatasetMetadata | null>(null);
  const [genomeReport, setGenomeReport] = useState<GenomeReport | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);

  const runAnalysis = async (datasetId: string) => {
    setIsAnalyzing(true);
    setAnalyzeError(null);

    try {
      const report = await analyzeDataset(datasetId);
      setGenomeReport(report);
    } catch (err) {
      setAnalyzeError(
        err instanceof Error ? err.message : "Failed to run Dataset Intelligence Engine."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUploadSuccess = (data: DatasetMetadata) => {
    setMetadata(data);
    runAnalysis(data.dataset_id);
  };

  const handleReset = () => {
    setMetadata(null);
    setGenomeReport(null);
    setAnalyzeError(null);
  };

  return (
    <div className="animated-bg min-h-screen">
      <Header />

      <main className="mx-auto max-w-6xl px-6 py-12">
        {/* ---- Hero (Shown when no Genome Report exists yet) ---- */}
        {!genomeReport && !isAnalyzing && (
          <section className="mb-12 animate-slide-up text-center">
            {/* Eyebrow badge */}
            <div className="mb-6 flex justify-center">
              <span className="inline-flex items-center gap-2 rounded-full border border-violet-500/20 bg-violet-500/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-violet-400">
                <span className="h-1.5 w-1.5 rounded-full bg-violet-400 animate-pulse" />
                Sprint 2 — Dataset Intelligence Engine
              </span>
            </div>

            <h1 className="mb-4 bg-gradient-to-b from-white via-white/90 to-white/50 bg-clip-text text-4xl font-extrabold leading-tight tracking-tight text-transparent sm:text-5xl lg:text-6xl">
              Dataset{" "}
              <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
                Genome
              </span>
            </h1>

            <p className="mx-auto max-w-xl text-base text-white/50 sm:text-lg">
              Upload a CSV dataset to run 6 automated intelligence profilers and generate your complete Dataset Genome.
            </p>

            {/* Decorative divider */}
            <div className="mx-auto mt-8 flex max-w-xs items-center gap-4">
              <div className="h-px flex-1 bg-gradient-to-r from-transparent to-white/10" />
              <div className="h-1 w-1 rounded-full bg-white/20" />
              <div className="h-1.5 w-1.5 rounded-full bg-violet-400/60" />
              <div className="h-1 w-1 rounded-full bg-white/20" />
              <div className="h-px flex-1 bg-gradient-to-l from-transparent to-white/10" />
            </div>
          </section>
        )}

        {/* ---- State 1: Loading / Analyzing ---- */}
        {isAnalyzing && (
          <div className="my-16 flex flex-col items-center justify-center text-center space-y-6 animate-fade-in">
            <div className="relative flex h-24 w-24 items-center justify-center">
              <div className="absolute inset-0 rounded-full border-4 border-violet-500/20" />
              <div className="absolute inset-0 rounded-full border-4 border-violet-500 border-t-transparent animate-spin" />
              <svg className="h-8 w-8 text-violet-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Running Dataset Intelligence Engine</h2>
              <p className="mt-1 text-sm text-white/50">
                Executing 6 Profilers: Completeness, Consistency, Balance, Noise (IQR), Correlation &amp; Feature Quality...
              </p>
            </div>
            <div className="w-64 space-y-2 opacity-50">
              <div className="shimmer h-2 rounded-full" />
              <div className="shimmer h-2 rounded-full" style={{ width: "80%" }} />
            </div>
          </div>
        )}

        {/* ---- State 2: Analysis Error ---- */}
        {analyzeError && (
          <div className="my-8 rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-center space-y-4">
            <p className="text-sm font-semibold text-red-300">Analysis Error: {analyzeError}</p>
            <button
              onClick={() => metadata && runAnalysis(metadata.dataset_id)}
              className="rounded-xl border border-red-500/40 bg-red-500/20 px-4 py-2 text-xs font-semibold text-red-200 hover:bg-red-500/30"
            >
              Retry Intelligence Engine
            </button>
          </div>
        )}

        {/* ---- State 3: Live Google Stitch Dashboard ---- */}
        {genomeReport && !isAnalyzing && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <button
                onClick={handleReset}
                className="flex items-center gap-1.5 text-xs text-white/50 hover:text-white transition-colors"
              >
                ← Upload Different Dataset
              </button>
            </div>

            <StitchDashboard
              report={genomeReport}
              onReAnalyze={() => metadata && runAnalysis(metadata.dataset_id)}
              isAnalyzing={isAnalyzing}
            />
          </div>
        )}

        {/* ---- State 4: Default Upload & Initial Metadata Panel ---- */}
        {!genomeReport && !isAnalyzing && (
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Upload panel */}
            <div
              className="glass-card animate-slide-up rounded-3xl p-8"
              style={{ animationDelay: "0.1s", animationFillMode: "both" }}
            >
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-white">Upload Dataset</h2>
                <p className="mt-1 text-sm text-white/40">
                  Drag &amp; drop or browse to select a CSV file.
                </p>
              </div>
              <CsvUpload onSuccess={handleUploadSuccess} />

              {/* Feature hints */}
              <div className="mt-6 grid grid-cols-2 gap-3">
                {[
                  { icon: "⚡", text: "Instant 6-profiler run" },
                  { icon: "🔒", text: "IQR outlier detection" },
                  { icon: "📊", text: "Pearson correlation" },
                  { icon: "🔑", text: "Health Score (0-100)" },
                ].map((item) => (
                  <div
                    key={item.text}
                    className="flex items-center gap-2 rounded-xl border border-white/5 bg-white/[0.02] px-3 py-2.5"
                  >
                    <span className="text-base">{item.icon}</span>
                    <span className="text-xs text-white/40">{item.text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Results panel */}
            <div
              className="glass-card animate-slide-up rounded-3xl p-8"
              style={{ animationDelay: "0.2s", animationFillMode: "both" }}
            >
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-white">Analysis Results</h2>
                <p className="mt-1 text-sm text-white/40">
                  Dataset metadata &amp; Genome Report will appear here after upload.
                </p>
              </div>

              {metadata ? (
                <DatasetMetadataPanel data={metadata} />
              ) : (
                /* Empty state */
                <div className="flex h-64 flex-col items-center justify-center gap-4 text-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-white/8 bg-white/[0.03]">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      className="h-8 w-8 text-white/15"
                      stroke="currentColor"
                      strokeWidth={1}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white/25">No dataset analysed yet</p>
                    <p className="mt-1 text-xs text-white/15">
                      Upload a CSV file to execute the Dataset Intelligence Engine
                    </p>
                  </div>
                  {/* Shimmer skeleton preview */}
                  <div className="w-full space-y-2 opacity-30">
                    {[80, 60, 90, 50].map((w, i) => (
                      <div
                        key={i}
                        className="shimmer h-3 rounded-full"
                        style={{ width: `${w}%` }}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ---- Footer ---- */}
        <footer className="mt-16 border-t border-white/5 pt-8 text-center">
          <p className="text-xs text-white/20">
            Dataset Genome · Sprint 2 Dataset Intelligence Engine · Next.js 15 + FastAPI
          </p>
        </footer>
      </main>
    </div>
  );
}
