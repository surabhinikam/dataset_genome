/**
 * DashboardHome.tsx — Main Home Dashboard View for Dataset Genome.
 *
 * Replaces genomics/DNA visual metaphors with an AI Dataset Evolution Pipeline,
 * KPI metrics, and right-panel Dataset Summary.
 */

"use client";

import React, { useState } from "react";
import {
  Activity,
  Award,
  CheckCircle2,
  BrainCircuit,
  FlaskConical,
  Share2,
  ChevronRight,
  Terminal,
  Database,
  ArrowUpRight,
  TrendingUp,
  FileCode,
  Zap,
} from "lucide-react";

interface DashboardHomeProps {
  onRunPipeline: () => void;
}

export const DashboardHome: React.FC<DashboardHomeProps> = ({ onRunPipeline }) => {
  const [selectedStage, setSelectedStage] = useState(3); // Default to Adaptive Data Engine

  const kpis = [
    {
      title: "Dataset Health Score",
      value: "88.4%",
      trend: "+4.2% vs raw baseline",
      icon: Activity,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
    },
    {
      title: "Adaptive Dataset Score",
      value: "79.0 / 100",
      trend: "High Reasoning Density",
      icon: Award,
      color: "text-blue-400",
      bg: "bg-blue-500/10",
      border: "border-blue-500/20",
    },
    {
      title: "Training Readiness",
      value: "READY",
      trend: "Validated & Balanced",
      icon: CheckCircle2,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
    },
    {
      title: "Models Benchmark Trained",
      value: "12 Models",
      trend: "AutoScientist v2.4",
      icon: BrainCircuit,
      color: "text-violet-400",
      bg: "bg-violet-500/10",
      border: "border-violet-500/20",
    },
    {
      title: "Scientific Experiments",
      value: "48 Executed",
      trend: "High Failure Coverage",
      icon: FlaskConical,
      color: "text-amber-400",
      bg: "bg-amber-500/10",
      border: "border-amber-500/20",
    },
    {
      title: "Open Source Publications",
      value: "6 Repositories",
      trend: "Hugging Face & Kaggle",
      icon: Share2,
      color: "text-indigo-400",
      bg: "bg-indigo-500/10",
      border: "border-indigo-500/20",
    },
  ];

  const pipelineStages = [
    {
      id: 0,
      name: "Raw Dataset",
      status: "COMPLETED",
      runtime: "0.02s",
      score: "54.2 / 100",
      logs: "Generated 2,450 synthetic reasoning records across 4 scientific domains.",
    },
    {
      id: 1,
      name: "Dataset Intelligence",
      status: "COMPLETED",
      runtime: "0.04s",
      score: "68.5 / 100",
      logs: "Profiled dataset completeness, feature quality, noise level, and correlation.",
    },
    {
      id: 2,
      name: "Evolution Planner",
      status: "COMPLETED",
      runtime: "0.03s",
      score: "71.0 / 100",
      logs: "Formulated 4 prioritized recommendations: balance difficulty & add domain tests.",
    },
    {
      id: 3,
      name: "Adaptive Data Engine",
      status: "COMPLETED",
      runtime: "0.05s",
      score: "79.0 / 100",
      logs: "Cleaned nulls, validated schemas, rebalanced class distribution, enriched metadata.",
    },
    {
      id: 4,
      name: "AutoScientist Adapter",
      status: "COMPLETED",
      runtime: "0.08s",
      score: "88.5% Acc",
      logs: "Benchmarked reasoning accuracy and hypothesis evaluation against baseline model.",
    },
    {
      id: 5,
      name: "Publication Engine",
      status: "COMPLETED",
      runtime: "0.04s",
      score: "READY",
      logs: "Bundled Kaggle & Hugging Face datasets, model cards, and changelog release tags.",
    },
    {
      id: 6,
      name: "Completed",
      status: "SUCCESS",
      runtime: "0.26s Total",
      score: "PASSED",
      logs: "Platform execution finished. Generated run_report.md and run_report.json.",
    },
  ];

  return (
    <div className="p-8 space-y-8">
      {/* Welcome Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-6 bg-gradient-to-r from-[#111827] via-[#161F33] to-[#111827] border border-[#1F2937] rounded-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-full bg-blue-500/5 blur-3xl pointer-events-none" />
        <div className="space-y-1 z-10">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-white tracking-tight">
              Dataset Evolution & Optimization Dashboard
            </h1>
            <span className="text-[10px] px-2 py-0.5 rounded-full font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20 font-semibold">
              Live Engine Active
            </span>
          </div>
          <p className="text-xs text-gray-400 max-w-2xl">
            Autonomous pipeline that analyzes, evolves, optimizes, trains, and publishes high-density scientific datasets for model reasoning benchmarks.
          </p>
        </div>
        <button
          onClick={onRunPipeline}
          className="z-10 flex items-center gap-2 px-4 py-2.5 bg-[#3B82F6] hover:bg-[#2563EB] text-white text-xs font-semibold rounded-lg shadow-lg shadow-blue-500/25 transition-all"
        >
          <Zap className="w-4 h-4 fill-current" />
          <span>Launch Autonomous Pipeline</span>
        </button>
      </div>

      {/* Top KPI Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div
              key={idx}
              className="bg-[#111827] border border-[#1F2937] hover:border-gray-700 rounded-xl p-4 space-y-3 transition-all duration-200"
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-medium text-gray-400">
                  {kpi.title}
                </span>
                <div className={`p-2 rounded-lg ${kpi.bg} ${kpi.border} border`}>
                  <Icon className={`w-4 h-4 ${kpi.color}`} />
                </div>
              </div>
              <div>
                <div className="text-lg font-bold text-white tracking-tight font-mono">
                  {kpi.value}
                </div>
                <div className="text-[10px] text-gray-500 font-medium flex items-center gap-1 mt-0.5">
                  <TrendingUp className="w-3 h-3 text-emerald-400" />
                  <span>{kpi.trend}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Grid: Evolution Workflow + Right Dataset Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Dataset Evolution Pipeline Workflow */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-semibold text-white tracking-tight flex items-center gap-2">
                  <FileCode className="w-4 h-4 text-[#3B82F6]" />
                  Dataset Evolution Pipeline Workflow
                </h2>
                <p className="text-xs text-gray-400">
                  Interactive 7-stage pipeline state machine tracking execution telemetry.
                </p>
              </div>
              <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
                ● Execution ID: exec-run-2036dc35
              </span>
            </div>

            {/* Horizontal Workflow Stepper */}
            <div className="flex items-center justify-between overflow-x-auto pb-4 pt-2 gap-2">
              {pipelineStages.map((stage, idx) => {
                const isSelected = selectedStage === idx;
                return (
                  <React.Fragment key={stage.name}>
                    <button
                      onClick={() => setSelectedStage(idx)}
                      className={`flex flex-col items-center gap-2 min-w-[100px] p-3 rounded-xl border transition-all ${
                        isSelected
                          ? "bg-[#1F2937] border-[#3B82F6] shadow-lg shadow-blue-500/10 text-white"
                          : "bg-[#0B1220]/60 border-[#1F2937] hover:border-gray-700 text-gray-400"
                      }`}
                    >
                      <div
                        className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-mono font-bold ${
                          isSelected
                            ? "bg-[#3B82F6] text-white"
                            : "bg-gray-800 text-gray-400 border border-gray-700"
                        }`}
                      >
                        {idx + 1}
                      </div>
                      <div className="text-[11px] font-semibold text-center leading-tight">
                        {stage.name}
                      </div>
                      <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-gray-800 text-emerald-400">
                        {stage.score}
                      </span>
                    </button>

                    {idx < pipelineStages.length - 1 && (
                      <ChevronRight className="w-4 h-4 text-gray-600 shrink-0" />
                    )}
                  </React.Fragment>
                );
              })}
            </div>

            {/* Selected Stage Detail Panel */}
            <div className="bg-[#0B1220] border border-[#1F2937] rounded-lg p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-[#1F2937] pb-3">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-[#3B82F6] animate-ping" />
                  <h3 className="text-sm font-semibold text-white">
                    Stage {selectedStage + 1}: {pipelineStages[selectedStage].name}
                  </h3>
                </div>
                <div className="flex items-center gap-4 text-xs font-mono">
                  <span className="text-gray-400">
                    Runtime: <strong className="text-white">{pipelineStages[selectedStage].runtime}</strong>
                  </span>
                  <span className="text-emerald-400 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    Status: {pipelineStages[selectedStage].status}
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <span className="text-xs font-semibold text-gray-400 flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-[#3B82F6]" />
                  Execution Telemetry Logs
                </span>
                <div className="bg-[#070B14] border border-[#1F2937] rounded-md p-3 font-mono text-xs text-gray-300">
                  {pipelineStages[selectedStage].logs}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel: Dataset Summary */}
        <div className="space-y-6">
          <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-[#1F2937] pb-4">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-[#3B82F6]" />
                <h3 className="font-semibold text-sm text-white">
                  Active Dataset Summary
                </h3>
              </div>
              <span className="text-[10px] font-mono bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded border border-blue-500/20">
                v2.0-adaptive
              </span>
            </div>

            {/* Specimen Dataset Metadata List */}
            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-1.5 border-b border-gray-800">
                <span className="text-gray-400">Dataset Name</span>
                <span className="font-mono text-white font-medium">scientific_reasoning_agri.jsonl</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-gray-800">
                <span className="text-gray-400">Total Rows</span>
                <span className="font-mono text-white font-medium">2,450 records</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-gray-800">
                <span className="text-gray-400">Feature Columns</span>
                <span className="font-mono text-white font-medium">18 features</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-gray-800">
                <span className="text-gray-400">Primary Domain</span>
                <span className="font-mono text-blue-400 font-medium">Agriculture & Soil</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-gray-800">
                <span className="text-gray-400">Adaptive Score</span>
                <span className="font-mono text-emerald-400 font-bold">79.0 / 100</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-gray-800">
                <span className="text-gray-400">Knowledge Coverage</span>
                <span className="font-mono text-violet-400 font-medium">92.4%</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-gray-800">
                <span className="text-gray-400">Reasoning Quality</span>
                <span className="font-mono text-emerald-400 font-medium">86.1%</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-gray-800">
                <span className="text-gray-400">Experiment Diversity</span>
                <span className="font-mono text-amber-400 font-medium">84.0%</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-gray-800">
                <span className="text-gray-400">Training Status</span>
                <span className="font-mono text-emerald-400 font-semibold">COMPLETED</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-gray-400">Publication Status</span>
                <span className="font-mono text-blue-400 font-semibold">READY FOR HUB</span>
              </div>
            </div>

            <button className="w-full flex items-center justify-center gap-2 py-2.5 bg-[#1F2937] hover:bg-gray-800 text-xs font-semibold text-white rounded-lg border border-gray-700 transition-colors">
              <span>View Schema & Distribution</span>
              <ArrowUpRight className="w-3.5 h-3.5 text-gray-400" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
