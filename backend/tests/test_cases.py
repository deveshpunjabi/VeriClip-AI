"""Unit tests for VeriClip AI cases endpoint."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_cases():
    response = client.get("/api/v1/cases")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1  # Has seed case


def test_create_case():
    payload = {
        "media_asset_id": "asset_test_001",
        "source_url": "https://example.com/test",
        "confidence": 0.85,
        "decision": "flag",
        "explanation": "Automated test case for verification"
    }
    response = client.post("/api/v1/cases", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "case_id" in data
    assert data["media_asset_id"] == "asset_test_001"
