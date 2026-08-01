"""
backend/app/benchmark/models.py — Pydantic v2 Schemas for Official Benchmark System.

Defines BenchmarkSample (16 fields), BenchmarkSampleBuilder (Builder Pattern),
BenchmarkStatistics, ValidationResult, BenchmarkVersionRecord, and BenchmarkReport.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BenchmarkSample(BaseModel):
    """
    Official Benchmark Sample model implementing the complete 16-field scientific reasoning schema.
    """

    sample_id: str = Field(..., description="Unique benchmark sample ID e.g. 'bm-agri-001'")
    dataset_id: str = Field("dataset-genome-benchmark-v1.0", description="Dataset identifier slug")
    domain: str = Field(
        ...,
        description="Supported Domain: Agriculture, Healthcare, Climate Science, Biology, Chemistry, Physics, Mathematics, Finance, HR, Market Analysis",
    )
    difficulty: str = Field(
        ...,
        description="Difficulty level: Easy, Medium, Hard, Expert",
    )
    prompt: str = Field(..., description="Scientific inquiry prompt or question")
    context: str = Field(..., description="Experimental or observational context")
    observation: str = Field(..., description="Empirical evidence or phenomenon observation")
    problem_identification: str = Field(..., description="Core problem or research bottleneck identified")
    research_gap: str = Field(..., description="Unanswered scientific question or knowledge gap")
    primary_hypothesis: str = Field(..., description="Testable primary scientific hypothesis")
    alternative_hypothesis: str = Field(..., description="Counter-hypothesis or alternative mechanism")
    experiment_design: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured experiment design protocol (variables, controls, methodology)",
    )
    evaluation_metrics: List[str] = Field(
        default_factory=list,
        description="List of quantitative/qualitative metrics used to measure hypothesis validation",
    )
    expected_results: str = Field(..., description="Predicted experimental outcomes if primary hypothesis holds")
    failure_cases: List[str] = Field(
        default_factory=list,
        description="Potential failure modes, negative controls, or disproving outcomes",
    )
    scientific_conclusion: str = Field(..., description="Deductive scientific synthesis and conclusion")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Auxiliary metadata (citations, version, tags)",
    )


class BenchmarkSampleBuilder:
    """
    Builder Pattern for constructing valid BenchmarkSample instances step-by-step.
    """

    def __init__(self, sample_id: str, domain: str, difficulty: str) -> None:
        self._data: Dict[str, Any] = {
            "sample_id": sample_id,
            "dataset_id": "dataset-genome-benchmark-v1.0",
            "domain": domain,
            "difficulty": difficulty,
            "prompt": "",
            "context": "",
            "observation": "",
            "problem_identification": "",
            "research_gap": "",
            "primary_hypothesis": "",
            "alternative_hypothesis": "",
            "experiment_design": {},
            "evaluation_metrics": [],
            "expected_results": "",
            "failure_cases": [],
            "scientific_conclusion": "",
            "metadata": {},
        }

    def set_dataset_id(self, dataset_id: str) -> "BenchmarkSampleBuilder":
        self._data["dataset_id"] = dataset_id
        return self

    def set_inquiry(self, prompt: str, context: str, observation: str) -> "BenchmarkSampleBuilder":
        self._data["prompt"] = prompt
        self._data["context"] = context
        self._data["observation"] = observation
        return self

    def set_problem(self, problem_identification: str, research_gap: str) -> "BenchmarkSampleBuilder":
        self._data["problem_identification"] = problem_identification
        self._data["research_gap"] = research_gap
        return self

    def set_hypotheses(self, primary: str, alternative: str) -> "BenchmarkSampleBuilder":
        self._data["primary_hypothesis"] = primary
        self._data["alternative_hypothesis"] = alternative
        return self

    def set_experiment(
        self,
        design: Dict[str, Any],
        metrics: List[str],
        expected_results: str,
        failure_cases: List[str],
    ) -> "BenchmarkSampleBuilder":
        self._data["experiment_design"] = design
        self._data["evaluation_metrics"] = metrics
        self._data["expected_results"] = expected_results
        self._data["failure_cases"] = failure_cases
        return self

    def set_conclusion(self, scientific_conclusion: str) -> "BenchmarkSampleBuilder":
        self._data["scientific_conclusion"] = scientific_conclusion
        return self

    def set_metadata(self, metadata: Dict[str, Any]) -> "BenchmarkSampleBuilder":
        self._data["metadata"] = metadata
        return self

    def build(self) -> BenchmarkSample:
        """Validate and return the built BenchmarkSample."""
        return BenchmarkSample.model_validate(self._data)


class BenchmarkStatistics(BaseModel):
    """Statistics assessing overall benchmark dataset composition and health."""

    total_samples: int = Field(..., ge=0, description="Total number of benchmark samples")
    domain_distribution: Dict[str, int] = Field(..., description="Sample count breakdown per domain")
    difficulty_distribution: Dict[str, int] = Field(..., description="Sample count breakdown per difficulty level")
    knowledge_coverage: float = Field(..., ge=0.0, le=100.0, description="Knowledge graph coverage score [0..100]")
    reasoning_coverage: float = Field(..., ge=0.0, le=100.0, description="16-field reasoning completeness score [0..100]")
    experiment_diversity: float = Field(..., ge=0.0, le=100.0, description="Experiment design protocol diversity score [0..100]")
    failure_diversity: float = Field(..., ge=0.0, le=100.0, description="Failure mode & negative control coverage score [0..100]")
    adaptive_score: float = Field(..., ge=0.0, le=100.0, description="Composite Benchmark Adaptive Score [0..100]")


class ValidationResult(BaseModel):
    """Result summary of benchmark validation execution."""

    is_valid: bool = Field(..., description="True if benchmark passes all validation criteria")
    duplicate_count: int = Field(..., ge=0, description="Number of duplicate samples detected")
    incomplete_count: int = Field(..., ge=0, description="Number of samples with incomplete reasoning chains")
    domain_balance_pass: bool = Field(..., description="True if domains are uniformly distributed")
    difficulty_balance_pass: bool = Field(..., description="True if difficulty levels are balanced")
    validation_issues: List[str] = Field(default_factory=list, description="List of detected validation flaws or warnings")


class BenchmarkVersionRecord(BaseModel):
    """Lineage tracker tracking version updates (Benchmark v1.0 -> v1.1 -> v2.0)."""

    version_tag: str = Field(..., description="Version slug e.g. 'v1.0', 'v1.1'")
    total_samples: int = Field(..., ge=0, description="Total sample count for this version")
    adaptive_score: float = Field(..., ge=0.0, le=100.0, description="Benchmark adaptive score")
    knowledge_coverage: float = Field(..., ge=0.0, le=100.0, description="Knowledge coverage score")
    changes_description: str = Field(..., description="Summary of changes in this release")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Release timestamp")


class BenchmarkReport(BaseModel):
    """Complete report summary output for Benchmark v1.0."""

    report_id: str = Field(..., description="Unique report execution ID")
    version: str = Field("v1.0", description="Benchmark version tag")
    statistics: BenchmarkStatistics = Field(..., description="Calculated benchmark statistics")
    validation: ValidationResult = Field(..., description="Validation summary findings")
    version_history: List[BenchmarkVersionRecord] = Field(default_factory=list, description="Version lineage progression")
    exported_formats: List[str] = Field(default_factory=list, description="List of exported format names")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")
