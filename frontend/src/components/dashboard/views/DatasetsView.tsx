/**
 * DatasetsView.tsx — Datasets Catalog View for Dataset Genome.
 */

"use client";

import React, { useState } from "react";
import { Database, Filter, Plus, Search, CheckCircle2, ArrowUpRight, ShieldCheck, Download } from "lucide-react";

export const DatasetsView: React.FC = () => {
  const [filterDomain, setFilterDomain] = useState("All");

  const datasets = [
    {
      id: "ds-01",
      name: "scientific_reasoning_agri_v2.jsonl",
      domain: "Agriculture",
      rows: "2,450",
      columns: "18",
      version: "v2.0-adaptive",
      adaptiveScore: 79.0,
      trainingReady: true,
      updated: "10 mins ago",
    },
    {
      id: "ds-02",
      name: "clinical_trial_reasoning_bench.jsonl",
      domain: "Medicine",
      rows: "4,120",
      columns: "24",
      version: "v1.4-evolved",
      adaptiveScore: 84.5,
      trainingReady: true,
      updated: "1 hour ago",
    },
    {
      id: "ds-03",
      name: "climate_telemetry_simulations.jsonl",
      domain: "Climate Science",
      rows: "3,890",
      columns: "22",
      version: "v2.1-optimized",
      adaptiveScore: 81.2,
      trainingReady: true,
      updated: "3 hours ago",
    },
    {
      id: "ds-04",
      name: "quantum_physics_hypotheses.jsonl",
      domain: "Physics",
      rows: "1,850",
      columns: "16",
      version: "v1.0-raw",
      adaptiveScore: 68.0,
      trainingReady: false,
      updated: "1 day ago",
    },
    {
      id: "ds-05",
      name: "molecular_chemistry_reactions.jsonl",
      domain: "Chemistry",
      rows: "5,300",
      columns: "28",
      version: "v3.0-adaptive",
      adaptiveScore: 89.4,
      trainingReady: true,
      updated: "2 days ago",
    },
    {
      id: "ds-06",
      name: "genomics_variant_reasoning.jsonl",
      domain: "Genetics Benchmark",
      rows: "2,980",
      columns: "20",
      version: "v2.2-evolved",
      adaptiveScore: 86.1,
      trainingReady: true,
      updated: "3 days ago",
    },
  ];

  const filtered =
    filterDomain === "All"
      ? datasets
      : datasets.filter((d) => d.domain === filterDomain);

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Database className="w-5 h-5 text-[#3B82F6]" />
            Dataset Catalog & Optimization Registry
          </h1>
          <p className="text-xs text-gray-400">
            Manage, evaluate, and optimize scientific datasets for training AutoScientist models.
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white text-xs font-semibold rounded-lg shadow-lg shadow-blue-500/20 transition-all">
          <Plus className="w-4 h-4" />
          <span>Import Dataset</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="flex items-center justify-between bg-[#111827] border border-[#1F2937] p-4 rounded-xl">
        <div className="flex items-center gap-3">
          <Filter className="w-4 h-4 text-gray-400" />
          <span className="text-xs text-gray-300 font-medium">Filter by Domain:</span>
          {["All", "Agriculture", "Medicine", "Climate Science", "Physics", "Chemistry"].map(
            (domain) => (
              <button
                key={domain}
                onClick={() => setFilterDomain(domain)}
                className={`text-xs px-3 py-1 rounded-lg font-medium transition-colors ${
                  filterDomain === domain
                    ? "bg-[#3B82F6] text-white font-semibold"
                    : "bg-[#0B1220] text-gray-400 border border-gray-800 hover:text-white"
                }`}
              >
                {domain}
              </button>
            )
          )}
        </div>
        <span className="text-xs font-mono text-gray-400">
          Showing {filtered.length} datasets
        </span>
      </div>

      {/* Dataset Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((ds) => (
          <div
            key={ds.id}
            className="bg-[#111827] border border-[#1F2937] hover:border-gray-700 rounded-xl p-5 space-y-4 transition-all duration-200 hover:shadow-xl hover:shadow-blue-500/5 flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  {ds.domain}
                </span>
                {ds.trainingReady ? (
                  <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    <ShieldCheck className="w-3 h-3" /> Training Ready
                  </span>
                ) : (
                  <span className="text-[10px] font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                    Raw Baseline
                  </span>
                )}
              </div>

              <div>
                <h3 className="font-semibold text-sm text-white font-mono truncate" title={ds.name}>
                  {ds.name}
                </h3>
                <span className="text-[11px] text-gray-400">Version: {ds.version}</span>
              </div>

              <div className="grid grid-cols-3 gap-2 bg-[#0B1220] p-3 rounded-lg border border-[#1F2937] text-center font-mono">
                <div>
                  <div className="text-[10px] text-gray-400">Rows</div>
                  <div className="text-xs font-bold text-white">{ds.rows}</div>
                </div>
                <div>
                  <div className="text-[10px] text-gray-400">Columns</div>
                  <div className="text-xs font-bold text-white">{ds.columns}</div>
                </div>
                <div>
                  <div className="text-[10px] text-gray-400">Adaptive Score</div>
                  <div className="text-xs font-bold text-emerald-400">{ds.adaptiveScore}</div>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-[#1F2937] flex items-center justify-between text-xs">
              <span className="text-gray-400 text-[10px]">Updated {ds.updated}</span>
              <div className="flex items-center gap-2">
                <button className="p-1.5 text-gray-400 hover:text-white bg-[#0B1220] rounded border border-gray-800 transition-colors">
                  <Download className="w-3.5 h-3.5" />
                </button>
                <button className="flex items-center gap-1 text-xs text-[#3B82F6] hover:text-blue-400 font-semibold">
                  <span>View Details</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
