"""
services/autoscientist/transformation_registry.py — Transformation Registry Pattern.

Maps dataset transformation class names (strings) to executable BaseTransformation plugin instances.
Avoids giant if-else blocks.
"""

import logging
from typing import Dict, Optional
from services.autoscientist.transformations.base import BaseTransformation
from services.autoscientist.transformations.feature_drop import FeatureDropTransformation, FeaturePruningTransformation
from services.autoscientist.transformations.knn_imputation import KNNImputationTransformation
from services.autoscientist.transformations.median_imputation import MedianImputationTransformation
from services.autoscientist.transformations.smote import SMOTEClassRebalancingTransformation
from services.autoscientist.transformations.winsorization import WinsorizationTransformation

logger = logging.getLogger("dataset_genome.transformation_registry")


class TransformationRegistry:
    """
    Registry for Dataset Genome Transformation plugins (Registry & Strategy Pattern).
    """

    def __init__(self) -> None:
        self._registry: Dict[str, BaseTransformation] = {}

        # Register default transformation plugins
        self.register("FeatureDropTransformation", FeatureDropTransformation())
        self.register("FeaturePruningTransformation", FeaturePruningTransformation())
        self.register("ImputationTransformation", KNNImputationTransformation())
        self.register("MedianImputationTransformation", MedianImputationTransformation())
        self.register("WinsorizationTransformation", WinsorizationTransformation())
        self.register("ClassRebalancingTransformation", SMOTEClassRebalancingTransformation())

    def register(self, name: str, transformation: BaseTransformation) -> None:
        """Register a transformation plugin under name key."""
        self._registry[name] = transformation
        logger.info(f"Registered transformation plugin '{name}' ({transformation.__class__.__name__})")

    def get(self, name: str) -> BaseTransformation:
        """
        Get transformation plugin instance by name key.
        
        Raises ValueError if transformation name is not registered.
        """
        if name not in self._registry:
            raise ValueError(f"Unsupported transformation type '{name}'. Registered options: {list(self._registry.keys())}")
        return self._registry[name]

    def has(self, name: str) -> bool:
        """Check if transformation name is registered."""
        return name in self._registry
