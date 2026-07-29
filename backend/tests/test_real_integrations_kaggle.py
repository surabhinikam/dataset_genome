"""
tests/test_real_integrations_kaggle.py — Unit tests for Kaggle API wrapper and uploader.
"""

from pathlib import Path
import pytest

from app.integrations.kaggle.api import KaggleApiWrapper
from app.integrations.kaggle.auth import KaggleAuth
from app.integrations.kaggle.uploader import ProductionKaggleUploader


def test_kaggle_auth_and_api():
    """Test KaggleAuth and KaggleApiWrapper dataset existence check."""
    auth = KaggleAuth()
    assert isinstance(auth.authenticate(), bool)

    api = KaggleApiWrapper()
    url = api.create_dataset("publication/kaggle")
    assert "kaggle.com" in url


def test_production_kaggle_uploader(tmp_path):
    """Test ProductionKaggleUploader upload workflow."""
    folder = tmp_path / "kaggle_bundle"
    folder.mkdir()
    (folder / "dataset-metadata.json").write_text('{"title": "Test Kaggle Dataset"}', encoding="utf-8")

    uploader = ProductionKaggleUploader()
    log_meta = uploader.upload_dataset(folder, dataset_slug="test-kaggle-dataset")

    assert log_meta["status"] == "SUCCESS"
    assert "kaggle" in log_meta["repository"]
