"""
tests/test_huggingface_integration.py — Unit & Integration tests for Phase 5 Hugging Face Integration Platform.

Tests DatasetPublisher (Module 1), ModelPublisher (Module 2), DatasetCardGenerator (Module 3),
ModelCardGenerator (Module 4), VersionManager (Module 5), MetadataManager (Module 6),
HuggingFaceUploader (Module 7), and report exporters.
"""

import json
from pathlib import Path
import pytest

from app.adaptive_data import AdaptiveDataPipeline
from app.dataset_generator import DatasetGenerator
from app.integrations.huggingface import (
    DatasetCardGenerator,
    DatasetPackage,
    DatasetPublisher,
    DatasetVersionRecord,
    GenomeMetadata,
    HuggingFaceUploader,
    MetadataManager,
    MockHuggingFaceClient,
    ModelArtifactPackage,
    ModelCardGenerator,
    ModelPublisher,
    PublishingReport,
    VersionManager,
    export_publishing_report_json,
    export_publishing_report_markdown,
)


def test_module_1_dataset_publisher():
    """Test Module 1: DatasetPublisher bundles TrainingReadyDataset."""
    generator = DatasetGenerator()
    records = generator.generate("Agriculture", 5)

    pipeline = AdaptiveDataPipeline()
    training_ready = pipeline.process(records)

    publisher = DatasetPublisher()
    package = publisher.prepare_package(training_ready)

    assert isinstance(package, DatasetPackage)
    assert package.total_samples == 5
    assert "Dataset Genome" in package.dataset_card_markdown


def test_module_2_model_publisher():
    """Test Module 2: ModelPublisher bundles model checkpoint metadata."""
    publisher = ModelPublisher()
    package = publisher.prepare_package(model_version="v1.0", dataset_version="v2.0-adaptive")

    assert isinstance(package, ModelArtifactPackage)
    assert package.model_version == "v1.0"
    assert "AutoScientist Reasoning Model" in package.model_card_markdown


def test_modules_3_and_4_card_generators():
    """Test Modules 3 & 4: DatasetCardGenerator and ModelCardGenerator."""
    generator = DatasetGenerator()
    records = generator.generate("Medicine", 5)
    pipeline = AdaptiveDataPipeline()
    training_ready = pipeline.process(records)

    ds_card_gen = DatasetCardGenerator()
    ds_card = ds_card_gen.generate_card(training_ready)
    assert "## Dataset Description" in ds_card
    assert "bibtex" in ds_card

    mdl_card_gen = ModelCardGenerator()
    mdl_card = mdl_card_gen.generate_card()
    assert "## Model Architecture & Intended Use" in mdl_card


def test_module_5_version_manager():
    """Test Module 5: VersionManager records version lineage."""
    vm = VersionManager()
    rec = vm.record_version("v1.0", "Initial dataset release", 85.0, 88.0)

    assert isinstance(rec, DatasetVersionRecord)
    assert rec.version_tag == "v1.0"
    assert len(vm.get_history()) == 1


def test_module_6_metadata_manager():
    """Test Module 6: MetadataManager generates UUID manifest."""
    mm = MetadataManager()
    meta = mm.generate_metadata(version="v3.0")

    assert isinstance(meta, GenomeMetadata)
    assert meta.dataset_uuid.startswith("uuid-ds-")
    assert meta.model_uuid.startswith("uuid-mdl-")


def test_module_7_huggingface_uploader_full_flow(tmp_path):
    """Test Module 7: HuggingFaceUploader orchestrating full publication flow."""
    generator = DatasetGenerator()
    records = generator.generate("Climate Science", 5)

    pipeline = AdaptiveDataPipeline()
    training_ready = pipeline.process(records)

    uploader = HuggingFaceUploader()
    report = uploader.publish(dataset=training_ready, model_version="v1.0")

    assert isinstance(report, PublishingReport)
    assert report.ready_for_publish is True
    assert len(report.artifacts) >= 2
    assert len(report.cards_generated) == 2

    # Test JSON Exporter
    json_path = tmp_path / "publishing_report.json"
    json_str = export_publishing_report_json(report, output_path=json_path)
    assert "publication_id" in json_str
    assert json_path.exists()

    # Test Markdown Exporter
    md_path = tmp_path / "publishing_report.md"
    md_str = export_publishing_report_markdown(report, output_path=md_path)
    assert "# Dataset Genome — Hugging Face Publishing Report" in md_str
    assert md_path.exists()
