"""
tests/test_end_to_end_pipeline_integration.py — End-to-End Multi-Module Schema & Interface Consistency Test.

Verifies exact data model compatibility across the entire Dataset Genome pipeline:
DatasetGenerator -> DatasetIntelligence -> DatasetEvolution -> AdaptiveDataEngine -> AutoScientistAdapter -> PublicationPipeline.
"""

import pytest

from app.adaptive_data import AdaptiveDataPipeline, TrainingReadyDataset
from app.dataset_evolution import EvolutionPlan, EvolutionPlanner
from app.dataset_generator import DatasetGenerator, ScientificReasoningRecord
from app.dataset_intelligence import DatasetAnalysisReport, DatasetAnalyzer
from app.integrations.autoscientist import AutoScientistAdapter, AutoScientistResult
from app.publication import PublicationPipeline, PublicationReport


def test_complete_end_to_end_pipeline_data_model_consistency():
    """
    Test complete data flow across all 6 Dataset Genome modules:
    
    1. DatasetGenerator outputs List[ScientificReasoningRecord]
    2. DatasetAnalyzer consumes List[ScientificReasoningRecord] and outputs DatasetAnalysisReport
    3. EvolutionPlanner consumes DatasetAnalysisReport and outputs EvolutionPlan
    4. AdaptiveDataPipeline consumes List[ScientificReasoningRecord] + DatasetAnalysisReport and outputs TrainingReadyDataset
    5. AutoScientistAdapter consumes TrainingReadyDataset and outputs AutoScientistResult
    6. PublicationPipeline consumes TrainingReadyDataset + AutoScientistResult and outputs PublicationReport
    """

    # STAGE 1: Dataset Generation
    generator = DatasetGenerator()
    records = generator.generate(domain="Agriculture", count=15)
    assert isinstance(records, list)
    assert len(records) == 15
    assert isinstance(records[0], ScientificReasoningRecord)

    # STAGE 2: Dataset Intelligence Profiling
    analyzer = DatasetAnalyzer()
    intel_report = analyzer.analyze_records(records)
    assert isinstance(intel_report, DatasetAnalysisReport)
    assert intel_report.general_statistics.total_samples == 15

    # STAGE 3: Dataset Evolution Planning
    evolution_planner = EvolutionPlanner()
    evolution_plan = evolution_planner.create_plan(intel_report)
    assert isinstance(evolution_plan, EvolutionPlan)
    assert len(evolution_plan.issues) >= 0

    # STAGE 4: Adaptive Data Engine Optimization
    adaptive_pipeline = AdaptiveDataPipeline()
    training_ready = adaptive_pipeline.process(records=records, intelligence_report=intel_report)
    assert isinstance(training_ready, TrainingReadyDataset)
    assert training_ready.cleaning_summary.cleaned_sample_count == 15

    # STAGE 5: AutoScientist Integration Adapter
    autoscientist_adapter = AutoScientistAdapter()
    autoscientist_result = autoscientist_adapter.execute_integration(training_ready)
    assert isinstance(autoscientist_result, AutoScientistResult)
    assert autoscientist_result.evaluation.hypothesis_accuracy > 0.0

    # STAGE 6: Master Publication & Open Source Engine
    publication_pipeline = PublicationPipeline()
    pub_report = publication_pipeline.run(
        dataset=training_ready,
        autoscientist_result=autoscientist_result,
        model_version="v1.0",
        changes_description="End-to-End Integration Verification Test Run",
    )
    assert isinstance(pub_report, PublicationReport)
    assert pub_report.dataset_ready is True
    assert pub_report.model_ready is True
    assert pub_report.hf_ready is True
    assert pub_report.kaggle_ready is True
