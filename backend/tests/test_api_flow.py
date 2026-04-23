"""Integration tests for VeriClip AI API flow."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_end_to_end_case_flow():
    """Test complete flow: health -> create media -> create case -> list cases."""
    # Health check
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200

    # Create media
    media_payload = {"title": "Test Media", "original_url": "https://example.com/test.mp4", "content_type": "video/mp4"}
    resp = client.post("/api/v1/media", json=media_payload)
    assert resp.status_code == 201
    media_id = resp.json()["media_asset_id"]

    # Create case
    case_payload = {"media_asset_id": media_id, "source_url": "https://example.com/infringement", "confidence": 0.9, "decision": "flag", "explanation": "End-to-end test case for infringement detection"}
    resp = client.post("/api/v1/cases", json=case_payload)
    assert resp.status_code == 201

    # List cases
    resp = client.get("/api/v1/cases")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 2
