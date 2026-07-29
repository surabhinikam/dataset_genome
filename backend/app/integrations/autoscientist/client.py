"""
backend/app/integrations/autoscientist/client.py — MODULE 2: AutoScientist Client.

Provides an abstract interface and mock implementation for communication with AutoScientist.
Implements prepare(), submit(), monitor(), and collect_results() methods.
"""

from abc import ABC, abstractmethod
import logging
import uuid
from typing import Any, Dict, Optional

from app.integrations.autoscientist.config import DEFAULT_AUTOSCIENTIST_CONFIG, AutoScientistConfig
from app.integrations.autoscientist.models import AutoScientistJobStatus, MappedDataset

logger = logging.getLogger("dataset_genome.integrations.autoscientist.client")


class BaseAutoScientistClient(ABC):
    """
    MODULE 2 — Base AutoScientist Client Abstract Interface.
    
    Decouples Dataset Genome from specific API implementations or RPC protocols.
    """

    @abstractmethod
    def prepare(self, dataset: MappedDataset) -> str:
        """Prepare mapped dataset for submission and return a unique job_id."""
        pass

    @abstractmethod
    def submit(self, job_id: str) -> bool:
        """Submit prepared job to AutoScientist engine for execution."""
        pass

    @abstractmethod
    def monitor(self, job_id: str) -> AutoScientistJobStatus:
        """Query current execution status of submitted job."""
        pass

    @abstractmethod
    def collect_results(self, job_id: str) -> Dict[str, Any]:
        """Retrieve raw experiment execution results payload from AutoScientist."""
        pass


class MockAutoScientistClient(BaseAutoScientistClient):
    """
    Concrete Mock Implementation of BaseAutoScientistClient for offline execution & testing.
    """

    def __init__(self, config: AutoScientistConfig = DEFAULT_AUTOSCIENTIST_CONFIG) -> None:
        self.config = config
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def prepare(self, dataset: MappedDataset) -> str:
        """Prepare mapped dataset for submission."""
        job_id = f"job-auto-{uuid.uuid4().hex[:8]}"
        logger.info(f"Module 2 (Client) preparing job '{job_id}' for dataset version '{dataset.dataset_version}' ({dataset.total_samples} samples)...")

        self._jobs[job_id] = {
            "job_id": job_id,
            "status": AutoScientistJobStatus.PREPARED,
            "dataset": dataset,
            "submitted_at": None,
            "results": None,
        }
        return job_id

    def submit(self, job_id: str) -> bool:
        """Submit job to AutoScientist."""
        if job_id not in self._jobs:
            raise KeyError(f"Job ID '{job_id}' not found in client registry.")

        logger.info(f"Module 2 (Client) submitting job '{job_id}' to AutoScientist service...")
        job = self._jobs[job_id]
        job["status"] = AutoScientistJobStatus.SUBMITTED
        
        # Simulate instant completion in mock client
        job["status"] = AutoScientistJobStatus.COMPLETED
        return True

    def monitor(self, job_id: str) -> AutoScientistJobStatus:
        """Monitor job execution status."""
        if job_id not in self._jobs:
            return AutoScientistJobStatus.FAILED
        return self._jobs[job_id]["status"]

    def collect_results(self, job_id: str) -> Dict[str, Any]:
        """Collect results payload from AutoScientist run."""
        if job_id not in self._jobs:
            raise KeyError(f"Job ID '{job_id}' not found.")

        job = self._jobs[job_id]
        dataset: MappedDataset = job["dataset"]

        # Calculate mock domain accuracy breakdown
        domain_counts: Dict[str, int] = {}
        for s in dataset.samples:
            domain_counts[s.domain] = domain_counts.get(s.domain, 0) + 1

        # Simulate weak accuracy if Genomics/Medicine or low sample count
        domain_accuracies: Dict[str, float] = {}
        for dom, cnt in domain_counts.items():
            if cnt < 5 or dom in ("Genomics", "Medicine"):
                domain_accuracies[dom] = 0.62  # Weak performance
            else:
                domain_accuracies[dom] = 0.91  # Strong performance

        raw_results = {
            "experiment_id": f"exp-bench-{job_id}",
            "job_id": job_id,
            "status": "COMPLETED",
            "total_benchmark_samples": dataset.total_samples,
            "reasoning_quality_score": 88.5,
            "hypothesis_accuracy": 0.84,
            "confidence_score": 0.89,
            "domain_accuracies": domain_accuracies,
            "failure_modes_detected": ["Genomics domain sample insufficiency", "Low failure case coverage in hard difficulty tier"],
            "scientific_metrics": {
                "f1_macro": 0.86,
                "rmse_loss": 0.12,
                "p_value_significance": 0.002,
            },
        }

        job["results"] = raw_results
        logger.info(f"Module 2 (Client) collected execution results for job '{job_id}'.")
        return raw_results
