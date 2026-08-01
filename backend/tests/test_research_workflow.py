"""
tests/test_research_workflow.py — Unit & Integration tests for Phase 8 Autonomous Research Workflow.

Tests ResearchAnalyzer, ImprovementPlanner, ResearchFeedbackEngine,
AutonomousResearchCoordinator multi-iteration loop, version lineage tracking,
stopping criteria rules, and report exporters.
"""

from pathlib import Path
import pytest

from app.research import (
    AutonomousResearchCoordinator,
    AutonomousResearchWorkflow,
    FailurePattern,
    ImprovementPlanner,
    IterationRecord,
    ResearchAnalyzer,
    ResearchFeedbackEngine,
    ResearchWorkflowReport,
    StoppingCriteriaConfig,
    export_research_report_json,
    export_research_report_markdown,
)


def test_research_analyzer_and_planner():
    """Test ResearchAnalyzer failure pattern detection and ImprovementPlanner recommendations."""
    analyzer = ResearchAnalyzer()
    planner = ImprovementPlanner()

    # Simulate iteration execution
    workflow = AutonomousResearchWorkflow()
    rec, dataset, result = workflow.execute_iteration("Agriculture", 10, "v1.0-adaptive")

    failures = analyzer.analyze_iteration(dataset, result)
    assert isinstance(failures, list)

    recommendations = planner.plan_improvements(failures)
    assert len(recommendations) >= 1
    assert recommendations[0].expected_score_gain > 0.0


def test_specific_recommendation_types():
    """Test planner produces specific recommendations like oncology upsampling and harder reasoning."""
    planner = ImprovementPlanner()
    failures = [
        FailurePattern(
            category="Coverage Gap",
            description="Key domain Oncology missing",
            severity="MEDIUM",
            affected_domain="Oncology",
        ),
        FailurePattern(
            category="Hard Reasoning Gap",
            description="Reasoning benchmark score below target",
            severity="HIGH",
        ),
        FailurePattern(
            category="Low Failure Coverage",
            description="Failure coverage low",
            severity="MEDIUM",
        ),
    ]

    recs = planner.plan_improvements(failures)
    action_types = [r.action_type for r in recs]
    assert "INCREASE_ONCOLOGY_SAMPLES" in action_types
    assert "HARDER_REASONING" in action_types
    assert "INCREASE_FAILURE_COVERAGE" in action_types


def test_research_feedback_engine():
    """Test ResearchFeedbackEngine request creation and observed delta recording."""
    feedback = ResearchFeedbackEngine()
    workflow = AutonomousResearchWorkflow()

    _, dataset, result = workflow.execute_iteration("Agriculture", 10, "v1.0-adaptive")
    analyzer = ResearchAnalyzer()
    planner = ImprovementPlanner()

    failures = analyzer.analyze_iteration(dataset, result)
    recs = planner.plan_improvements(failures)

    req = feedback.create_improvement_request(
        from_version="v1.0-adaptive",
        to_version="v2.0-adaptive",
        recommendations=recs,
    )

    assert req.from_version == "v1.0-adaptive"
    assert req.to_version == "v2.0-adaptive"

    delta = feedback.record_observed_improvement(req, previous_score=75.0, current_score=81.5)
    assert delta == 6.5
    assert req.observed_improvement == 6.5


def test_stopping_criteria_threshold():
    """Test coordinator stopping when adaptive score threshold is satisfied."""
    criteria = StoppingCriteriaConfig(
        max_iterations=5,
        target_adaptive_score=70.0,  # Low threshold to trigger early stop
    )
    coordinator = AutonomousResearchCoordinator(stopping_criteria=criteria)

    report = coordinator.run_research_loop(domain="Agriculture", initial_count=10)
    assert report.total_iterations == 1
    assert "Target adaptive score achieved" in report.stopping_reason


def test_autonomous_research_coordinator_closed_loop(tmp_path):
    """Test AutonomousResearchCoordinator running multi-iteration self-improving loop."""
    criteria = StoppingCriteriaConfig(
        max_iterations=2,
        target_adaptive_score=95.0,
        target_evaluation_score=98.0,
    )
    coordinator = AutonomousResearchCoordinator(stopping_criteria=criteria)

    report = coordinator.run_research_loop(domain="Agriculture", initial_count=10)

    assert isinstance(report, ResearchWorkflowReport)
    assert report.total_iterations == 2
    assert report.initial_version == "v1.0-adaptive"
    assert report.final_version == "v2.0-adaptive"
    assert len(report.iterations) == 2
    assert len(report.version_lineage) == 2

    # Exporters
    json_path = tmp_path / "research_report.json"
    json_str = export_research_report_json(report, output_path=json_path)
    assert "research_id" in json_str
    assert json_path.exists()

    md_path = tmp_path / "research_report.md"
    md_str = export_research_report_markdown(report, output_path=md_path)
    assert "# Dataset Genome — Autonomous Research Workflow Report" in md_str
    assert "Recommendations Applied & Improvement Timeline" in md_str
    assert md_path.exists()
