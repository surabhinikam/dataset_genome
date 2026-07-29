"use client";

import React, { useState, useMemo } from "react";
import { MOCK_SPECIMENS, MOCK_LINEAGE_RUNGS, DatasetSpecimen } from "@/lib/mock-genome-data";
import { LocusHeader } from "./LocusHeader";
import { RegistrySidebar } from "./RegistrySidebar";
import { LineageLadder } from "./LineageLadder";
import { DatasetInspector } from "./DatasetInspector";

export const LineageBrowserDashboard: React.FC = () => {
  const [selectedSpecimenId, setSelectedSpecimenId] = useState<string>("customers");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [isInspectorOpen, setIsInspectorOpen] = useState<boolean>(true);

  const specimenList = useMemo(() => Object.values(MOCK_SPECIMENS), []);
  const activeSpecimen = MOCK_SPECIMENS[selectedSpecimenId] || MOCK_SPECIMENS["customers"];

  // Helper to trace full parent ancestry path IDs
  const tracedPathIds = useMemo(() => {
    const ids = new Set<string>();
    const stack = [selectedSpecimenId];

    while (stack.length > 0) {
      const currentId = stack.pop()!;
      if (!ids.has(currentId)) {
        ids.add(currentId);
        const spec = MOCK_SPECIMENS[currentId];
        if (spec && spec.parentIds) {
          stack.push(...spec.parentIds);
        }
      }
    }
    return Array.from(ids);
  }, [selectedSpecimenId]);

  const handleSelectSpecimen = (id: string) => {
    setSelectedSpecimenId(id);
    setIsInspectorOpen(true);
  };

  const handleTraceLineage = (id: string) => {
    setSelectedSpecimenId(id);
    setIsInspectorOpen(true);
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-[#EEF2EF] overflow-hidden select-none">
      {/* Top Locus Coordinate Bar */}
      <LocusHeader
        activeSpecimen={activeSpecimen}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
        isSidebarOpen={isSidebarOpen}
        totalSpecimens={specimenList.length}
      />

      {/* Main Three-Column Workspace */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Column: Specimen Registry Sidebar */}
        <RegistrySidebar
          specimens={specimenList}
          selectedSpecimenId={selectedSpecimenId}
          onSelectSpecimen={handleSelectSpecimen}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          isOpen={isSidebarOpen}
          onToggleOpen={() => setIsSidebarOpen((prev) => !prev)}
        />

        {/* Center Column: The Lineage Ladder (Hero Canvas) */}
        <LineageLadder
          specimens={MOCK_SPECIMENS}
          rungs={MOCK_LINEAGE_RUNGS}
          selectedSpecimenId={selectedSpecimenId}
          onSelectSpecimen={handleSelectSpecimen}
          tracedPathIds={tracedPathIds}
        />

        {/* Right Column: Dataset Inspector Panel */}
        {isInspectorOpen && (
          <DatasetInspector
            specimen={activeSpecimen}
            onClose={() => setIsInspectorOpen(false)}
            onTraceLineage={handleTraceLineage}
          />
        )}
      </div>
    </div>
  );
};
