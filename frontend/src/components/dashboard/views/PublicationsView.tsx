/**
 * PublicationsView.tsx — Open Source Hub Publication Engine View.
 */

"use client";

import React, { useState } from "react";
import { Share2, ExternalLink, CheckCircle2, FileText, Copy, ShieldCheck } from "lucide-react";

export const PublicationsView: React.FC = () => {
  const [activeCardTab, setActiveCardTab] = useState<"hf" | "kaggle" | "github">("hf");

  const publications = [
    {
      platform: "Hugging Face Hub",
      type: "Dataset & Model Card",
      repo: "datasets/dataset-genome/scientific-reasoning-benchmark",
      status: "PUBLISHED & READY",
      url: "https://huggingface.co/datasets/dataset-genome/scientific-reasoning-benchmark",
      version: "v2.0-adaptive",
      releaseTag: "v2.0.0",
      readmeContent: `# Dataset Genome — Scientific Reasoning Benchmark

A production-ready scientific reasoning benchmark dataset created automatically by **Dataset Genome**.

## Dataset Statistics
- **Total Records**: 2,450
- **Feature Columns**: 18
- **Primary Domains**: Agriculture, Medicine, Climate Science, Physics
- **Adaptive Dataset Score**: 79.0 / 100

## Quick Usage
\`\`\`python
from datasets import load_dataset
dataset = load_dataset("dataset-genome/scientific-reasoning-benchmark")
\`\`\`
`,
    },
    {
      platform: "Kaggle Datasets",
      type: "Kaggle Dataset Bundle",
      repo: "kaggle/datasetgenome/scientific-reasoning-benchmark",
      status: "PUBLISHED & READY",
      url: "https://www.kaggle.com/datasets/datasetgenome/scientific-reasoning-benchmark",
      version: "v2.0-adaptive",
      releaseTag: "v2.0.0",
      readmeContent: `# Kaggle Release — Dataset Genome

Kaggle dataset package containing pre-tokenized JSONL files, JSON schema manifests, and exploratory analytics.

License: CC-BY-4.0
`,
    },
    {
      platform: "GitHub Releases",
      type: "Open Source Code & Artifacts",
      repo: "surabhicodes/adaption-autoscientist-challenge-part-2-60000-prize-pool-surabhicodes",
      status: "SYNCED TO MAIN",
      url: "https://github.com/surabhicodes/adaption-autoscientist-challenge-part-2-60000-prize-pool-surabhicodes",
      version: "v2.0-adaptive",
      releaseTag: "v2.0.0-final",
      readmeContent: `# Adaption Labs Challenge — Dataset Genome

Repository containing the full 7-stage autonomous Dataset Genome backend platform, OpenAPI specs, and Next.js frontend dashboard.
`,
    },
  ];

  const currentPub = publications.find(
    (p) =>
      (activeCardTab === "hf" && p.platform.includes("Hugging Face")) ||
      (activeCardTab === "kaggle" && p.platform.includes("Kaggle")) ||
      (activeCardTab === "github" && p.platform.includes("GitHub"))
  ) || publications[0];

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Share2 className="w-5 h-5 text-[#3B82F6]" />
          Open Source Ecosystem Publication Engine
        </h1>
        <p className="text-xs text-gray-400">
          Publish and sync optimized dataset packages, model cards, and changelogs directly to Hugging Face, Kaggle, and GitHub.
        </p>
      </div>

      {/* Target Platform Tabs */}
      <div className="flex items-center gap-4 border-b border-[#1F2937] pb-4">
        {[
          { id: "hf", label: "Hugging Face Hub" },
          { id: "kaggle", label: "Kaggle Datasets" },
          { id: "github", label: "GitHub Releases" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveCardTab(tab.id as any)}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeCardTab === tab.id
                ? "bg-[#3B82F6] text-white shadow-lg shadow-blue-500/20"
                : "bg-[#111827] text-gray-400 border border-[#1F2937] hover:text-white"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Active Publication Card Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 bg-[#111827] border border-[#1F2937] rounded-xl p-6 space-y-6">
          <div className="space-y-2">
            <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              {currentPub.type}
            </span>
            <h2 className="text-lg font-bold text-white">{currentPub.platform}</h2>
            <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-mono font-semibold">
              <ShieldCheck className="w-4 h-4" /> {currentPub.status}
            </div>
          </div>

          <div className="space-y-3 text-xs border-t border-b border-[#1F2937] py-4">
            <div className="flex justify-between">
              <span className="text-gray-400">Target Repository</span>
              <span className="font-mono text-white text-[11px] truncate max-w-[180px]">{currentPub.repo}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Dataset Version</span>
              <span className="font-mono text-emerald-400 font-semibold">{currentPub.version}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Latest Release Tag</span>
              <span className="font-mono text-blue-400 font-semibold">{currentPub.releaseTag}</span>
            </div>
          </div>

          <a
            href={currentPub.url}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-[#3B82F6] hover:bg-[#2563EB] text-white text-xs font-semibold rounded-lg shadow-lg shadow-blue-500/20 transition-all"
          >
            <span>Open Repository on {currentPub.platform.split(" ")[0]}</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>

        {/* README Preview */}
        <div className="lg:col-span-2 bg-[#111827] border border-[#1F2937] rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-[#1F2937] pb-3">
            <span className="text-xs font-semibold text-white flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-400" />
              Generated README Card Preview
            </span>
            <button className="text-xs text-gray-400 hover:text-white flex items-center gap-1">
              <Copy className="w-3.5 h-3.5" /> Copy Markdown
            </button>
          </div>

          <pre className="bg-[#090D16] border border-[#1F2937] rounded-lg p-4 font-mono text-xs text-gray-300 leading-relaxed overflow-x-auto whitespace-pre-wrap">
            {currentPub.readmeContent}
          </pre>
        </div>
      </div>
    </div>
  );
};
