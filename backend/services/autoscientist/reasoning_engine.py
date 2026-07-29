"""
services/autoscientist/reasoning_engine.py — Main Reasoning Engine Coordinator.

Coordinates template-based scientific reasoning, context aggregation, memory interface
stubs, and output validation to produce validated ReasoningTrace domain models.
"""

import logging
from services.autoscientist.reasoning_builder import ReasoningTraceBuilder
from services.autoscientist.reasoning_context import ReasoningContext
from services.autoscientist.reasoning_models import ReasoningTrace
from services.autoscientist.reasoning_templates import FallbackReasoningTemplate, TEMPLATE_REGISTRY

logger = logging.getLogger("dataset_genome.reasoning_engine")


class ReasoningEngine:
    """
    Core Reasoning Engine for Dataset Genome AutoScientist.
    
    Transforms a ReasoningContext containing a target RankedProblem into a structured,
    validated Causal Reasoning Trace (ReasoningTrace) without generating executable code.
    """

    def __init__(self) -> None:
        self._templates = TEMPLATE_REGISTRY
        self._fallback_template = FallbackReasoningTemplate()

    def generate_reasoning_trace(self, context: ReasoningContext) -> ReasoningTrace:
        """
        Synthesize a structured CausalReasoningTrace from a ReasoningContext.
        
        Evaluates category-specific reasoning templates, integrates Scientific Memory
        insights, applies data constraints, and validates the output trace.
        """
        problem = context.prioritized_problem
        obs = problem.observation
        category = obs.category

        logger.info(f"Generating ReasoningTrace for problem_id='{problem.observation_id}' (Category: {category})")

        # 1. Select template for category
        template = self._templates.get(category, self._fallback_template)

        # 2. Execute template reasoning
        res = template.reason(problem)

        # 3. Combine constraints with context constraints
        combined_constraints = list(set(res.constraints + context.constraints))

        # 4. Build trace via fluent builder
        trace_id = f"trace-{problem.observation_id}"
        builder = (
            ReasoningTraceBuilder()
            .with_id(trace_id)
            .with_problem_id(problem.observation_id)
            .with_category(category)
            .with_reasoning_summary(res.reasoning_summary)
            .with_inferred_mechanism(res.inferred_mechanism)
            .with_supporting_evidence(obs.evidence)
            .with_recommended_transformation_class(res.recommended_transformation_class)
            .with_confidence(res.confidence)
            .with_assumptions(res.assumptions)
            .with_constraints(combined_constraints)
            .with_risks(res.risks)
            .with_memory_insights(context.memory_interface)
        )

        trace = builder.build()
        logger.info(f"Successfully generated validated ReasoningTrace (id='{trace.id}')")
        return trace
