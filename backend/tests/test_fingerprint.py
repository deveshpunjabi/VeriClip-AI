"""Unit tests for Fingerprint service."""
import pytest
from app.services.fingerprint_service import FingerprintService
from app.models.fingerprint import FingerprintRequest


def test_fingerprint_hash_generation():
    svc = FingerprintService()
    request = FingerprintRequest(
        media_asset_id="asset_test",
        media_url="https://example.com/video.mp4",
        media_type="video",
    )
    hash_result = svc._compute_media_hash(request)
    assert len(hash_result) == 64  # SHA256 hex length


def test_hash_similarity_identical():
    svc = FingerprintService()
    h = "abc123def456"
    assert svc._compute_hash_similarity(h, h) == 1.0


def test_hash_similarity_different():
    svc = FingerprintService()
    h1 = "aaaaaaaaaaaaaaaa"
    h2 = "bbbbbbbbbbbbbbbb"
    assert svc._compute_hash_similarity(h1, h2) == 0.0


def test_cosine_similarity_identical():
    svc = FingerprintService()
    v = [1.0, 2.0, 3.0]
    assert svc._compute_cosine_similarity(v, v) == pytest.approx(1.0)


def test_spatial_features_deterministic():
    svc = FingerprintService()
    f1 = svc._generate_spatial_features("asset_123")
    f2 = svc._generate_spatial_features("asset_123")
    assert f1 == f2


def test_temporal_features_empty_for_image():
    svc = FingerprintService()
    features = svc._generate_temporal_features("asset_img", "image")
    assert features == []
