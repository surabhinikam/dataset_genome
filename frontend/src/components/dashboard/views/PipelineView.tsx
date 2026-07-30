/**
 * PipelineView.tsx — Visual Execution Timeline View for Dataset Genome.
 */

"use client";

import React, { useState } from "react";
import { GitMerge, CheckCircle2, ChevronDown, ChevronUp, Terminal, FileCode, Clock, Box } from "lucide-react";

export const PipelineView: React.FC = () => {
  const [expandedStage, setExpandedStage] = useState<number | null>(3);

  const pipelineStages = [
    {
      id: 1,
      name: "Dataset Generator",
      module: "app.dataset_generator",
      duration: "0.02s",
      status: "COMPLETED",
      score: "54.2 / 100",
      input: '{ "domain": "Agriculture", "count": 20 }',
      output: '{ "generated_records": 20, "fields": ["id", "hypothesis", "experiment", "reasoning_steps"] }',
      artifacts: ["raw_records.json"],
      logs: [
        "[00:00:00.01] Instantiating DatasetGenerator for domain 'Agriculture'...",
        "[00:00:00.02] Generated 20 raw scientific reasoning samples cleanly.",
      ],
    },
    {
      id: 2,
      name: "Dataset Intelligence",
      module: "app.dataset_intelligence",
      duration: "0.04s",
      status: "COMPLETED",
      score: "68.5 / 100",
      input: '{ "records_count": 20 }',
      output: '{ "health_score": 88.4, "completeness": 96.2, "feature_quality": 84.1 }',
      artifacts: ["intel_report.json", "intel_report.md"],
      logs: [
        "[00:00:00.03] Profiling dataset completeness, feature distribution, noise, and health scores...",
        "[00:00:00.04] Dataset Health Score: 88.4 / 100.",
      ],
    },
    {
      id: 3,
      name: "Evolution Planner",
      module: "app.dataset_evolution",
      duration: "0.03s",
      status: "COMPLETED",
      score: "71.0 / 100",
      input: '{ "analysis_report": "intel_report.json" }',
      output: '{ "issues_identified": 4, "recommendations_count": 4, "severity": "HIGH" }',
      artifacts: ["evolution_plan.json"],
      logs: [
        "[00:00:00.05] Analyzing DatasetAnalysisReport for quality gaps...",
        "[00:00:00.06] EvolutionPlan created with 4 prioritized optimization recommendations.",
      ],
    },
    {
      id: 4,
      name: "Adaptive Data Engine",
      module: "app.adaptive_data",
      duration: "0.05s",
      status: "COMPLETED",
      score: "79.0 / 100",
      input: '{ "raw_records": 20, "evolution_plan": "evolution_plan.json" }',
      output: '{ "adaptive_score": 79.0, "cleaner": "PASS", "validator": "PASS", "balancer": "PASS" }',
      artifacts: ["dataset_final.json", "dataset_summary.md", "schema.json"],
      logs: [
        "[00:00:00.07] Cleaner agent handling nulls and outliers...",
        "[00:00:00.08] Validator agent validating JSON schemas...",
        "[00:00:00.09] Balancer agent adjusting domain distributions...",
        "[00:00:00.10] Adaptive Data Engine output score: 79.0 / 100.",
      ],
    },
    {
      id: 5,
      name: "AutoScientist Integration Layer",
      module: "app.integrations.autoscientist",
      duration: "0.08s",
      status: "COMPLETED",
      score: "88.5% Acc",
      input: '{ "dataset": "dataset_final.json", "model_version": "v1.0" }',
      output: '{ "hypothesis_accuracy": 0.885, "reasoning_score": 0.912, "training_status": "COMPLETED" }',
      artifacts: ["evaluation.json", "training_summary.md"],
      logs: [
        "[00:00:00.11] AutoScientist Adapter mapping TrainingReadyDataset schema...",
        "[00:00:00.12] Benchmarking reasoning hypothesis accuracy against AutoScientist client...",
        "[00:00:00.13] Benchmarked hypothesis accuracy: 88.5%.",
      ],
    },
    {
      id: 6,
      name: "Publication & Open Source Engine",
      module: "app.publication",
      duration: "0.04s",
      status: "COMPLETED",
      score: "READY",
      input: '{ "dataset": "dataset_final.json", "result": "evaluation.json" }',
      output: '{ "hf_ready": true, "kaggle_ready": true, "artifacts_count": 14 }',
      artifacts: ["DATASET_CARD.md", "MODEL_CARD.md", "dataset-metadata.json", "CHANGELOG.md"],
      logs: [
        "[00:00:00.14] Packaging Kaggle dataset zip and dataset-metadata.json...",
        "[00:00:00.15] Generating Hugging Face DATASET_CARD.md & MODEL_CARD.md...",
        "[00:00:00.16] Publication engine release ready.",
      ],
    },
    {
      id: 7,
      name: "Orchestration Engine",
      module: "app.orchestrator",
      duration: "0.01s",
      status: "COMPLETED",
      score: "PASSED",
      input: '{ "pipeline": "full_7_stage" }',
      output: '{ "final_state": "COMPLETED", "execution_time_seconds": 0.26 }',
      artifacts: ["run_report.json", "run_report.md"],
      logs: [
        "[00:00:00.17] State machine transition: PUBLISHING -> COMPLETED.",
        "[00:00:00.18] Emitted GenomeEventType.PipelineCompleted event.",
      ],
    },
  ];

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <GitMerge className="w-5 h-5 text-[#3B82F6]" />
          Visual Execution Timeline & Pipeline Telemetry
        </h1>
        <p className="text-xs text-gray-400">
          Inspect input payloads, stage outputs, execution logs, and output artifacts across all 7 platform stages.
        </p>
      </div>

      {/* Timeline Stage List */}
      <div className="space-y-4">
        {pipelineStages.map((stage) => {
          const isExpanded = expandedStage === stage.id;
          return (
            <div
              key={stage.id}
              className={`bg-[#111827] border rounded-xl overflow-hidden transition-all ${
                isExpanded ? "border-[#3B82F6]" : "border-[#1F2937]"
              }`}
            >
              {/* Stage Header */}
              <button
                onClick={() => setExpandedStage(isExpanded ? null : stage.id)}
                className="w-full p-4 flex items-center justify-between hover:bg-[#161F33] transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center font-mono text-xs font-bold">
                    0{stage.id}
                  </div>
                  <div className="text-left">
                    <div className="font-semibold text-sm text-white flex items-center gap-2">
                      {stage.name}
                      <span className="text-[10px] font-mono text-gray-500 bg-gray-800 px-2 py-0.5 rounded border border-gray-700">
                        {stage.module}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400">Duration: {stage.duration}</div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <span className="font-mono text-xs text-emerald-400 font-semibold bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20">
                    {stage.score}
                  </span>
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  )}
                </div>
              </button>

              {/* Expanded Detail View */}
              {isExpanded && (
                <div className="p-5 border-t border-[#1F2937] bg-[#0B1220]/70 space-y-5">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Input */}
                    <div className="space-y-2">
                      <span className="text-xs font-semibold text-gray-400 flex items-center gap-1.5">
                        <FileCode className="w-3.5 h-3.5 text-blue-400" /> Input Payload
                      </span>
                      <pre className="bg-[#070B14] border border-[#1F2937] rounded-md p-3 font-mono text-[11px] text-blue-300 overflow-x-auto">
                        {stage.input}
                      </pre>
                    </div>

                    {/* Output */}
                    <div className="space-y-2">
                      <span className="text-xs font-semibold text-gray-400 flex items-center gap-1.5">
                        <FileCode className="w-3.5 h-3.5 text-emerald-400" /> Output Result
                      </span>
                      <pre className="bg-[#070B14] border border-[#1F2937] rounded-md p-3 font-mono text-[11px] text-emerald-300 overflow-x-auto">
                        {stage.output}
                      </pre>
                    </div>
                  </div>

                  {/* Artifacts */}
                  <div className="space-y-2">
                    <span className="text-xs font-semibold text-gray-400 flex items-center gap-1.5">
                      <Box className="w-3.5 h-3.5 text-violet-400" /> Generated Artifacts
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {stage.artifacts.map((art) => (
                        <span
                          key={art}
                          className="font-mono text-xs bg-gray-800 text-gray-200 px-2.5 py-1 rounded border border-gray-700"
                        >
                          {art}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Logs */}
                  <div className="space-y-2">
                    <span className="text-xs font-semibold text-gray-400 flex items-center gap-1.5">
                      <Terminal className="w-3.5 h-3.5 text-amber-400" /> Execution Logs
                    </span>
                    <div className="bg-[#070B14] border border-[#1F2937] rounded-md p-3 font-mono text-xs text-gray-300 space-y-1">
                      {stage.logs.map((log, idx) => (
                        <div key={idx}>{log}</div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
