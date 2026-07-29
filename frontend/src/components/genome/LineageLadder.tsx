"use client";

import React, { useState } from "react";
import { DatasetSpecimen, LineageRung, OPERATION_COLOR_MAP } from "@/lib/mock-genome-data";
import { Dna, ZoomIn, ZoomOut, RotateCcw, Sparkles, Layers, Activity, GitCommit, Check } from "lucide-react";

interface LineageLadderProps {
  specimens: Record<string, DatasetSpecimen>;
  rungs: LineageRung[];
  selectedSpecimenId: string;
  onSelectSpecimen: (id: string) => void;
  tracedPathIds: string[];
}

export const LineageLadder: React.FC<LineageLadderProps> = ({
  specimens,
  rungs,
  selectedSpecimenId,
  onSelectSpecimen,
  tracedPathIds,
}) => {
  const [zoomLevel, setZoomLevel] = useState<number>(1.0);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Layout node coordinates for horizontal DNA ladder
  const nodePositions: Record<string, { x: number; y: number; tier: number }> = {
    "raw-transactions": { x: 70, y: 120, tier: 1 },
    "raw-users": { x: 70, y: 380, tier: 1 },
    "filtered-users": { x: 320, y: 380, tier: 2 },
    "user-transactions": { x: 570, y: 250, tier: 3 },
    "cleaned-events": { x: 820, y: 250, tier: 4 },
    "enriched-profiles": { x: 1070, y: 250, tier: 5 },
    "customers": { x: 1320, y: 130, tier: 6 },
    "churn-features": { x: 1320, y: 370, tier: 6 },
    "final-training": { x: 1570, y: 250, tier: 7 },
  };

  const svgWidth = 1750;
  const svgHeight = 520;

  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.15, 1.6));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 0.15, 0.65));
  const handleResetZoom = () => setZoomLevel(1.0);

  const formatRows = (rows: number) => {
    if (rows >= 1000000) return `${(rows / 1000000).toFixed(2)}M`;
    if (rows >= 1000) return `${(rows / 1000).toFixed(0)}K`;
    return rows.toString();
  };

  return (
    <div className="flex-1 bg-[#EEF2EF] relative overflow-hidden flex flex-col h-full select-none">
      {/* Ladder Top Control Bar */}
      <div className="h-10 bg-[#FFFFFF]/80 border-b border-[#14171A]/08 px-4 flex items-center justify-between text-xs font-mono-data z-10">
        <div className="flex items-center gap-2 text-[#14171A]/70">
          <Dna className="w-4 h-4 text-[#0F6B5C]" />
          <span className="font-bold text-[#14171A] font-mono-display">DNA LINEAGE LADDER</span>
          <span className="text-[11px] text-[#14171A]/50">| 9 Specimen Nodes • 9 Derivation Rungs</span>
        </div>

        {/* Zoom & View Controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={handleZoomOut}
            className="p-1 rounded hover:bg-[#EEF2EF] text-[#14171A]/70"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="px-1.5 text-[11px] text-[#0F6B5C] font-bold">{Math.round(zoomLevel * 100)}%</span>
          <button
            onClick={handleZoomIn}
            className="p-1 rounded hover:bg-[#EEF2EF] text-[#14171A]/70"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleResetZoom}
            className="p-1 rounded hover:bg-[#EEF2EF] text-[#14171A]/70 ml-1"
            title="Reset Zoom"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Canvas Scroll Area */}
      <div className="flex-1 overflow-auto relative p-6 bg-grid-instrument">
        {/* Sequencing Light Beam Scan Overlay */}
        <div className="absolute inset-y-0 w-32 bg-gradient-to-r from-transparent via-[#0F6B5C]/20 to-transparent pointer-events-none z-10 animate-sequencing-scan border-r border-[#0F6B5C]/40" />

        {/* Zoom Transform Wrapper */}
        <div
          className="transition-transform duration-200 ease-out origin-top-left relative"
          style={{ transform: `scale(${zoomLevel})` }}
        >
          <svg
            width={svgWidth}
            height={svgHeight}
            className="overflow-visible"
          >
            <defs>
              {/* Rung Markers */}
              <marker
                id="arrow-A"
                viewBox="0 0 10 10"
                refX="6"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3FA66D" />
              </marker>

              <marker
                id="arrow-T"
                viewBox="0 0 10 10"
                refX="6"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#D64545" />
              </marker>

              <marker
                id="arrow-G"
                viewBox="0 0 10 10"
                refX="6"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#D98F3F" />
              </marker>

              <marker
                id="arrow-C"
                viewBox="0 0 10 10"
                refX="6"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3C6E9C" />
              </marker>
            </defs>

            {/* Parallel DNA Backbone Rails */}
            <line x1="20" y1="120" x2={svgWidth - 40} y2="120" stroke="#14171A" strokeWidth="1.5" strokeOpacity="0.15" strokeDasharray="6,6" />
            <line x1="20" y1="250" x2={svgWidth - 40} y2="250" stroke="#14171A" strokeWidth="1.5" strokeOpacity="0.20" strokeDasharray="6,6" />
            <line x1="20" y1="380" x2={svgWidth - 40} y2="380" stroke="#14171A" strokeWidth="1.5" strokeOpacity="0.15" strokeDasharray="6,6" />

            {/* DNA Derivation Rungs */}
            {rungs.map((rung) => {
              const srcPos = nodePositions[rung.sourceId];
              const tgtPos = nodePositions[rung.targetId];
              if (!srcPos || !tgtPos) return null;

              const isPathActive = tracedPathIds.includes(rung.sourceId) && tracedPathIds.includes(rung.targetId);
              const cardWidth = 190;
              const cardHeight = 76;

              // Calculate start and end connection points on specimen cards
              const x1 = srcPos.x + cardWidth;
              const y1 = srcPos.y + cardHeight / 2;
              const x2 = tgtPos.x;
              const y2 = tgtPos.y + cardHeight / 2;

              // Cubic bezier control points for smooth phylogenetic curve
              const dx = (x2 - x1) * 0.5;
              const pathD = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;

              const opMeta = OPERATION_COLOR_MAP[rung.operation];

              return (
                <g key={rung.id} className="group">
                  {/* Background halo line */}
                  <path
                    d={pathD}
                    fill="none"
                    stroke={opMeta.hex}
                    strokeWidth={isPathActive ? "5" : "2.5"}
                    strokeOpacity={isPathActive ? "0.9" : "0.55"}
                    markerEnd={`url(#arrow-${opMeta.base})`}
                    className="transition-all"
                  />

                  {/* Ambient Pulsing Dotted Line */}
                  <path
                    d={pathD}
                    fill="none"
                    stroke="#FFFFFF"
                    strokeWidth="1.5"
                    strokeOpacity="0.7"
                    className="animate-rung-pulse"
                  />

                  {/* Rung Operation Badge on midpoint */}
                  <g transform={`translate(${(x1 + x2) / 2}, ${(y1 + y2) / 2})`}>
                    <rect
                      x="-38"
                      y="-11"
                      width="76"
                      height="22"
                      rx="4"
                      fill="#FFFFFF"
                      stroke={opMeta.hex}
                      strokeWidth="1.5"
                      className="shadow-xs"
                    />
                    <text
                      x="0"
                      y="3"
                      textAnchor="middle"
                      fill={opMeta.hex}
                      fontSize="9"
                      className="font-mono-display font-bold"
                    >
                      [{opMeta.base}] {rung.operation}
                    </text>
                  </g>
                </g>
              );
            })}
          </svg>

          {/* HTML Overlay for Specimen Nodes */}
          {Object.entries(specimens).map(([id, specimen]) => {
            const pos = nodePositions[id];
            if (!pos) return null;

            const isSelected = id === selectedSpecimenId;
            const isTraced = tracedPathIds.includes(id);
            const isHovered = id === hoveredNodeId;

            return (
              <div
                key={id}
                style={{
                  position: "absolute",
                  left: `${pos.x}px`,
                  top: `${pos.y}px`,
                  width: "190px",
                }}
                onMouseEnter={() => setHoveredNodeId(id)}
                onMouseLeave={() => setHoveredNodeId(null)}
                onClick={() => onSelectSpecimen(id)}
                className={`specimen-paper-card rounded-md p-2.5 cursor-pointer select-none transition-all ${
                  isSelected
                    ? "ring-2 ring-[#0F6B5C] shadow-md border-[#0F6B5C]"
                    : isTraced
                    ? "ring-1 ring-[#3FA66D] border-[#3FA66D]"
                    : "hover:scale-[1.02]"
                }`}
              >
                {/* Node Top Meta */}
                <div className="flex items-center justify-between gap-1 mb-1">
                  <div className="flex items-center gap-1.5 min-w-0">
                    <span
                      className={`w-2 h-2 rounded-full ${
                        specimen.healthStatus === "healthy"
                          ? "bg-[#3FA66D]"
                          : specimen.healthStatus === "warning"
                          ? "bg-[#D98F3F]"
                          : "bg-[#D64545]"
                      }`}
                    />
                    <span className="font-mono-display font-bold text-xs text-[#14171A] truncate">
                      {specimen.name}
                    </span>
                  </div>

                  <span className="font-mono-data text-[10px] px-1.5 py-0.2 rounded bg-[#EEF2EF] text-[#14171A]/70 font-semibold border border-[#14171A]/08">
                    {specimen.version}
                  </span>
                </div>

                {/* Node Subtitle Meta */}
                <div className="flex items-center justify-between text-[11px] font-mono-data text-[#14171A]/60 mt-1">
                  <span>{formatRows(specimen.rowCount)} rows</span>
                  <span className="text-[#0F6B5C] font-semibold">{specimen.healthScore}%</span>
                </div>

                {/* Hover Chromatogram Preview Popup */}
                {isHovered && !isSelected && (
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 bg-[#14171A] text-[#FFFFFF] p-2 rounded shadow-lg z-30 font-mono-data text-[10px] pointer-events-none animate-slide-up">
                    <div className="flex justify-between border-b border-[#FFFFFF]/10 pb-1 mb-1 font-mono-display font-bold text-[9px] text-[#3FA66D]">
                      <span>CHROMATOGRAM PREVIEW</span>
                      <span>{specimen.healthScore}% HEALTH</span>
                    </div>
                    <p className="text-[#FFFFFF]/80 line-clamp-2">{specimen.description}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Rung Operation Legend Footer */}
      <div className="bg-[#FFFFFF] border-t border-[#14171A]/10 px-4 py-2 flex items-center justify-between font-mono-data text-xs z-10 flex-wrap gap-2">
        <div className="flex items-center gap-4">
          <span className="font-mono-display font-bold text-[11px] text-[#14171A]">BASE PAIR LEGEND:</span>
          {Object.entries(OPERATION_COLOR_MAP).map(([op, meta]) => (
            <div key={op} className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: meta.hex }} />
              <span className="text-[#14171A]/80 font-medium text-[11px]">
                [{meta.base}] {op}
              </span>
            </div>
          ))}
        </div>

        <div className="text-[11px] text-[#14171A]/50 font-mono-data hidden md:block">
          Click any specimen card to open Sanger Inspector.
        </div>
      </div>
    </div>
  );
};
