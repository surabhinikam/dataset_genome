"""
services/autoscientist — AutoScientist Intelligence & Reasoning Layer.

Contains the Observation Engine, Problem Ranking Engine, Reasoning Engine,
Scientific Hypothesis Generator, Experiment Planner, Execution Engine, Evaluation Engine, Scientific Memory, Confidence Engine, and Learning Loop.
"""

from services.autoscientist.evaluation_constants import EvaluationOutcome, EvaluationRecommendation
from services.autoscientist.evaluation_engine import EvaluationEngine
from services.autoscientist.evaluation_models import (
    EvaluateRequest,
    EvaluateResponse,
    EvaluationReport,
    MetricDelta,
)
from services.autoscientist.execution_engine import ExecutionEngine
from services.autoscientist.execution_models import (
    ExecuteRequest,
    ExecuteResponse,
    ExecutionResult,
    ExecutionStatus,
)
from services.autoscientist.experiment_models import (
    ExecutionStep,
    ExperimentPlan,
    PlanRequest,
    PlanResponse,
    ResourceEstimate,
    RollbackPlan,
    ValidationRuleItem,
)
from services.autoscientist.experiment_planner import ExperimentPlanner
from services.autoscientist.hypothesis_constants import ParameterFactory, RiskLevel
from services.autoscientist.hypothesis_engine import ScientificHypothesisGenerator
from services.autoscientist.hypothesis_models import (
    HypothesisRequest,
    HypothesisResponse,
    ScientificHypothesis,
)
from services.autoscientist.observation_engine import ObservationEngine
from services.autoscientist.observation_models import (
    ObservationCategory,
    ObservationRequest,
    ObservationResponse,
    ScientificObservation,
)
from services.autoscientist.ranking_engine import ProblemRankingEngine
from services.autoscientist.ranking_models import (
    PrioritizedProblemQueue,
    RankedProblem,
    RankRequest,
    RankResponse,
)
from services.autoscientist.reasoning_context import ReasoningContext
from services.autoscientist.reasoning_engine import ReasoningEngine
from services.autoscientist.reasoning_models import (
    ReasoningTrace,
    ReasonRequest,
    ReasonResponse,
    ScientificMemoryInterface,
)

from services.autoscientist.memory_builder import MemoryRecordBuilder
from services.autoscientist.memory_constants import SimilarityMetric
from services.autoscientist.memory_encoder import MemoryEncoder
from services.autoscientist.memory_engine import ScientificMemoryEngine
from services.autoscientist.memory_models import (
    MemoryRecord,
    MemoryRetrievalResult,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryStore,
    MemoryStoreRequest,
    MemoryStoreResponse,
)
from services.autoscientist.research_builder import ResearchNotebookBuilder
from services.autoscientist.research_models import (
    NotebookCreateRequest,
    NotebookEntry,
    NotebookResponse,
    NotebookStage,
    ResearchNotebook,
    TimelineEvent,
)
from services.autoscientist.research_notebook import ScientificResearchNotebookEngine
from services.autoscientist.llm_models import (
    ExplainRequest,
    ExplainResponse,
    ExplanationTarget,
    ScientificExplanation,
)
from services.autoscientist.llm_narrator import LLMScientificNarrator

__all__ = [
    "ObservationEngine",
    "ScientificObservation",
    "ObservationCategory",
    "ObservationRequest",
    "ObservationResponse",
    "ProblemRankingEngine",
    "RankedProblem",
    "PrioritizedProblemQueue",
    "RankRequest",
    "RankResponse",
    "ReasoningContext",
    "ReasoningEngine",
    "ReasoningTrace",
    "ReasonRequest",
    "ReasonResponse",
    "ScientificMemoryInterface",
    "ScientificHypothesisGenerator",
    "ScientificHypothesis",
    "RiskLevel",
    "HypothesisRequest",
    "HypothesisResponse",
    "ParameterFactory",
    "ExperimentPlanner",
    "ExperimentPlan",
    "ExecutionStep",
    "ValidationRuleItem",
    "RollbackPlan",
    "ResourceEstimate",
    "PlanRequest",
    "PlanResponse",
    "ExecutionEngine",
    "ExecutionResult",
    "ExecutionStatus",
    "ExecuteRequest",
    "ExecuteResponse",
    "EvaluationEngine",
    "EvaluationReport",
    "EvaluationOutcome",
    "EvaluationRecommendation",
    "MetricDelta",
    "EvaluateRequest",
    "EvaluateResponse",
    "ScientificMemoryEngine",
    "MemoryRecord",
    "MemoryStore",
    "MemoryRetrievalResult",
    "MemoryRecordBuilder",
    "MemoryEncoder",
    "SimilarityMetric",
    "MemoryStoreRequest",
    "MemoryStoreResponse",
    "MemorySearchRequest",
    "MemorySearchResponse",
    "ScientificResearchNotebookEngine",
    "ResearchNotebook",
    "NotebookEntry",
    "TimelineEvent",
    "NotebookStage",
    "ResearchNotebookBuilder",
    "NotebookCreateRequest",
    "NotebookResponse",
    "LLMScientificNarrator",
    "ExplanationTarget",
    "ScientificExplanation",
    "ExplainRequest",
    "ExplainResponse",
]



