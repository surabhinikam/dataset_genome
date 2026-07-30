/**
 * AnalyticsView.tsx — Recharts Visual Analytics View for Dataset Genome.
 */

"use client";

import React from "react";
import { BarChart3, TrendingUp, PieChart as PieIcon, Activity } from "lucide-react";
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

export const AnalyticsView: React.FC = () => {
  const healthTrendData = [
    { run: "Run 1", rawHealth: 54.2, evolvedHealth: 68.5, adaptiveHealth: 79.0, target: 85.0 },
    { run: "Run 2", rawHealth: 56.1, evolvedHealth: 71.0, adaptiveHealth: 82.4, target: 85.0 },
    { run: "Run 3", rawHealth: 58.0, evolvedHealth: 74.2, adaptiveHealth: 85.1, target: 85.0 },
    { run: "Run 4", rawHealth: 60.5, evolvedHealth: 78.0, adaptiveHealth: 88.4, target: 85.0 },
    { run: "Run 5", rawHealth: 62.4, evolvedHealth: 81.5, adaptiveHealth: 91.2, target: 85.0 },
  ];

  const domainDistribution = [
    { name: "Agriculture", records: 850, color: "#3B82F6" },
    { name: "Medicine", records: 620, color: "#8B5CF6" },
    { name: "Climate Science", records: 540, color: "#22C55E" },
    { name: "Physics", records: 440, color: "#F59E0B" },
  ];

  const difficultyDistribution = [
    { difficulty: "Easy", count: 420 },
    { difficulty: "Medium", count: 1150 },
    { difficulty: "Hard", count: 680 },
    { difficulty: "Expert", count: 200 },
  ];

  const coverageMetrics = [
    { metric: "Knowledge Coverage", raw: 64.0, optimized: 92.4 },
    { metric: "Reasoning Density", raw: 58.2, optimized: 86.1 },
    { metric: "Experiment Diversity", raw: 61.0, optimized: 84.0 },
    { metric: "Failure Coverage", raw: 52.5, optimized: 88.0 },
  ];

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-[#3B82F6]" />
          Dataset Quality & Optimization Analytics
        </h1>
        <p className="text-xs text-gray-400">
          Interactive charts tracking dataset health progression, domain balancing, and reasoning density metrics.
        </p>
      </div>

      {/* Row 1: Dataset Health & Adaptive Score Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Chart 1: Dataset Health Trend */}
        <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                Dataset Health & Adaptive Score Progression
              </h2>
              <p className="text-[11px] text-gray-400">Progression across 5 autonomous pipeline runs</p>
            </div>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              +37.0% Growth
            </span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={healthTrendData}>
                <defs>
                  <linearGradient id="adaptiveGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="run" stroke="#6B7280" fontSize={11} />
                <YAxis stroke="#6B7280" fontSize={11} domain={[40, 100]} />
                <Tooltip contentStyle={{ backgroundColor: "#0B1220", borderColor: "#1F2937", borderRadius: "8px", fontSize: "12px" }} />
                <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                <Area type="monotone" dataKey="adaptiveHealth" name="Adaptive Engine Score" stroke="#3B82F6" fillOpacity={1} fill="url(#adaptiveGrad)" strokeWidth={2} />
                <Line type="monotone" dataKey="evolvedHealth" name="Evolution Planner Score" stroke="#8B5CF6" strokeWidth={2} />
                <Line type="monotone" dataKey="rawHealth" name="Raw Baseline Score" stroke="#6B7280" strokeDasharray="5 5" strokeWidth={1.5} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Knowledge Coverage & Reasoning Density Comparison */}
        <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Activity className="w-4 h-4 text-[#3B82F6]" />
                Raw vs. Adaptive Optimized Benchmark Coverage
              </h2>
              <p className="text-[11px] text-gray-400">Comparing baseline vs optimized metric quality</p>
            </div>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={coverageMetrics}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="metric" stroke="#6B7280" fontSize={10} />
                <YAxis stroke="#6B7280" fontSize={11} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: "#0B1220", borderColor: "#1F2937", borderRadius: "8px", fontSize: "12px" }} />
                <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                <Bar dataKey="raw" name="Raw Baseline (%)" fill="#4B5563" radius={[4, 4, 0, 0]} />
                <Bar dataKey="optimized" name="Dataset Genome Adaptive (%)" fill="#22C55E" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 2: Domain Distribution & Difficulty Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Chart 3: Domain Distribution */}
        <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <PieIcon className="w-4 h-4 text-violet-400" />
            Scientific Domain Distribution
          </h2>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={domainDistribution} dataKey="records" nameKey="name" cx="50%" cy="50%" outerRadius={85} label={({ name, records }: any) => `${name} (${records})`}>
                  {domainDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: "#0B1220", borderColor: "#1F2937", borderRadius: "8px", fontSize: "12px" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: Difficulty Imbalance */}
        <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-amber-400" />
            Reasoning Difficulty Distribution
          </h2>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={difficultyDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="difficulty" stroke="#6B7280" fontSize={11} />
                <YAxis stroke="#6B7280" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: "#0B1220", borderColor: "#1F2937", borderRadius: "8px", fontSize: "12px" }} />
                <Bar dataKey="count" name="Record Count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
