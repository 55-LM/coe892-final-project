"""
Basic tests for Planning Service API.
Run from planning-service: pytest
"""

import pytest
from fastapi.testclient import TestClient

# Import after setting up path so app can load
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("service") == "planning"
    assert data.get("status") == "ok"


def test_neighbourhoods():
    r = client.get("/api/neighbourhoods")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Seed creates 5 neighbourhoods
    assert len(data) >= 1
    assert "name" in data[0] and "id" in data[0]


def test_houses():
    r = client.get("/api/houses")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_schedule_empty_or_exists():
    r = client.get("/api/schedule")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_generate_schedule():
    r = client.post("/api/generate-schedule", json={})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
