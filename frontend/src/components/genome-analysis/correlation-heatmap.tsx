"use client";

/**
 * components/genome-analysis/correlation-heatmap.tsx — Pearson Correlation Heatmap.
 *
 * Visualizes pairwise feature correlations with color-coded cells and highlights
 * high multicollinearity. Optimized for wide datasets to prevent DOM freezing.
 */

import { useState, useMemo } from "react";
import type { CorrelationMetrics } from "@/types/intelligence";

interface CorrelationHeatmapProps {
  correlation: CorrelationMetrics;
}

export default function CorrelationHeatmap({ correlation }: CorrelationHeatmapProps) {
  const { numeric_columns, matrix, high_correlation_pairs } = correlation;
  const [showAll, setShowAll] = useState(false);
  const [hoveredCell, setHoveredCell] = useState<{ c1: string; c2: string; val: number } | null>(null);

  // Maximum columns to render by default to prevent DOM freezing on wide datasets
  const MAX_DEFAULT_COLS = 12;
  const isLargeMatrix = numeric_columns.length > MAX_DEFAULT_COLS;

  const displayCols = useMemo(() => {
    if (!isLargeMatrix || showAll) return numeric_columns;

    // Prioritize columns involved in high correlation pairs first
    const prioritized = new Set<string>();
    for (const pair of high_correlation_pairs) {
      prioritized.add(pair.column_1);
      prioritized.add(pair.column_2);
    }
    for (const col of numeric_columns) {
      if (prioritized.size >= MAX_DEFAULT_COLS) break;
      prioritized.add(col);
    }
    return Array.from(prioritized);
  }, [numeric_columns, high_correlation_pairs, isLargeMatrix, showAll]);

  if (!numeric_columns || numeric_columns.length < 2) {
    return (
      <div className="flex h-48 flex-col items-center justify-center rounded-2xl border border-white/5 bg-white/[0.02] text-center p-6">
        <p className="text-sm font-medium text-white/50">Insufficient numeric columns for correlation matrix</p>
        <p className="text-xs text-white/30 mt-1">Correlation requires at least 2 numerical features in the dataset.</p>
      </div>
    );
  }

  // Color mapping helper for Pearson r (-1.0 to 1.0)
  const getCellColor = (val: number) => {
    if (val === 1.0) return "bg-white/10 text-white/40"; // Self-correlation
    const absVal = Math.abs(val);
    if (absVal >= 0.85) return "bg-violet-600/90 text-white font-bold border border-violet-400/50 shadow-lg shadow-violet-500/30";
    if (absVal >= 0.6) return "bg-indigo-600/70 text-indigo-100 font-medium";
    if (absVal >= 0.3) return "bg-indigo-950/60 text-indigo-200/80";
    return "bg-white/[0.03] text-white/40";
  };

  return (
    <div className="space-y-4">
      {/* Header & Multicollinearity alert */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-white">Pearson Correlation Matrix</h3>
          <p className="text-xs text-white/40">
            Pairwise linear correlation coefficients (|r| &ge; 0.85 highlighted)
            {isLargeMatrix && !showAll && ` · Showing top ${displayCols.length} of ${numeric_columns.length} numeric columns`}
          </p>
        </div>

        <div className="flex items-center gap-3">
          {high_correlation_pairs.length > 0 && (
            <div className="flex items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs text-amber-300">
              <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse" />
              <span>{high_correlation_pairs.length} highly correlated pair(s)</span>
            </div>
          )}

          {isLargeMatrix && (
            <button
              onClick={() => setShowAll(!showAll)}
              className="rounded-xl border border-violet-500/30 bg-violet-500/10 px-3 py-1.5 text-xs font-semibold text-violet-300 hover:bg-violet-500/20 transition-all"
            >
              {showAll ? `Show Top ${MAX_DEFAULT_COLS}` : `Show All ${numeric_columns.length} Columns`}
            </button>
          )}
        </div>
      </div>

      {/* Heatmap Grid */}
      <div className="overflow-x-auto max-h-[500px] overflow-y-auto rounded-2xl border border-white/10 bg-white/[0.02] p-4 backdrop-blur-md">
        <div className="min-w-[400px]">
          {/* Header Row */}
          <div className="grid gap-1.5" style={{ gridTemplateColumns: `110px repeat(${displayCols.length}, minmax(55px, 1fr))` }}>
            <div className="text-[10px] font-bold uppercase tracking-wider text-white/30 truncate flex items-center">
              Features
            </div>
            {displayCols.map((col) => (
              <div key={col} className="text-center text-[11px] font-mono font-medium text-violet-300/80 truncate px-1" title={col}>
                {col}
              </div>
            ))}
          </div>

          {/* Matrix Rows */}
          {displayCols.map((rowCol) => (
            <div
              key={rowCol}
              className="grid gap-1.5 mt-1.5"
              style={{ gridTemplateColumns: `110px repeat(${displayCols.length}, minmax(55px, 1fr))` }}
            >
              {/* Row Header */}
              <div className="text-[11px] font-mono font-medium text-violet-300/80 truncate flex items-center px-1" title={rowCol}>
                {rowCol}
              </div>

              {/* Cells */}
              {displayCols.map((colCol) => {
                const val = matrix[rowCol]?.[colCol] ?? 0.0;
                return (
                  <div
                    key={colCol}
                    onMouseEnter={() => setHoveredCell({ c1: rowCol, c2: colCol, val })}
                    onMouseLeave={() => setHoveredCell(null)}
                    className={`flex h-9 items-center justify-center rounded-lg text-[11px] font-mono transition-all duration-150 cursor-pointer ${getCellColor(val)}`}
                    title={`${rowCol} vs ${colCol}: r = ${val}`}
                  >
                    {val.toFixed(2)}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Hover Info Footer */}
      <div className="h-6 flex items-center px-2 text-xs text-white/50">
        {hoveredCell ? (
          <span>
            Correlation between <strong className="text-violet-300">{hoveredCell.c1}</strong> and <strong className="text-violet-300">{hoveredCell.c2}</strong>: <span className="font-mono font-bold text-white">r = {hoveredCell.val}</span>
          </span>
        ) : (
          <span className="text-white/30">Hover over any matrix cell to view feature pair details</span>
        )}
      </div>
    </div>
  );
}
