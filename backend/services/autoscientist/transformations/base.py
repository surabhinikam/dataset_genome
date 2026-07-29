"""
services/autoscientist/transformations/base.py — Abstract Base Transformation.

Defines the common interface for all dataset mutation transformations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
import pandas as pd


class BaseTransformation(ABC):
    """
    Abstract Base Class for all Dataset Genome transformations.
    
    Every transformation must implement name property and transform() method.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name slug of the transformation class."""
        pass

    @abstractmethod
    def transform(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any],
        target_columns: List[str]
    ) -> Tuple[pd.DataFrame, List[str], List[str]]:
        """
        Execute transformation in memory on a pandas DataFrame.
        
        Returns:
            Tuple of (transformed_df, log_messages, warning_messages)
        """
        pass
