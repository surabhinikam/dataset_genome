"use client";

import React, { useState } from "react";
import { Search, Sliders, Dna, Database, Terminal, ShieldCheck, Activity } from "lucide-react";
import { DatasetSpecimen } from "@/lib/mock-genome-data";

interface LocusHeaderProps {
  activeSpecimen: DatasetSpecimen;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onToggleSidebar: () => void;
  isSidebarOpen: boolean;
  totalSpecimens: number;
}

export const LocusHeader: React.FC<LocusHeaderProps> = ({
  activeSpecimen,
  searchQuery,
  onSearchChange,
  onToggleSidebar,
  isSidebarOpen,
  totalSpecimens,
}) => {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopyLocus = () => {
    navigator.clipboard.writeText(activeSpecimen.locusPath);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <header className="h-14 bg-[#FFFFFF] border-b border-[#14171A]/10 px-4 flex items-center justify-between gap-4 sticky top-0 z-30 shadow-xs select-none">
      {/* Left: Brand & Locus Coordinate */}
      <div className="flex items-center gap-3 overflow-hidden">
        <button
          onClick={onToggleSidebar}
          title="Toggle Registry Sidebar"
          className="p-1.5 rounded-md hover:bg-[#EEF2EF] text-[#0F6B5C] transition-colors focus:ring-2 focus:ring-[#0F6B5C]"
          aria-label="Toggle Registry"
        >
          <Dna className="w-5 h-5 animate-pulse" />
        </button>

        <div className="flex items-center gap-2 border-l border-[#14171A]/10 pl-3">
          <span className="font-mono-display font-bold text-xs uppercase tracking-wider text-[#0F6B5C] hidden sm:inline-block">
            GENOME//
          </span>

          {/* Locus Coordinate Pill */}
          <button
            onClick={handleCopyLocus}
            title="Click to copy locus coordinate"
            className="flex items-center gap-2 px-2.5 py-1 rounded bg-[#EEF2EF] hover:bg-[#0F6B5C]/10 border border-[#14171A]/10 transition-colors font-mono-data text-xs text-[#14171A] group"
          >
            <span className="w-2 h-2 rounded-full bg-[#3FA66D] animate-ping" />
            <span className="truncate max-w-[260px] sm:max-w-[400px] font-medium">
              {activeSpecimen.locusPath}
            </span>
            <span className="text-[10px] text-[#0F6B5C] font-mono-display opacity-0 group-hover:opacity-100 transition-opacity">
              {isCopied ? "COPIED!" : "COPY"}
            </span>
          </button>
        </div>
      </div>

      {/* Center: Search input */}
      <div className="flex-1 max-w-md hidden md:block">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#14171A]/40" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search specimen by locus, tag, or schema field..."
            className="w-full bg-[#EEF2EF]/70 focus:bg-[#FFFFFF] border border-[#14171A]/10 focus:border-[#0F6B5C] rounded-md pl-9 pr-12 py-1.5 text-xs font-sans text-[#14171A] outline-hidden transition-all placeholder:text-[#14171A]/40 font-mono-data"
          />
          <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 px-1.5 py-0.5 rounded bg-[#FFFFFF] border border-[#14171A]/15 font-mono-data text-[10px] text-[#14171A]/50">
            /
          </kbd>
        </div>
      </div>

      {/* Right: Instrument status indicators */}
      <div className="flex items-center gap-3 font-mono-data text-xs">
        <div className="hidden lg:flex items-center gap-2 px-2.5 py-1 rounded bg-[#EEF2EF] border border-[#14171A]/08 text-[#14171A]/70">
          <Activity className="w-3.5 h-3.5 text-[#0F6B5C]" />
          <span>SPECIMENS: <strong className="text-[#14171A]">{totalSpecimens}</strong></span>
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#3FA66D]/10 border border-[#3FA66D]/30 text-[#3FA66D] font-medium">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span className="text-[11px] font-mono-display">HEALTH: {activeSpecimen.healthScore}%</span>
        </div>

        <button
          className="p-1.5 rounded-md hover:bg-[#EEF2EF] text-[#14171A]/60 hover:text-[#14171A] transition-colors"
          title="Instrument Settings"
        >
          <Sliders className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
