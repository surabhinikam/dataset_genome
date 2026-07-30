/**
 * app/page.tsx — Dataset Genome AI SaaS Dashboard Root Container.
 */

"use client";

import React, { useState } from "react";
import { Sidebar, NavTab } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { RunPipelineModal } from "@/components/dashboard/RunPipelineModal";

import { DashboardHome } from "@/components/dashboard/views/DashboardHome";
import { DatasetsView } from "@/components/dashboard/views/DatasetsView";
import { PipelineView } from "@/components/dashboard/views/PipelineView";
import { ExperimentsView } from "@/components/dashboard/views/ExperimentsView";
import { ModelsView } from "@/components/dashboard/views/ModelsView";
import { PublicationsView } from "@/components/dashboard/views/PublicationsView";
import { AnalyticsView } from "@/components/dashboard/views/AnalyticsView";
import { ReportsView } from "@/components/dashboard/views/ReportsView";
import { SettingsView } from "@/components/dashboard/views/SettingsView";

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<NavTab>("dashboard");
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0B1220] text-[#F9FAFB]">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-y-auto">
        <Header onRunPipeline={() => setIsModalOpen(true)} />

        <main className="flex-1 pb-16">
          {activeTab === "dashboard" && <DashboardHome onRunPipeline={() => setIsModalOpen(true)} />}
          {activeTab === "datasets" && <DatasetsView />}
          {activeTab === "pipeline" && <PipelineView />}
          {activeTab === "experiments" && <ExperimentsView />}
          {activeTab === "models" && <ModelsView />}
          {activeTab === "publications" && <PublicationsView />}
          {activeTab === "analytics" && <AnalyticsView />}
          {activeTab === "reports" && <ReportsView />}
          {activeTab === "settings" && <SettingsView />}
        </main>
      </div>

      {/* Interactive Run Pipeline Modal */}
      <RunPipelineModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}
