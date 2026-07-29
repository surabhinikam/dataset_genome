"use client";

import React, { useState } from "react";
import { DatasetSpecimen } from "@/lib/mock-genome-data";
import { Filter, Layers, ChevronLeft, ChevronRight, CheckCircle2, AlertTriangle, XCircle, Tag } from "lucide-react";

interface RegistrySidebarProps {
  specimens: DatasetSpecimen[];
  selectedSpecimenId: string;
  onSelectSpecimen: (id: string) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  isOpen: boolean;
  onToggleOpen: () => void;
}

export const RegistrySidebar: React.FC<RegistrySidebarProps> = ({
  specimens,
  selectedSpecimenId,
  onSelectSpecimen,
  searchQuery,
  onSearchChange,
  isOpen,
  onToggleOpen,
}) => {
  const [statusFilter, setStatusFilter] = useState<"all" | "healthy" | "warning" | "critical">("all");

  const filteredSpecimens = specimens.filter((s) => {
    const matchesSearch =
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.locusPath.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesStatus = statusFilter === "all" || s.healthStatus === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const formatRows = (rows: number) => {
    if (rows >= 1000000) return `${(rows / 1000000).toFixed(2)}M`;
    if (rows >= 1000) return `${(rows / 1000).toFixed(0)}K`;
    return rows.toString();
  };

  const getStatusDot = (status: DatasetSpecimen["healthStatus"]) => {
    switch (status) {
      case "healthy":
        return <span className="w-2 h-2 rounded-full bg-[#3FA66D] shadow-xs" title="Healthy specimen" />;
      case "warning":
        return <span className="w-2 h-2 rounded-full bg-[#D98F3F] shadow-xs animate-pulse" title="Warning" />;
      case "critical":
        return <span className="w-2 h-2 rounded-full bg-[#D64545] shadow-xs animate-ping" title="Critical anomaly" />;
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={onToggleOpen}
        className="hidden md:flex items-center gap-1 bg-[#FFFFFF] border-r border-y border-[#14171A]/10 p-2 text-[#14171A]/70 hover:text-[#0F6B5C] hover:bg-[#EEF2EF] transition-colors z-20 self-stretch my-auto rounded-r-md shadow-xs"
        title="Expand Registry Sidebar"
      >
        <Layers className="w-4 h-4" />
        <ChevronRight className="w-3.5 h-3.5" />
      </button>
    );
  }

  return (
    <aside className="w-full md:w-80 bg-[#FFFFFF] border-r border-[#14171A]/10 flex flex-col h-full z-20 shrink-0 select-none shadow-xs">
      {/* Sidebar Header */}
      <div className="p-3 border-b border-[#14171A]/10 flex items-center justify-between bg-[#EEF2EF]/40">
        <div className="flex items-center gap-2 font-mono-display text-xs font-bold text-[#14171A] tracking-wide">
          <Layers className="w-4 h-4 text-[#0F6B5C]" />
          <span>SPECIMEN REGISTRY</span>
          <span className="ml-1 px-1.5 py-0.2 rounded bg-[#0F6B5C]/10 text-[#0F6B5C] font-mono-data text-[10px]">
            {filteredSpecimens.length}
          </span>
        </div>

        <button
          onClick={onToggleOpen}
          className="p-1 text-[#14171A]/50 hover:text-[#14171A] rounded hover:bg-[#EEF2EF]"
          title="Collapse Registry"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="p-2 border-b border-[#14171A]/08 bg-[#FFFFFF] flex items-center gap-1 font-mono-data text-[11px]">
        <span className="text-[#14171A]/40 px-1">
          <Filter className="w-3 h-3" />
        </span>
        {(["all", "healthy", "warning", "critical"] as const).map((st) => (
          <button
            key={st}
            onClick={() => setStatusFilter(st)}
            className={`px-2 py-0.5 rounded capitalize transition-all ${
              statusFilter === st
                ? "bg-[#0F6B5C] text-[#FFFFFF] font-medium"
                : "text-[#14171A]/60 hover:bg-[#EEF2EF] hover:text-[#14171A]"
            }`}
          >
            {st}
          </button>
        ))}
      </div>

      {/* Specimen List */}
      <div className="flex-1 overflow-y-auto divide-y divide-[#14171A]/06">
        {filteredSpecimens.length === 0 ? (
          <div className="p-6 text-center text-xs font-sans text-[#14171A]/50">
            No specimen found matching query.
            <div className="mt-2 text-[11px] font-mono-data text-[#0F6B5C]">
              Connect a data source to begin tracing.
            </div>
          </div>
        ) : (
          filteredSpecimens.map((specimen) => {
            const isSelected = specimen.id === selectedSpecimenId;
            return (
              <button
                key={specimen.id}
                onClick={() => onSelectSpecimen(specimen.id)}
                className={`w-full text-left p-3 transition-all flex flex-col gap-1.5 group ${
                  isSelected
                    ? "bg-[#0F6B5C]/08 border-l-4 border-l-[#0F6B5C] pl-2.5"
                    : "hover:bg-[#EEF2EF]/60 border-l-4 border-l-transparent"
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    {getStatusDot(specimen.healthStatus)}
                    <span className="font-mono-display font-semibold text-xs text-[#14171A] group-hover:text-[#0F6B5C] truncate">
                      {specimen.name}
                    </span>
                  </div>
                  <span className="font-mono-data text-[10px] px-1.5 py-0.5 rounded bg-[#EEF2EF] text-[#14171A]/70 border border-[#14171A]/08">
                    {specimen.version}
                  </span>
                </div>

                <div className="flex items-center justify-between text-[11px] font-mono-data text-[#14171A]/60">
                  <span>{formatRows(specimen.rowCount)} rows • {specimen.columnCount} cols</span>
                  <span className="text-[10px] text-[#0F6B5C] font-semibold">{specimen.healthScore}% score</span>
                </div>

                {/* Tags */}
                <div className="flex items-center gap-1 flex-wrap">
                  {specimen.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-0.5 px-1.5 py-0.2 rounded text-[9px] font-mono-data bg-[#14171A]/04 text-[#14171A]/70 border border-[#14171A]/05"
                    >
                      <Tag className="w-2.5 h-2.5 text-[#0F6B5C]" />
                      {tag}
                    </span>
                  ))}
                </div>
              </button>
            );
          })
        )}
      </div>

      {/* Footer Info */}
      <div className="p-2.5 border-t border-[#14171A]/10 bg-[#EEF2EF]/50 font-mono-data text-[10px] text-[#14171A]/60 flex items-center justify-between">
        <span>BIOINFORMATICS DISCOVERY</span>
        <span className="text-[#0F6B5C] font-bold">DNA-v3.2</span>
      </div>
    </aside>
  );
};
