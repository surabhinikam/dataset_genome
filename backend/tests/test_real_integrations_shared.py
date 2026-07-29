"""
tests/test_real_integrations_shared.py — Unit tests for shared credentials, exceptions, and validators.
"""

from pathlib import Path
import pytest

from app.integrations.shared import (
    ArtifactValidator,
    DatasetGenomeIntegrationError,
    IntegrationCredentials,
    ValidationError,
    get_credentials,
)


def test_credentials_loader():
    """Test get_credentials loads IntegrationCredentials model."""
    creds = get_credentials()
    assert isinstance(creds, IntegrationCredentials)


def test_artifact_validator(tmp_path):
    """Test ArtifactValidator verifies datasets, metadata, READMEs, and licenses."""
    validator = ArtifactValidator()

    # 1. Dataset file validation
    ds_path = tmp_path / "train.jsonl"
    ds_path.write_text('{"id": "rec-1"}', encoding="utf-8")
    assert validator.validate_dataset_file(ds_path) is True

    # 2. Metadata file validation
    meta_path = tmp_path / "metadata.json"
    meta_path.write_text('{"version": "v1.0"}', encoding="utf-8")
    assert validator.validate_metadata_file(meta_path) is True

    # 3. README file validation
    readme_path = tmp_path / "README.md"
    readme_path.write_text("# Dataset Genome Documentation Card Header", encoding="utf-8")
    assert validator.validate_readme_file(readme_path) is True

    # 4. Invalid metadata rejection
    bad_meta = tmp_path / "bad.json"
    bad_meta.write_text("invalid json content", encoding="utf-8")
    with pytest.raises(ValidationError):
        validator.validate_metadata_file(bad_meta)
