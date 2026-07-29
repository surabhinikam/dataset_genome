"""
services/autoscientist/resource_estimator.py — Resource Estimation Module.

Estimates runtime (seconds), RAM usage (MB), Disk IO (MB), and complexity level
for planned dataset experiments based on dataset size and transformation type.
"""

from typing import Any, Dict, List
from services.autoscientist.experiment_models import ResourceEstimate
from services.autoscientist.planning_constants import BASE_RUNTIME_PER_1K_ROWS, PlanningComplexity


class ResourceEstimator:
    """
    Estimates computational resource requirements for executing ExperimentPlans.
    """

    @classmethod
    def estimate_resources(
        cls,
        transformation_type: str,
        num_rows: int = 1000,
        num_cols: int = 10,
        parameters: Dict[str, Any] = None
    ) -> ResourceEstimate:
        """
        Compute estimated runtime, memory, disk IO, and complexity.
        """
        rows_k = max(0.1, num_rows / 1000.0)
        base_rate = BASE_RUNTIME_PER_1K_ROWS.get(transformation_type, 0.20)

        # Runtime estimation
        runtime_sec = round(base_rate * rows_k, 2)
        runtime_sec = max(0.1, min(60.0, runtime_sec))

        # RAM estimation (base 50MB + 15MB per 10k cells)
        total_cells = max(100, num_rows * num_cols)
        memory_mb = round(50.0 + (total_cells / 10000.0) * 15.0, 2)
        memory_mb = max(50.0, min(2048.0, memory_mb))

        # Disk IO estimation (2x dataset CSV memory footprint approx)
        disk_io_mb = round((total_cells * 8) / (1024.0 * 1024.0) * 2.0 + 1.0, 2)

        # Complexity determination
        if transformation_type in ["ClassRebalancingTransformation", "ImputationTransformation"]:
            complexity = PlanningComplexity.HIGH
        elif transformation_type in ["WinsorizationTransformation", "MedianImputationTransformation", "TypeUnificationTransformation"]:
            complexity = PlanningComplexity.MEDIUM
        else:
            complexity = PlanningComplexity.LOW

        return ResourceEstimate(
            estimated_runtime_seconds=runtime_sec,
            estimated_memory_mb=memory_mb,
            estimated_disk_io_mb=disk_io_mb,
            complexity_level=complexity,
        )
