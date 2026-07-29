"use client";

import React, { useState } from "react";
import { DatasetSpecimen } from "@/lib/mock-genome-data";
import { Activity, AlertCircle, Sparkles } from "lucide-react";

interface SangerChromatogramProps {
  specimen: DatasetSpecimen;
}

export const SangerChromatogram: React.FC<SangerChromatogramProps> = ({ specimen }) => {
  const [hoveredPeak, setHoveredPeak] = useState<number | null>(null);

  const points = specimen.qualityTrace;
  const svgWidth = 400;
  const svgHeight = 90;
  const maxVal = 100;
  const minVal = 0;

  // Calculate SVG path string
  const pathD = points
    .map((val, idx) => {
      const x = (idx / (points.length - 1)) * svgWidth;
      const y = svgHeight - ((val - minVal) / (maxVal - minVal)) * (svgHeight - 20) - 10;
      return `${idx === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");

  // Fill area under path
  const areaD = `${pathD} L ${svgWidth} ${svgHeight} L 0 ${svgHeight} Z`;

  return (
    <div className="bg-[#FFFFFF] border border-[#14171A]/10 rounded-md p-3 select-none shadow-xs">
      <div className="flex items-center justify-between mb-2 font-mono-display text-xs">
        <div className="flex items-center gap-1.5 font-bold text-[#14171A]">
          <Activity className="w-3.5 h-3.5 text-[#0F6B5C]" />
          <span>SANGER QUALITY CHROMATOGRAM</span>
        </div>
        <span className="font-mono-data text-[10px] text-[#0F6B5C] bg-[#0F6B5C]/10 px-1.5 py-0.5 rounded font-medium">
          SIGNAL: OPTIMAL
        </span>
      </div>

      <p className="font-sans text-[11px] text-[#14171A]/60 mb-3">
        Sequencing trace amplitudes across dataset genome loci. Peaks indicate data drift & null anomalies.
      </p>

      {/* SVG Sanger Trace Container */}
      <div className="relative bg-[#EEF2EF]/60 rounded border border-[#14171A]/08 p-2 overflow-hidden">
        {/* Background Grid Lines */}
        <div className="absolute inset-0 bg-grid-instrument opacity-50 pointer-events-none" />

        <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-24 overflow-visible relative z-10">
          <defs>
            <linearGradient id="traceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#0F6B5C" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#0F6B5C" stopOpacity="0.0" />
            </linearGradient>

            <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#0F6B5C" />
              <stop offset="50%" stopColor="#3FA66D" />
              <stop offset="100%" stopColor="#3C6E9C" />
            </linearGradient>
          </defs>

          {/* Area Fill */}
          <path d={areaD} fill="url(#traceGradient)" />

          {/* Animated Line Path */}
          <path
            d={pathD}
            fill="none"
            stroke="url(#lineGradient)"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="animate-draw-trace"
          />

          {/* Data Points & Peak Markers */}
          {points.map((val, idx) => {
            const x = (idx / (points.length - 1)) * svgWidth;
            const y = svgHeight - ((val - minVal) / (maxVal - minVal)) * (svgHeight - 20) - 10;
            const peakInfo = specimen.qualityTracePeaks.find((p) => p.pos === idx);
            const isHovered = hoveredPeak === idx;

            return (
              <g key={idx} onMouseEnter={() => setHoveredPeak(idx)} onMouseLeave={() => setHoveredPeak(null)} className="cursor-pointer">
                {/* Data point circle */}
                <circle
                  cx={x}
                  cy={y}
                  r={isHovered ? "4" : "2.5"}
                  fill={peakInfo ? "#D64545" : "#0F6B5C"}
                  stroke="#FFFFFF"
                  strokeWidth="1"
                  className="transition-all"
                />

                {/* Peak Anomaly Callout */}
                {peakInfo && (
                  <g transform={`translate(${x}, ${y - 12})`}>
                    <rect x="-10" y="-12" width="20" height="12" rx="2" fill="#D64545" />
                    <text x="0" y="-3" textAnchor="middle" fill="#FFFFFF" fontSize="9" className="font-mono-display font-bold">
                      {peakInfo.base}
                    </text>
                  </g>
                )}

                {/* Hover Tooltip */}
                {isHovered && (
                  <g transform={`translate(${Math.min(svgWidth - 60, Math.max(60, x))}, ${Math.max(25, y - 20)})`}>
                    <rect x="-55" y="-22" width="110" height="22" rx="3" fill="#14171A" opacity="0.9" />
                    <text x="0" y="-8" textAnchor="middle" fill="#FFFFFF" fontSize="10" className="font-mono-data">
                      Locus #{idx + 1}: {val}% quality
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>

        {/* Genome Base-Pair Scale Footer */}
        <div className="flex justify-between items-center mt-1 font-mono-data text-[9px] text-[#14171A]/50 border-t border-[#14171A]/08 pt-1">
          <span>0bp</span>
          <span>50bp</span>
          <span>100bp</span>
          <span>150bp</span>
          <span>200bp</span>
        </div>
      </div>

      {/* Peak Anomaly Summary List */}
      {specimen.qualityTracePeaks.length > 0 && (
        <div className="mt-3.5 space-y-1.5">
          <div className="font-mono-display text-[11px] font-semibold text-[#14171A]/80 flex items-center gap-1">
            <AlertCircle className="w-3.5 h-3.5 text-[#D64545]" />
            <span>LOCUS ANOMALY PEAKS</span>
          </div>
          {specimen.qualityTracePeaks.map((peak, idx) => (
            <div key={idx} className="flex items-center justify-between text-[11px] font-mono-data bg-[#D64545]/08 border border-[#D64545]/20 rounded p-1.5 text-[#D64545]">
              <span className="font-bold">Base-{peak.base} @ Locus #{peak.pos}</span>
              <span>{peak.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
