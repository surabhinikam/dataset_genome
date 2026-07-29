"""
services/autoscientist/timeline_generator.py — Frontend Timeline Event Generator.

Transforms NotebookEntry objects into frontend-ready TimelineEvent objects with color tokens,
icons, and formatted summary payloads suitable for direct rendering in UI components.
"""

from typing import Dict, List
from services.autoscientist.research_models import NotebookEntry, NotebookStage, TimelineEvent


class TimelineGenerator:
    """
    Generator for converting scientific notebook entries into frontend timeline event schemas.
    """

    STAGE_ICON_MAP: Dict[NotebookStage, str] = {
        NotebookStage.OBSERVATION: "microscope",
        NotebookStage.RANKING: "filter",
        NotebookStage.REASONING: "brain",
        NotebookStage.HYPOTHESIS: "flask",
        NotebookStage.PLANNING: "clipboard-list",
        NotebookStage.EXECUTION: "play",
        NotebookStage.EVALUATION: "check-circle",
        NotebookStage.LESSONS_LEARNED: "bookmark",
    }

    STAGE_COLOR_MAP: Dict[NotebookStage, str] = {
        NotebookStage.OBSERVATION: "#3B82F6",      # Blue
        NotebookStage.RANKING: "#8B5CF6",          # Purple
        NotebookStage.REASONING: "#EC4899",        # Pink
        NotebookStage.HYPOTHESIS: "#F59E0B",       # Amber
        NotebookStage.PLANNING: "#10B981",         # Emerald
        NotebookStage.EXECUTION: "#06B6D4",        # Cyan
        NotebookStage.EVALUATION: "#10B981",       # Emerald
        NotebookStage.LESSONS_LEARNED: "#6366F1",   # Indigo
    }

    @classmethod
    def generate_timeline(cls, entries: List[NotebookEntry]) -> List[TimelineEvent]:
        """
        Transform a list of NotebookEntry objects into a ordered list of TimelineEvent objects.
        """
        events: List[TimelineEvent] = []

        for idx, entry in enumerate(entries, start=1):
            icon = cls.STAGE_ICON_MAP.get(entry.stage, "activity")
            color = entry.ui_color or cls.STAGE_COLOR_MAP.get(entry.stage, "#6B7280")

            summary = entry.reasoning or f"Completed {entry.stage_title}"
            if len(summary) > 120:
                summary = summary[:117] + "..."

            event = TimelineEvent(
                event_id=f"evt-{idx}-{entry.entry_id}",
                stage_name=entry.stage.value,
                label=entry.stage_title,
                summary=summary,
                timestamp=entry.timestamp,
                status=entry.status,
                color=color,
                icon=icon,
                details={
                    "entry_id": entry.entry_id,
                    "confidence": entry.confidence,
                    "metrics": entry.metrics,
                    "dataset_version": entry.dataset_version,
                    "experiment_version": entry.experiment_version,
                    "artifacts": entry.artifacts,
                    "inputs": entry.inputs,
                    "outputs": entry.outputs,
                },
            )
            events.append(event)

        return events
