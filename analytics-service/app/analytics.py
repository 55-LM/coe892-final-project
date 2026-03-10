"""
Analytics logic: fetches pickup events from Operations Service and
house/neighbourhood data from Planning Service, then computes metrics.
Demonstrates distributed data flow: operations -> analytics, planning -> analytics.
"""

import os
from collections import defaultdict

import httpx

OPERATIONS_SERVICE_URL = os.environ.get("OPERATIONS_SERVICE_URL", "http://localhost:8001")
PLANNING_SERVICE_URL = os.environ.get("PLANNING_SERVICE_URL", "http://localhost:8000")


def fetch_pickup_events(limit: int = 5000) -> list[dict]:
    """Fetch all pickup events from Operations Service."""
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.get(f"{OPERATIONS_SERVICE_URL}/api/pickup-events", params={"limit": limit})
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return []


def fetch_houses() -> list[dict]:
    """Fetch houses from Planning Service (for house_id -> neighbourhood_id)."""
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(f"{PLANNING_SERVICE_URL}/api/houses")
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return []


def fetch_neighbourhoods() -> list[dict]:
    """Fetch neighbourhoods from Planning Service."""
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(f"{PLANNING_SERVICE_URL}/api/neighbourhoods")
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return []


def fetch_routes_count() -> int:
    """Optional: count of routes from Planning (e.g. for 'active' count)."""
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(f"{PLANNING_SERVICE_URL}/api/routes")
            if r.status_code == 200:
                return len(r.json())
    except Exception:
        pass
    return 0


def compute_summary(events: list[dict], routes_count: int | None = None) -> dict:
    completed = sum(1 for e in events if e.get("status") == "completed")
    missed = sum(1 for e in events if e.get("status") == "missed")
    delayed = sum(1 for e in events if e.get("status") == "delayed")
    total = len(events)
    rate = (completed / total * 100) if total else 0.0
    return {
        "total_pickups_completed": completed,
        "total_pickups_missed": missed,
        "total_pickups_delayed": delayed,
        "total_pickups": total,
        "completion_rate": round(rate, 2),
        "active_route_count": routes_count,
    }


def compute_by_neighbourhood(
    events: list[dict],
    houses: list[dict],
    neighbourhoods: list[dict],
) -> list[dict]:
    house_to_n = {h["id"]: h["neighbourhood_id"] for h in houses}
    n_to_name = {n["id"]: n["name"] for n in neighbourhoods}
    by_n = defaultdict(lambda: {"completed": 0, "missed": 0, "delayed": 0})
    for e in events:
        nid = house_to_n.get(e.get("house_id"))
        if nid is None:
            continue
        status = e.get("status", "completed")
        if status == "completed":
            by_n[nid]["completed"] += 1
        elif status == "missed":
            by_n[nid]["missed"] += 1
        else:
            by_n[nid]["delayed"] += 1
    result = []
    for nid, counts in by_n.items():
        total = counts["completed"] + counts["missed"] + counts["delayed"]
        rate = (counts["completed"] / total * 100) if total else 0
        result.append({
            "neighbourhood_id": nid,
            "neighbourhood_name": n_to_name.get(nid, f"Neighbourhood {nid}"),
            "completed": counts["completed"],
            "missed": counts["missed"],
            "delayed": counts["delayed"],
            "total": total,
            "completion_rate": round(rate, 2),
        })
    return sorted(result, key=lambda x: -x["total"])


def compute_by_waste_type(events: list[dict]) -> list[dict]:
    by_type = defaultdict(lambda: {"completed": 0, "missed": 0, "delayed": 0})
    for e in events:
        wt = e.get("waste_type", "garbage")
        status = e.get("status", "completed")
        if status == "completed":
            by_type[wt]["completed"] += 1
        elif status == "missed":
            by_type[wt]["missed"] += 1
        else:
            by_type[wt]["delayed"] += 1
    result = []
    for wt, counts in by_type.items():
        total = counts["completed"] + counts["missed"] + counts["delayed"]
        rate = (counts["completed"] / total * 100) if total else 0
        result.append({
            "waste_type": wt,
            "completed": counts["completed"],
            "missed": counts["missed"],
            "delayed": counts["delayed"],
            "total": total,
            "completion_rate": round(rate, 2),
        })
    return sorted(result, key=lambda x: -x["total"])


def get_missed_pickups(events: list[dict], limit: int = 100) -> list[dict]:
    missed = [e for e in events if e.get("status") == "missed"]
    missed.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return missed[:limit]
