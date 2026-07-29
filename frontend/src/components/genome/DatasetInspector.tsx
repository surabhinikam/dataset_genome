"use client";

import React, { useState } from "react";
import { DatasetSpecimen, OPERATION_COLOR_MAP } from "@/lib/mock-genome-data";
import { SangerChromatogram } from "./SangerChromatogram";
import { X, GitBranch, History, Table, Terminal, FileCode, CheckCircle2, AlertTriangle, ArrowRight, Share2, Download } from "lucide-react";

interface DatasetInspectorProps {
  specimen: DatasetSpecimen | null;
  onClose: () => void;
  onTraceLineage: (id: string) => void;
}

export const DatasetInspector: React.FC<DatasetInspectorProps> = ({
  specimen,
  onClose,
  onTraceLineage,
}) => {
  const [activeTab, setActiveTab] = useState<"trace" | "schema" | "history">("trace");

  if (!specimen) return null;

  const eventInfo = specimen.derivationEvent;
  const opMeta = eventInfo ? OPERATION_COLOR_MAP[eventInfo.operation] : null;

  return (
    <div className="w-full md:w-[450px] bg-[#FFFFFF] border-l border-[#14171A]/10 flex flex-col h-full z-20 shrink-0 shadow-lg select-none">
      {/* Inspector Top Header */}
      <div className="p-3.5 border-b border-[#14171A]/10 flex items-center justify-between bg-[#EEF2EF]/50">
        <div className="flex items-center gap-2 overflow-hidden">
          <span className="w-2.5 h-2.5 rounded-full bg-[#0F6B5C] animate-pulse" />
          <span className="font-mono-display font-bold text-xs uppercase tracking-wider text-[#14171A] truncate">
            SPECIMEN INSPECTOR
          </span>
        </div>

        <button
          onClick={onClose}
          className="p-1 rounded text-[#14171A]/50 hover:text-[#14171A] hover:bg-[#EEF2EF] transition-colors"
          title="Close Inspector"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Specimen Header Meta */}
      <div className="p-4 border-b border-[#14171A]/10 bg-[#FFFFFF]">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="font-mono-display font-bold text-base text-[#14171A]">
              {specimen.name}
            </h3>
            <div className="font-mono-data text-xs text-[#0F6B5C] font-semibold mt-0.5">
              {specimen.locusPath}
            </div>
          </div>
          <span className="font-mono-data text-xs px-2 py-0.5 rounded bg-[#EEF2EF] border border-[#14171A]/10 text-[#14171A]/80 font-bold">
            {specimen.version}
          </span>
        </div>

        <p className="font-sans text-xs text-[#14171A]/70 mt-2.5 leading-relaxed">
          {specimen.description}
        </p>

        {/* Quick Specimen Metrics Grid */}
        <div className="grid grid-cols-3 gap-2 mt-3 font-mono-data text-xs">
          <div className="p-2 rounded bg-[#EEF2EF]/60 border border-[#14171A]/06">
            <span className="text-[10px] text-[#14171A]/50 uppercase block">Rows</span>
            <span className="font-bold text-[#14171A]">{specimen.rowCount.toLocaleString()}</span>
          </div>
          <div className="p-2 rounded bg-[#EEF2EF]/60 border border-[#14171A]/06">
            <span className="text-[10px] text-[#14171A]/50 uppercase block">Cols</span>
            <span className="font-bold text-[#14171A]">{specimen.columnCount}</span>
          </div>
          <div className="p-2 rounded bg-[#EEF2EF]/60 border border-[#14171A]/06">
            <span className="text-[10px] text-[#14171A]/50 uppercase block">Health</span>
            <span className="font-bold text-[#3FA66D]">{specimen.healthScore}%</span>
          </div>
        </div>

        {/* Derivation Rung Event Summary */}
        {eventInfo && opMeta && (
          <div
            className="mt-3 p-2.5 rounded border text-xs font-mono-data flex items-start gap-2"
            style={{
              backgroundColor: `${opMeta.hex}10`,
              borderColor: `${opMeta.hex}40`,
              color: opMeta.hex,
            }}
          >
            <GitBranch className="w-4 h-4 mt-0.5 shrink-0" />
            <div>
              <div className="font-bold flex items-center gap-1">
                <span>DERIVED VIA [{eventInfo.operation}]</span>
                <span className="text-[10px] opacity-80">({eventInfo.operator})</span>
              </div>
              <p className="text-[11px] opacity-90 font-sans mt-0.5">{eventInfo.description}</p>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-[#14171A]/10 bg-[#EEF2EF]/30 font-mono-data text-xs">
        <button
          onClick={() => setActiveTab("trace")}
          className={`flex-1 py-2.5 px-3 flex items-center justify-center gap-1.5 border-b-2 font-medium transition-colors ${
            activeTab === "trace"
              ? "border-[#0F6B5C] text-[#0F6B5C] bg-[#FFFFFF]"
              : "border-transparent text-[#14171A]/60 hover:text-[#14171A]"
          }`}
        >
          <Table className="w-3.5 h-3.5" />
          <span>Quality Trace</span>
        </button>

        <button
          onClick={() => setActiveTab("schema")}
          className={`flex-1 py-2.5 px-3 flex items-center justify-center gap-1.5 border-b-2 font-medium transition-colors ${
            activeTab === "schema"
              ? "border-[#0F6B5C] text-[#0F6B5C] bg-[#FFFFFF]"
              : "border-transparent text-[#14171A]/60 hover:text-[#14171A]"
          }`}
        >
          <FileCode className="w-3.5 h-3.5" />
          <span>Schema ({specimen.schema.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("history")}
          className={`flex-1 py-2.5 px-3 flex items-center justify-center gap-1.5 border-b-2 font-medium transition-colors ${
            activeTab === "history"
              ? "border-[#0F6B5C] text-[#0F6B5C] bg-[#FFFFFF]"
              : "border-transparent text-[#14171A]/60 hover:text-[#14171A]"
          }`}
        >
          <History className="w-3.5 h-3.5" />
          <span>Commits ({specimen.versionHistory.length})</span>
        </button>
      </div>

      {/* Tab Contents */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {activeTab === "trace" && (
          <div className="space-y-4">
            <SangerChromatogram specimen={specimen} />

            {/* Specimen Metadata Box */}
            <div className="bg-[#FFFFFF] border border-[#14171A]/10 rounded-md p-3 font-mono-data text-xs space-y-2">
              <div className="font-mono-display font-bold text-xs text-[#14171A]">SPECIMEN ORIGIN METADATA</div>
              <div className="flex justify-between text-[#14171A]/70">
                <span>Owner:</span>
                <span className="font-semibold text-[#14171A]">{specimen.owner}</span>
              </div>
              <div className="flex justify-between text-[#14171A]/70">
                <span>Size:</span>
                <span className="font-semibold text-[#14171A]">{(specimen.sizeBytes / 1024 / 1024).toFixed(1)} MB</span>
              </div>
              <div className="flex justify-between text-[#14171A]/70">
                <span>Last Updated:</span>
                <span className="font-semibold text-[#14171A]">{new Date(specimen.lastUpdated).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === "schema" && (
          <div className="space-y-3">
            <div className="font-mono-display text-xs font-bold text-[#14171A] flex items-center justify-between">
              <span>FIELD SCHEMA SPECIFICATION</span>
              <span className="font-mono-data text-[10px] text-[#0F6B5C]">MONOSPACE VIEW</span>
            </div>

            <div className="border border-[#14171A]/10 rounded-md overflow-hidden bg-[#FFFFFF] font-mono-data text-[11px]">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-[#EEF2EF] border-b border-[#14171A]/10 text-[#14171A]/70 font-semibold">
                    <th className="p-2">Field</th>
                    <th className="p-2">Type</th>
                    <th className="p-2 text-right">Null %</th>
                    <th className="p-2 text-center">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#14171A]/06">
                  {specimen.schema.map((field) => (
                    <tr key={field.name} className="hover:bg-[#EEF2EF]/40">
                      <td className="p-2 font-bold text-[#14171A]">{field.name}</td>
                      <td className="p-2 text-[#0F6B5C]">{field.type}</td>
                      <td className="p-2 text-right">{field.nullPercentage.toFixed(1)}%</td>
                      <td className="p-2 text-center">
                        {field.qualityStatus === "optimal" ? (
                          <span className="inline-block w-2 h-2 rounded-full bg-[#3FA66D]" title="Optimal" />
                        ) : (
                          <span className="inline-block w-2 h-2 rounded-full bg-[#D98F3F]" title="Warn" />
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === "history" && (
          <div className="space-y-3">
            <div className="font-mono-display text-xs font-bold text-[#14171A]">VERSION COMMIT TIMELINE</div>

            <div className="space-y-3 relative pl-4 border-l-2 border-[#0F6B5C]/30 font-mono-data text-xs">
              {specimen.versionHistory.map((commit, idx) => (
                <div key={idx} className="relative">
                  {/* Timeline Node Bullet */}
                  <span className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-[#0F6B5C] border-2 border-[#FFFFFF]" />

                  <div className="bg-[#FFFFFF] border border-[#14171A]/10 rounded-md p-2.5 space-y-1">
                    <div className="flex items-center justify-between font-bold text-[#14171A]">
                      <span>{commit.version}</span>
                      <span className="text-[10px] text-[#14171A]/40 font-normal">#{commit.commitHash}</span>
                    </div>
                    <p className="font-sans text-[11px] text-[#14171A]/80">{commit.message}</p>
                    <div className="flex items-center justify-between text-[10px] text-[#14171A]/50 pt-1">
                      <span>By {commit.author}</span>
                      <span>{commit.timestamp}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Inspector Bottom Action Buttons (Plain engineer copy) */}
      <div className="p-3 border-t border-[#14171A]/10 bg-[#EEF2EF]/50 flex items-center gap-2">
        <button
          onClick={() => onTraceLineage(specimen.id)}
          className="flex-1 py-2 px-3 rounded bg-[#0F6B5C] hover:bg-[#0F6B5C]/90 text-[#FFFFFF] font-mono-data text-xs font-medium flex items-center justify-center gap-1.5 transition-colors focus:ring-2 focus:ring-[#0F6B5C]"
        >
          <GitBranch className="w-3.5 h-3.5" />
          <span>Trace lineage</span>
        </button>

        <button
          className="py-2 px-3 rounded bg-[#FFFFFF] hover:bg-[#EEF2EF] border border-[#14171A]/15 text-[#14171A] font-mono-data text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
          title="Compare with parent specimen"
        >
          <Share2 className="w-3.5 h-3.5 text-[#14171A]/60" />
          <span>Compare</span>
        </button>
      </div>
    </div>
  );
};
