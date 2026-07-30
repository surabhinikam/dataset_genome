/**
 * ReportsView.tsx — Reports Download & Export Hub View.
 */

"use client";

import React from "react";
import { FileText, Download, FileCode, CheckCircle2 } from "lucide-react";

export const ReportsView: React.FC = () => {
  const reports = [
    {
      id: "rep-01",
      title: "Autonomous Platform Run Report",
      category: "Execution Report",
      generated: "2026-07-29 20:31 UTC",
      summary: "Full end-to-end 7-stage execution report containing stage timing, health scores, and generated artifact manifests.",
      jsonFile: "run_report.json",
      mdFile: "run_report.md",
    },
    {
      id: "rep-02",
      title: "Open Source Publication Report",
      category: "Publication Engine",
      generated: "2026-07-29 20:25 UTC",
      summary: "Publication readiness report for Hugging Face Hub, Kaggle Datasets, and GitHub release CHANGELOG.",
      jsonFile: "publication_report.json",
      mdFile: "publication_report.md",
    },
    {
      id: "rep-03",
      title: "AutoScientist Benchmark Training Report",
      category: "Model Training",
      generated: "2026-07-29 20:15 UTC",
      summary: "Hypothesis evaluation accuracy scores, loss curves, and reasoning trace benchmark results.",
      jsonFile: "evaluation.json",
      mdFile: "training_summary.md",
    },
    {
      id: "rep-04",
      title: "Dataset Intelligence Profiling Report",
      category: "Dataset Intelligence",
      generated: "2026-07-29 20:05 UTC",
      summary: "Comprehensive dataset completeness, noise level, feature quality, and correlation metrics.",
      jsonFile: "intel_report.json",
      mdFile: "intel_report.md",
    },
  ];

  const handleDownload = (filename: string) => {
    const element = document.createElement("a");
    const file = new Blob([`# Sample Download: ${filename}\nGenerated automatically by Dataset Genome AI Platform.`], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
  };

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <FileText className="w-5 h-5 text-[#3B82F6]" />
          Platform Reports & Exporters Hub
        </h1>
        <p className="text-xs text-gray-400">
          Download structured JSON payloads and formatted GitHub-Flavored Markdown reports for all platform runs.
        </p>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reports.map((rep) => (
          <div
            key={rep.id}
            className="bg-[#111827] border border-[#1F2937] hover:border-gray-700 rounded-xl p-6 space-y-4 transition-all"
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  {rep.category}
                </span>
                <h3 className="font-bold text-base text-white mt-2">{rep.title}</h3>
                <span className="text-[11px] text-gray-400 font-mono">Generated: {rep.generated}</span>
              </div>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>

            <p className="text-xs text-gray-300 leading-relaxed bg-[#0B1220] p-3 rounded-lg border border-[#1F2937]">
              {rep.summary}
            </p>

            <div className="pt-2 border-t border-[#1F2937] flex items-center justify-between">
              <span className="text-[11px] text-gray-400 font-mono">Available Formats:</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleDownload(rep.mdFile)}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0B1220] hover:bg-gray-800 text-xs text-gray-200 font-mono rounded border border-gray-700 transition-colors"
                >
                  <FileText className="w-3.5 h-3.5 text-blue-400" />
                  <span>{rep.mdFile}</span>
                </button>
                <button
                  onClick={() => handleDownload(rep.jsonFile)}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0B1220] hover:bg-gray-800 text-xs text-gray-200 font-mono rounded border border-gray-700 transition-colors"
                >
                  <FileCode className="w-3.5 h-3.5 text-emerald-400" />
                  <span>{rep.jsonFile}</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
