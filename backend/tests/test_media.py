"""Unit tests for VeriClip AI media endpoint."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_media():
    payload = {
        "title": "IPL 2026 Match 15",
        "original_url": "https://example.com/ipl-match-15.mp4",
        "content_type": "video/mp4"
    }
    response = client.post("/api/v1/media", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "media_asset_id" in data
    assert data["title"] == "IPL 2026 Match 15"


def test_list_media():
    response = client.get("/api/v1/media")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
