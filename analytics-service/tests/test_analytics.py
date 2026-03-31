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
    assert data.get("service") == "analytics"
    assert data.get("status") == "ok"


def test_metrics_summary():
    r = client.get("/api/metrics/summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_pickups_completed" in data
    assert "completion_rate" in data
