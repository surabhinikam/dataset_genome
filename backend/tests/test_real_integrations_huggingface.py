"""
tests/test_real_integrations_huggingface.py — Unit tests for Hugging Face Hub, Datasets, Evaluate, and Transformers integrations.
"""

from pathlib import Path
import pytest

from app.integrations.huggingface.auth import HuggingFaceAuth
from app.integrations.huggingface.datasets import HuggingFaceDatasetsWrapper
from app.integrations.huggingface.downloader import HuggingFaceDownloader
from app.integrations.huggingface.evaluate import HuggingFaceEvaluator, MetricRegistry
from app.integrations.huggingface.hub import HuggingFaceHubWrapper
from app.integrations.huggingface.uploader import ProductionHuggingFaceUploader
from app.integrations.huggingface.utils import TransformersLoader


def test_hf_hub_wrapper():
    """Test HuggingFaceHubWrapper repo creation and file upload simulation."""
    hub = HuggingFaceHubWrapper()
    repo_url = hub.create_repo("dataset-genome/test-repo")
    assert "dataset-genome/test-repo" in repo_url

    file_url = hub.upload_file("README.md", "README.md", "dataset-genome/test-repo")
    assert "README.md" in file_url


def test_hf_datasets_wrapper(tmp_path):
    """Test HuggingFaceDatasetsWrapper from_list and save_to_disk."""
    ds_wrapper = HuggingFaceDatasetsWrapper()
    records = [{"id": "s1", "domain": "Agriculture"}, {"id": "s2", "domain": "Medicine"}]

    ds = ds_wrapper.from_list(records)
    saved_path = ds_wrapper.save_to_disk(ds, tmp_path / "saved_ds")
    assert Path(saved_path).exists()


def test_hf_evaluator_metrics():
    """Test HuggingFaceEvaluator Accuracy, Precision, Recall, F1, BLEU, ROUGE, and MetricRegistry."""
    evaluator = HuggingFaceEvaluator()
    preds = ["a", "b", "c", "d"]
    refs = ["a", "b", "c", "e"]

    acc = evaluator.compute_accuracy(preds, refs)
    assert acc == 0.75

    metrics = evaluator.evaluate_all(preds, refs)
    assert metrics["accuracy"] == 0.75
    assert "f1" in metrics
    assert "bleu" in metrics
    assert "rouge1" in metrics

    # Test MetricRegistry dynamic registration
    evaluator.registry.register("custom_metric", lambda p, r: 0.99)
    val = evaluator.registry.compute_custom("custom_metric", preds, refs)
    assert val == 0.99


def test_transformers_loader():
    """Test TransformersLoader configurable model and tokenizer loading."""
    loader = TransformersLoader(default_model_name="meta-llama/Llama-3.2-1B")
    tok = loader.load_tokenizer()
    mdl = loader.load_model()
    assert tok is not None
    assert mdl is not None


def test_production_hf_uploader(tmp_path):
    """Test ProductionHuggingFaceUploader workflow."""
    folder = tmp_path / "hf_bundle"
    folder.mkdir()
    (folder / "README.md").write_text("# Test Dataset Documentation Card", encoding="utf-8")

    uploader = ProductionHuggingFaceUploader()
    log_meta = uploader.upload_dataset_repo(folder, "dataset-genome/test-upload")

    assert log_meta["status"] == "SUCCESS"
    assert log_meta["repository"] == "dataset-genome/test-upload"
