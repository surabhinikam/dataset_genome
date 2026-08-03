"""
backend/app/pipeline/job_engine.py — Execution Engine, Logging & Live Dashboard Integration.

Manages pipeline run execution state, run history persistence, structured log recording,
and live JSON updates for frontend dashboard visualization.
"""

import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("dataset_genome.pipeline.job_engine")


class RunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"


class PipelineStage(str, Enum):
    IDLE = "Idle"
    GENERATE_BENCHMARK = "Generate Benchmark"
    VALIDATE = "Validate"
    DATASET_INTELLIGENCE = "Dataset Intelligence"
    QUALITY_ANALYSIS = "Quality Analysis"
    ADAPTIVE_DATA = "Adaptive Data"
    AUTOSCIENTIST = "AutoScientist"
    EVALUATION = "Evaluation"
    PUBLICATION = "Publication"
    HUGGINGFACE_PACKAGING = "Hugging Face Packaging"
    KAGGLE_PACKAGING = "Kaggle Packaging"
    DASHBOARD_REFRESH = "Dashboard Refresh"


class PipelineRun:
    """Represents a single pipeline execution job instance."""

    def __init__(self, run_id: Optional[str] = None, version_tag: str = "v1.0") -> None:
        self.run_id = run_id or f"run-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        self.version_tag = version_tag
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.duration_seconds: float = 0.0
        self.status = RunStatus.PENDING
        self.current_stage = PipelineStage.IDLE
        self.progress_pct: float = 0.0
        self.samples_generated: int = 0
        self.quality_score: float = 0.0
        self.adaptive_score: float = 0.0
        self.logs: List[Dict[str, Any]] = []

    def update_stage(self, stage: PipelineStage, progress_pct: float, message: str = "") -> None:
        """Update current stage and progress percentage."""
        self.current_stage = stage
        self.progress_pct = round(progress_pct, 2)
        if message:
            self.add_log(message, stage=stage.value)
        logger.info(f"[{self.run_id}] Stage: {stage.value} ({progress_pct:.1f}%) - {message}")

    def add_log(self, message: str, level: str = "INFO", stage: Optional[str] = None) -> None:
        """Record structured log entry."""
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "datetime": datetime.utcnow().isoformat(),
            "level": level,
            "stage": stage or self.current_stage.value,
            "message": message,
        }
        self.logs.append(entry)

    def complete(self, samples_generated: int = 0, quality_score: float = 0.0, adaptive_score: float = 0.0) -> None:
        """Mark run as successfully completed."""
        self.end_time = datetime.utcnow()
        self.duration_seconds = round((self.end_time - self.start_time).total_seconds(), 2)
        self.status = RunStatus.COMPLETED
        self.current_stage = PipelineStage.DASHBOARD_REFRESH
        self.progress_pct = 100.0
        self.samples_generated = samples_generated
        self.quality_score = quality_score
        self.adaptive_score = adaptive_score
        self.add_log("Pipeline run completed successfully.", level="SUCCESS")

    def fail(self, error_message: str) -> None:
        """Mark run as failed."""
        self.end_time = datetime.utcnow()
        self.duration_seconds = round((self.end_time - self.start_time).total_seconds(), 2)
        self.status = RunStatus.FAILED
        self.add_log(f"Pipeline execution failed: {error_message}", level="ERROR")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize run telemetry for persistence."""
        return {
            "run_id": self.run_id,
            "version_tag": self.version_tag,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "status": self.status.value,
            "current_stage": self.current_stage.value,
            "progress_pct": self.progress_pct,
            "samples_generated": self.samples_generated,
            "quality_score": self.quality_score,
            "adaptive_score": self.adaptive_score,
            "total_logs": len(self.logs),
        }


class JobExecutionEngine:
    """
    Manages run history, log persistence, and live dashboard JSON status updates.
    """

    def __init__(self, storage_dir: Optional[Union[str, Path]] = None) -> None:
        self.storage_dir = Path(storage_dir) if storage_dir else Path(r"c:\Users\surab\OneDrive\Documents\DATASET GENOME\dataset_genome\export_benchmark")
        self.runs_dir = self.storage_dir / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.runs_dir / "run_history.json"
        self.live_status_file = self.storage_dir / "live_pipeline_status.json"

    def save_run(self, run: PipelineRun) -> None:
        """Persist run log file and update master run history."""
        # 1. Write run-specific log file
        log_file = self.runs_dir / f"{run.run_id}_logs.json"
        log_payload = {
            "run_info": run.to_dict(),
            "logs": run.logs,
        }
        log_file.write_text(json.dumps(log_payload, indent=2, ensure_ascii=False), encoding="utf-8")

        # 2. Append to history list
        history = self.get_history()
        # Replace if exists, else append
        history = [r for r in history if r["run_id"] != run.run_id]
        history.append(run.to_dict())
        self.history_file.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_history(self) -> List[Dict[str, Any]]:
        """Retrieve stored run history."""
        if not self.history_file.exists():
            return []
        try:
            return json.loads(self.history_file.read_text(encoding="utf-8"))
        except Exception:
            return []

    def update_live_status(
        self,
        run: PipelineRun,
        validation_progress: str = "100%",
        autoscientist_progress: str = "Complete",
        publication_status: str = "Ready",
        hf_status: str = "Packaged",
        kaggle_status: str = "Packaged",
    ) -> Dict[str, Any]:
        """Expose real-time live status payload to frontend dashboard."""
        status_payload = {
            "run_id": run.run_id,
            "current_stage": run.current_stage.value,
            "status": run.status.value,
            "progress_pct": run.progress_pct,
            "samples_generated": run.samples_generated,
            "validation_progress": validation_progress,
            "quality_score": run.quality_score,
            "adaptive_score": run.adaptive_score,
            "autoscientist_progress": autoscientist_progress,
            "publication_status": publication_status,
            "huggingface_status": hf_status,
            "kaggle_status": kaggle_status,
            "updated_at": datetime.utcnow().isoformat(),
            "recent_logs": run.logs[-5:] if run.logs else [],
        }

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.live_status_file.write_text(json.dumps(status_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return status_payload
