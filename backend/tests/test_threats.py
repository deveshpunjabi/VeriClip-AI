"""Integration tests for threat scanning and takedown."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_scan_for_threats():
    response = client.post("/api/v1/scan", json={"query": "IPL 2026 live stream free"})
    assert response.status_code == 201
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_list_threats():
    client.post("/api/v1/scan", json={"query": "cricket highlights"})
    response = client.get("/api/v1/threats")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_verify_threat_not_found():
    response = client.post("/api/v1/verify/9999")
    assert response.status_code == 404


def test_list_events():
    response = client.get("/api/v1/events")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_list_notices():
    response = client.get("/api/v1/notices")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
