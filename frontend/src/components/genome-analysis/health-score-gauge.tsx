"use client";

/**
 * components/genome-analysis/health-score-gauge.tsx — Health Score Visual Gauge.
 *
 * Displays the overall Dataset Health Score (0-100) with a circular SVG progress ring,
 * color-coded grade badge, and dimension breakdown.
 */

import type { HealthScoreResult } from "@/types/intelligence";

interface HealthScoreGaugeProps {
  healthScore: HealthScoreResult;
}

export default function HealthScoreGauge({ healthScore }: HealthScoreGaugeProps) {
  const score = healthScore.overall_score;
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const gradeColorMap = {
    Excellent: "from-emerald-500 to-teal-400 text-emerald-300 border-emerald-500/30 bg-emerald-500/10",
    Good: "from-indigo-500 to-violet-400 text-indigo-300 border-indigo-500/30 bg-indigo-500/10",
    Fair: "from-amber-500 to-yellow-400 text-amber-300 border-amber-500/30 bg-amber-500/10",
    Poor: "from-red-500 to-rose-400 text-red-300 border-red-500/30 bg-red-500/10",
  };

  const badgeStyle = gradeColorMap[healthScore.grade] || gradeColorMap.Good;

  return (
    <div className="relative flex flex-col items-center justify-between rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.05] to-white/[0.02] p-6 shadow-2xl backdrop-blur-xl md:flex-row md:items-center">
      {/* Left: Gauge Circle */}
      <div className="flex flex-col items-center gap-3">
        <div className="relative flex h-36 w-36 items-center justify-center">
          <svg className="h-full w-full -rotate-90 transform" viewBox="0 0 120 120">
            {/* Background ring */}
            <circle
              cx="60"
              cy="60"
              r={radius}
              className="stroke-white/10"
              strokeWidth="8"
              fill="transparent"
            />
            {/* Gradient progress ring */}
            <circle
              cx="60"
              cy="60"
              r={radius}
              stroke="url(#scoreGradient)"
              strokeWidth="10"
              strokeLinecap="round"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className="transition-all duration-1000 ease-out"
            />
            <defs>
              <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#a78bfa" />
                <stop offset="50%" stopColor="#6366f1" />
                <stop offset="100%" stopColor="#10b981" />
              </linearGradient>
            </defs>
          </svg>

          {/* Center text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className="text-3xl font-extrabold tracking-tight text-white">{score}</span>
            <span className="text-[10px] font-semibold uppercase tracking-widest text-white/40">/ 100</span>
          </div>
        </div>

        {/* Grade badge */}
        <div className={`flex items-center gap-1.5 rounded-full border px-3.5 py-1 text-xs font-semibold uppercase tracking-wider ${badgeStyle}`}>
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-current" />
          {healthScore.grade} Grade
        </div>
      </div>

      {/* Right: Dimension breakdown grid */}
      <div className="mt-6 flex-1 md:ml-8 md:mt-0">
        <h3 className="mb-3 text-xs font-bold uppercase tracking-wider text-white/40">
          Health Dimensions Breakdown
        </h3>
        <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3">
          {Object.entries(healthScore.breakdown).map(([dim, val]) => (
            <div key={dim} className="rounded-xl border border-white/5 bg-white/[0.02] p-3 transition-colors hover:border-white/10">
              <span className="block text-[11px] capitalize text-white/50">
                {dim.replace("_", " ")}
              </span>
              <div className="mt-1 flex items-baseline justify-between">
                <span className="text-base font-bold text-white">{val}%</span>
                <span
                  className={`text-[10px] font-medium ${
                    val >= 85 ? "text-emerald-400" : val >= 70 ? "text-indigo-400" : val >= 50 ? "text-amber-400" : "text-red-400"
                  }`}
                >
                  {val >= 85 ? "Optimal" : val >= 70 ? "Good" : "Notice"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
