"""
services/autoscientist/hypothesis_engine.py — Main Hypothesis Generator Engine Coordinator.

Transforms validated ReasoningTrace objects into testable, measurable, and falsifiable ScientificHypothesis models.
"""

import logging
from typing import Optional

from services.autoscientist.hypothesis_builder import ScientificHypothesisBuilder
from services.autoscientist.hypothesis_models import ScientificHypothesis
from services.autoscientist.hypothesis_templates import FallbackHypothesisTemplate, HYPOTHESIS_TEMPLATE_REGISTRY
from services.autoscientist.reasoning_models import ReasoningTrace

logger = logging.getLogger("dataset_genome.hypothesis_engine")


class ScientificHypothesisGenerator:
    """
    Scientific Hypothesis Generator for Dataset Genome AutoScientist.
    
    Synthesizes testable, measurable, and falsifiable scientific claim statements
    from a validated Causal ReasoningTrace without generating executable Python code.
    """

    def __init__(self) -> None:
        self._templates = HYPOTHESIS_TEMPLATE_REGISTRY
        self._fallback_template = FallbackHypothesisTemplate()

    def generate_hypothesis(self, trace: ReasoningTrace) -> ScientificHypothesis:
        """
        Synthesize a ScientificHypothesis from a validated ReasoningTrace.
        
        Evaluates category-specific hypothesis templates, selects parameter factories,
        predicts metric improvement deltas, assesses risk levels, and validates the output.
        """
        logger.info(f"Generating ScientificHypothesis for reasoning trace_id='{trace.id}' (Category: {trace.category})")

        # 1. Select hypothesis template for category
        template = self._templates.get(trace.category, self._fallback_template)

        # 2. Execute template synthesis
        res = template.generate(trace)

        # 3. Construct hypothesis via fluent builder
        hyp_id = f"hyp-{trace.problem_id}"
        builder = (
            ScientificHypothesisBuilder()
            .with_id(hyp_id)
            .with_problem_id(trace.problem_id)
            .with_statement(res.statement)
            .with_observation_summary(trace.reasoning_summary)
            .with_causal_mechanism(trace.inferred_mechanism)
            .with_transformation_type(trace.recommended_transformation_class)
            .with_target_column(res.target_column)
            .with_proposed_parameters(res.proposed_parameters)
            .with_target_evaluation_metric(res.target_evaluation_metric)
            .with_predicted_metric_delta(res.predicted_metric_delta)
            .with_estimated_confidence(res.estimated_confidence)
            .with_risk_level(res.risk_level)
            .with_expected_side_effects(res.expected_side_effects)
            .with_assumptions(trace.assumptions)
            .with_constraints(trace.constraints)
        )

        hypothesis = builder.build()
        logger.info(f"Successfully generated validated ScientificHypothesis (id='{hypothesis.id}')")
        return hypothesis
