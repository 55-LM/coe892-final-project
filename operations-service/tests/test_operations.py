"""
Basic tests for Operations Service API.
Run from operations-service: pytest
Note: simulate-route requires Planning Service; these tests only hit local endpoints.
"""

import pytest
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("service") == "operations"
    assert data.get("status") == "ok"


def test_pickup_events_list():
    r = client.get("/api/pickup-events")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
