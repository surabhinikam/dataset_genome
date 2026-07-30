/**
 * ModelsView.tsx — Benchmark Trained Models View for Dataset Genome.
 */

"use client";

import React from "react";
import { BrainCircuit, CheckCircle2, ArrowUpRight, Cpu, Layers } from "lucide-react";

export const ModelsView: React.FC = () => {
  const models = [
    {
      id: "mdl-01",
      name: "autoscientist-llama-3.2-agri-v2.4",
      baseModel: "meta-llama/Llama-3.2-1B",
      status: "COMPLETED",
      accuracy: "88.5%",
      f1Score: "87.9%",
      loss: "0.142",
      version: "v2.4",
      created: "2026-07-29",
    },
    {
      id: "mdl-02",
      name: "autoscientist-mistral-medicine-v1.8",
      baseModel: "mistralai/Mistral-7B-v0.1",
      status: "COMPLETED",
      accuracy: "92.1%",
      f1Score: "91.8%",
      loss: "0.098",
      version: "v1.8",
      created: "2026-07-28",
    },
    {
      id: "mdl-03",
      name: "autoscientist-qwen-climate-v3.0",
      baseModel: "Qwen/Qwen2.5-7B-Instruct",
      status: "COMPLETED",
      accuracy: "89.4%",
      f1Score: "88.7%",
      loss: "0.115",
      version: "v3.0",
      created: "2026-07-26",
    },
    {
      id: "mdl-04",
      name: "autoscientist-deepseek-physics-v1.0",
      baseModel: "deepseek-ai/DeepSeek-R1-Distill",
      status: "EVALUATING",
      accuracy: "85.2%",
      f1Score: "84.6%",
      loss: "0.189",
      version: "v1.0",
      created: "2026-07-24",
    },
  ];

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <BrainCircuit className="w-5 h-5 text-violet-400" />
          Benchmark Trained Models Registry
        </h1>
        <p className="text-xs text-gray-400">
          Models fine-tuned and benchmarked on Dataset Genome optimized scientific reasoning records.
        </p>
      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {models.map((mdl) => (
          <div
            key={mdl.id}
            className="bg-[#111827] border border-[#1F2937] hover:border-gray-700 rounded-xl p-6 space-y-4 transition-all"
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-violet-500/10 text-violet-400 border border-violet-500/20">
                  {mdl.version}
                </span>
                <h3 className="font-bold text-sm font-mono text-white mt-2 truncate" title={mdl.name}>
                  {mdl.name}
                </h3>
                <span className="text-[11px] text-gray-400">Base: {mdl.baseModel}</span>
              </div>
              <span className="flex items-center gap-1 text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20 font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5" /> {mdl.status}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 bg-[#0B1220] p-3 rounded-lg border border-[#1F2937] text-center font-mono">
              <div>
                <div className="text-[10px] text-gray-400">Accuracy</div>
                <div className="text-sm font-bold text-emerald-400">{mdl.accuracy}</div>
              </div>
              <div>
                <div className="text-[10px] text-gray-400">F1 Score</div>
                <div className="text-sm font-bold text-[#3B82F6]">{mdl.f1Score}</div>
              </div>
              <div>
                <div className="text-[10px] text-gray-400">Eval Loss</div>
                <div className="text-sm font-bold text-amber-400">{mdl.loss}</div>
              </div>
            </div>

            <div className="pt-2 border-t border-[#1F2937] flex items-center justify-between text-xs">
              <span className="text-gray-400 text-[10px] font-mono">Created: {mdl.created}</span>
              <button className="flex items-center gap-1 text-xs text-[#3B82F6] hover:text-blue-400 font-semibold">
                <span>View Evaluation Metrics</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
