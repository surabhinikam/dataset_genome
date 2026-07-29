"""
tests/test_publication_engine.py — Unit & Integration tests for Publication Engine.

Tests DatasetPackager (Module 1), ModelPackager (Module 2), CardGenerator (Modules 3 & 4),
VersionManager & Changelog (Module 5), KaggleUploader (Module 6), HuggingFaceUploader (Module 7),
ReportPackager & PublicationPipeline (Module 8), and exporters.
"""

import json
from pathlib import Path
import pytest

from app.adaptive_data import AdaptiveDataPipeline
from app.dataset_generator import DatasetGenerator
from app.integrations.autoscientist import AutoScientistAdapter
from app.publication import (
    DatasetArtifactPackage,
    DatasetPackager,
    HuggingFacePackage,
    HuggingFaceUploader,
    KagglePackage,
    KaggleUploader,
    ModelArtifactPackage,
    ModelPackager,
    PublicationConfig,
    PublicationPipeline,
    PublicationReport,
    ReportPackager,
    export_publication_report_json,
    export_publication_report_markdown,
)


def test_module_1_dataset_packager(tmp_path):
    """Test Module 1: DatasetPackager creates dataset publication files."""
    generator = DatasetGenerator()
    records = generator.generate("Agriculture", 5)

    pipeline = AdaptiveDataPipeline()
    training_ready = pipeline.process(records)

    config = PublicationConfig(dataset_dir=str(tmp_path / "dataset"))
    packager = DatasetPackager(config=config)
    pkg = packager.package(training_ready)

    assert isinstance(pkg, DatasetArtifactPackage)
    assert Path(pkg.dataset_final_path).exists()
    assert Path(pkg.dataset_statistics_path).exists()
    assert Path(pkg.schema_path).exists()
    assert Path(pkg.metadata_path).exists()
    assert Path(pkg.dataset_summary_path).exists()


def test_module_2_model_packager(tmp_path):
    """Test Module 2: ModelPackager creates model publication files."""
    generator = DatasetGenerator()
    records = generator.generate("Medicine", 5)

    pipeline = AdaptiveDataPipeline()
    training_ready = pipeline.process(records)

    adapter = AutoScientistAdapter()
    result = adapter.execute_integration(training_ready)

    config = PublicationConfig(model_dir=str(tmp_path / "model"))
    packager = ModelPackager(config=config)
    pkg = packager.package(result)

    assert isinstance(pkg, ModelArtifactPackage)
    assert Path(pkg.model_metadata_path).exists()
    assert Path(pkg.training_summary_path).exists()
    assert Path(pkg.evaluation_path).exists()
    assert Path(pkg.weights_manifest_path).exists()


def test_module_6_kaggle_uploader(tmp_path):
    """Test Module 6: KaggleUploader creates publication/kaggle/ folder."""
    generator = DatasetGenerator()
    records = generator.generate("Physics", 5)

    pipeline = AdaptiveDataPipeline()
    training_ready = pipeline.process(records)

    config = PublicationConfig(kaggle_dir=str(tmp_path / "kaggle"))
    uploader = KaggleUploader(config=config)
    pkg = uploader.package(training_ready)

    assert isinstance(pkg, KagglePackage)
    assert Path(pkg.metadata_json_path).exists()
    assert Path(pkg.readme_path).exists()


def test_module_7_huggingface_uploader(tmp_path):
    """Test Module 7: HuggingFaceUploader creates publication/huggingface/ folder."""
    generator = DatasetGenerator()
    records = generator.generate("Climate Science", 5)

    pipeline = AdaptiveDataPipeline()
    training_ready = pipeline.process(records)

    adapter = AutoScientistAdapter()
    result = adapter.execute_integration(training_ready)

    config = PublicationConfig(huggingface_dir=str(tmp_path / "huggingface"))
    uploader = HuggingFaceUploader(config=config)
    pkg = uploader.package(training_ready, result)

    assert isinstance(pkg, HuggingFacePackage)
    assert Path(pkg.dataset_card_path).exists()
    assert Path(pkg.model_card_path).exists()


def test_publication_pipeline_master_flow(tmp_path):
    """Test full PublicationPipeline execution across all modules."""
    generator = DatasetGenerator()
    records = generator.generate("Agriculture", 5)

    adaptive_pipeline = AdaptiveDataPipeline()
    training_ready = adaptive_pipeline.process(records)

    adapter = AutoScientistAdapter()
    result = adapter.execute_integration(training_ready)

    config = PublicationConfig(
        base_output_dir=str(tmp_path / "publication"),
        dataset_dir=str(tmp_path / "publication" / "dataset"),
        model_dir=str(tmp_path / "publication" / "model"),
        kaggle_dir=str(tmp_path / "publication" / "kaggle"),
        huggingface_dir=str(tmp_path / "publication" / "huggingface"),
        reports_dir=str(tmp_path / "publication" / "reports"),
        release_dir=str(tmp_path / "publication" / "release"),
    )

    pub_pipeline = PublicationPipeline(config=config)
    report = pub_pipeline.run(training_ready, result)

    assert isinstance(report, PublicationReport)
    assert report.dataset_ready is True
    assert report.model_ready is True
    assert report.hf_ready is True
    assert report.kaggle_ready is True
    assert len(report.artifacts_generated) > 10

    # Exporters test
    json_str = export_publication_report_json(report, output_path=tmp_path / "pub_rep.json")
    assert "publication_id" in json_str

    md_str = export_publication_report_markdown(report, output_path=tmp_path / "pub_rep.md")
    assert "# Dataset Genome — Master Publication Report" in md_str
