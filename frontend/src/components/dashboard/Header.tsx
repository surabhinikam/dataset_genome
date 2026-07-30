/**
 * Header.tsx — Top Header Bar for Dataset Genome AI SaaS Platform.
 */

"use client";

import React, { useState } from "react";
import {
  Search,
  Bell,
  Play,
  ChevronDown,
  Layers,
  Sparkles,
  Command,
} from "lucide-react";

interface HeaderProps {
  onRunPipeline: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onRunPipeline }) => {
  const [workspace, setWorkspace] = useState("Production ML Workspace");
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <header className="h-16 bg-[#0B1220] border-b border-[#1F2937] px-8 flex items-center justify-between sticky top-0 z-20">
      {/* Workspace Selector & Search */}
      <div className="flex items-center gap-6">
        {/* Workspace Dropdown */}
        <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#111827] border border-[#1F2937] hover:border-gray-700 text-xs font-medium text-gray-200 transition-colors">
          <Layers className="w-4 h-4 text-[#3B82F6]" />
          <span>{workspace}</span>
          <ChevronDown className="w-3.5 h-3.5 text-gray-400 ml-1" />
        </button>

        {/* Global Search */}
        <div className="relative w-80">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search datasets, pipelines, models..."
            className="w-full bg-[#111827] border border-[#1F2937] rounded-lg pl-9 pr-12 py-1.5 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-[#3B82F6] transition-all"
          />
          <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-0.5 text-[10px] text-gray-500 bg-gray-800 px-1.5 py-0.5 rounded font-mono border border-gray-700">
            <Command className="w-2.5 h-2.5" /> /
          </div>
        </div>
      </div>

      {/* Actions & Controls */}
      <div className="flex items-center gap-4">
        {/* Run Pipeline CTA */}
        <button
          onClick={onRunPipeline}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#3B82F6] hover:bg-[#2563EB] text-white text-xs font-semibold shadow-lg shadow-blue-500/25 transition-all duration-150 active:scale-95"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>Run Pipeline</span>
        </button>

        {/* Notification Bell */}
        <button className="relative p-2 text-gray-400 hover:text-gray-200 hover:bg-[#111827] rounded-lg transition-colors border border-transparent hover:border-[#1F2937]">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-emerald-500 rounded-full" />
        </button>

        {/* User Profile Avatar */}
        <div className="flex items-center gap-3 pl-2 border-l border-[#1F2937]">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-violet-600 to-indigo-600 flex items-center justify-center font-bold text-xs text-white shadow-inner">
            SN
          </div>
          <div className="hidden md:flex flex-col text-left">
            <span className="text-xs font-medium text-gray-200 leading-tight">
              Surabhi Nikam
            </span>
            <span className="text-[10px] text-gray-400 leading-tight">
              Lead ML Engineer
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
