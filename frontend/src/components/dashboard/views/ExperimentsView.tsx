/**
 * ExperimentsView.tsx — Scientific Experiments Benchmark View for Dataset Genome.
 */

"use client";

import React from "react";
import { FlaskConical, CheckCircle2, AlertTriangle, Play, Sparkles, FileText, ArrowUpRight } from "lucide-react";

export const ExperimentsView: React.FC = () => {
  const experiments = [
    {
      id: "exp-101",
      name: "Soil Mineral Balance vs Crop Resistance",
      domain: "Agriculture",
      status: "VERIFIED",
      hypothesisAccuracy: "91.2%",
      reasoningSteps: 6,
      failureCoverage: "88.0%",
      narratorSummary: "Formulated hypothesis correlating potassium deficiency with fungal susceptibility under humid conditions.",
    },
    {
      id: "exp-102",
      name: "Clinical Trial Adverse Reaction Predictor",
      domain: "Medicine",
      status: "VERIFIED",
      hypothesisAccuracy: "88.5%",
      reasoningSteps: 8,
      failureCoverage: "92.4%",
      narratorSummary: "Identified interaction between ACE inhibitors and high-sodium diets leading to mild electrolyte imbalances.",
    },
    {
      id: "exp-103",
      name: "Ocean Thermal Expansion Telemetry",
      domain: "Climate Science",
      status: "VERIFIED",
      hypothesisAccuracy: "86.4%",
      reasoningSteps: 5,
      failureCoverage: "84.1%",
      narratorSummary: "Simulated deep ocean thermal storage capacity anomalies across tropical pacific grid points.",
    },
    {
      id: "exp-104",
      name: "Quantum Superconductor Critical Temperature",
      domain: "Physics",
      status: "OPTIMIZING",
      hypothesisAccuracy: "74.0%",
      reasoningSteps: 7,
      failureCoverage: "68.5%",
      narratorSummary: "Evaluated high-pressure cuprate lattice phase transitions; flagged low experiment diversity.",
    },
  ];

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-amber-400" />
            Scientific Reasoning Experiments & Benchmark Suite
          </h1>
          <p className="text-xs text-gray-400">
            Autonomous experiment planning, reasoning trace validation, and failure coverage benchmarks.
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white text-xs font-semibold rounded-lg shadow-lg shadow-blue-500/20 transition-all">
          <Play className="w-4 h-4 fill-current" />
          <span>Plan New Experiment</span>
        </button>
      </div>

      {/* Experiment Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {experiments.map((exp) => (
          <div
            key={exp.id}
            className="bg-[#111827] border border-[#1F2937] hover:border-gray-700 rounded-xl p-6 space-y-4 transition-all"
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  {exp.domain}
                </span>
                <h3 className="font-bold text-base text-white mt-2">{exp.name}</h3>
                <span className="text-[11px] text-gray-400 font-mono">ID: {exp.id}</span>
              </div>
              <span className="flex items-center gap-1 text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20 font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5" /> {exp.status}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 bg-[#0B1220] p-3 rounded-lg border border-[#1F2937] text-center font-mono">
              <div>
                <div className="text-[10px] text-gray-400">Accuracy</div>
                <div className="text-sm font-bold text-emerald-400">{exp.hypothesisAccuracy}</div>
              </div>
              <div>
                <div className="text-[10px] text-gray-400">Reasoning Steps</div>
                <div className="text-sm font-bold text-white">{exp.reasoningSteps}</div>
              </div>
              <div>
                <div className="text-[10px] text-gray-400">Failure Coverage</div>
                <div className="text-sm font-bold text-violet-400">{exp.failureCoverage}</div>
              </div>
            </div>

            <div className="space-y-1 bg-[#090D16] border border-[#1F2937] rounded-lg p-3">
              <span className="text-[11px] font-semibold text-gray-400 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" /> AutoScientist Narrator Summary
              </span>
              <p className="text-xs text-gray-300 italic leading-relaxed">
                "{exp.narratorSummary}"
              </p>
            </div>

            <div className="pt-2 flex justify-end">
              <button className="flex items-center gap-1 text-xs text-[#3B82F6] hover:text-blue-400 font-semibold">
                <span>View Full Reasoning Trace</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
