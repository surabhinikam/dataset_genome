/**
 * Sidebar.tsx — Left Navigation Sidebar for Dataset Genome AI SaaS Platform.
 */

"use client";

import React from "react";
import {
  LayoutDashboard,
  Database,
  GitMerge,
  FlaskConical,
  BrainCircuit,
  Share2,
  BarChart3,
  FileText,
  Settings,
  Sparkles,
  LucideIcon,
} from "lucide-react";

export type NavTab =
  | "dashboard"
  | "datasets"
  | "pipeline"
  | "experiments"
  | "models"
  | "publications"
  | "analytics"
  | "reports"
  | "settings";

interface NavItem {
  id: NavTab;
  label: string;
  icon: LucideIcon;
  badge?: string;
}

interface SidebarProps {
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const navItems: NavItem[] = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "datasets", label: "Datasets", icon: Database, badge: "9" },
    { id: "pipeline", label: "Pipeline", icon: GitMerge, badge: "Active" },
    { id: "experiments", label: "Experiments", icon: FlaskConical },
    { id: "models", label: "Models", icon: BrainCircuit, badge: "v1.0" },
    { id: "publications", label: "Publications", icon: Share2 },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "reports", label: "Reports", icon: FileText },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#0B1220] border-r border-[#1F2937] flex flex-col h-screen sticky top-0 z-30 select-none">
      {/* Brand Logo */}
      <div className="h-16 flex items-center gap-3 px-6 border-b border-[#1F2937]">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#3B82F6] to-[#8B5CF6] flex items-center justify-center shadow-lg shadow-blue-500/20">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div className="flex flex-col">
          <span className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
            Dataset Genome
            <span className="text-[10px] px-1.5 py-0.5 rounded font-mono bg-[#3B82F6]/10 text-[#3B82F6] border border-[#3B82F6]/20">
              v2.0
            </span>
          </span>
          <span className="text-[11px] text-gray-400 font-medium">
            AI Dataset Intelligence
          </span>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 py-6 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
          Platform Menu
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? "bg-[#1F2937] text-white shadow-sm border border-[#374151]/50"
                  : "text-gray-400 hover:text-gray-200 hover:bg-[#111827]"
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={`w-4 h-4 transition-colors ${
                    isActive ? "text-[#3B82F6]" : "text-gray-400"
                  }`}
                />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-semibold ${
                    item.badge === "Active"
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 animate-pulse"
                      : "bg-gray-800 text-gray-400 border border-gray-700"
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer System Status */}
      <div className="p-4 border-t border-[#1F2937] bg-[#111827]/50">
        <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
          <span className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            Ecosystem Connected
          </span>
          <span className="font-mono text-gray-500 text-[10px]">99.9% UP</span>
        </div>
        <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
          <div className="bg-gradient-to-r from-blue-500 to-violet-500 h-full w-[88%]" />
        </div>
      </div>
    </aside>
  );
};
