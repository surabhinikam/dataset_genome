"""
services/dataset_intelligence/base.py — BaseProfiler abstract class.

Defines the interface that all profiler modules must implement.
Ensures single responsibility and easy testability.
"""

from abc import ABC, abstractmethod
from typing import Tuple, List, Any
import pandas as pd
from schemas.intelligence import DatasetIssue


class BaseProfiler(ABC):
    """
    Abstract base class for all Dataset Intelligence profilers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the profiler."""
        pass

    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> Tuple[Any, List[DatasetIssue]]:
        """
        Execute profiling on the given pandas DataFrame.

        Returns
        -------
        Tuple[Any, List[DatasetIssue]]
            (profiler_metrics_pydantic_model, list_of_detected_issues)
        """
        pass
