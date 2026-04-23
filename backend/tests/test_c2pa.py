"""Unit tests for C2PA service."""
import pytest
from app.services.c2pa_service import C2PAService
from app.models.c2pa_manifest import C2PAManifest


def test_c2pa_manifest_creation():
    manifest = C2PAManifest(
        manifest_id="manifest_test_001",
        media_asset_id="asset_001",
        sequence_number=1,
    )
    assert manifest.manifest_id.startswith("manifest_")
    assert manifest.sequence_number == 1


def test_c2pa_service_generate_manifest():
    svc = C2PAService()
    manifest = svc.generate_manifest(
        media_asset_id="asset_test",
        sequence_number=1,
        title="Test Broadcast Segment",
    )
    assert manifest.media_asset_id == "asset_test"
    assert manifest.sequence_number == 1
    assert len(manifest.manifest_hash) == 64


def test_c2pa_service_validate_chain_valid():
    svc = C2PAService()
    m1 = svc.generate_manifest("asset_chain", 1, "Segment 1")
    m2 = svc.generate_manifest("asset_chain", 2, "Segment 2", prev_hash=m1.manifest_hash)
    result = svc.validate_chain([m1, m2])
    assert result.is_valid is True


def test_c2pa_service_validate_chain_broken():
    svc = C2PAService()
    m1 = C2PAManifest(manifest_id="manifest_m1", media_asset_id="asset_broken", sequence_number=1)
    m2 = C2PAManifest(manifest_id="manifest_m2", media_asset_id="asset_broken", sequence_number=3, prev_hash="sha256:wrong_hash")
    result = svc.validate_chain([m1, m2])
    assert result.is_valid is False
    assert len(result.errors) > 0
