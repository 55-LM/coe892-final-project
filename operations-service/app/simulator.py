"""
Simulates waste collection for a route: fetches route from Planning Service,
generates pickup events (completed/missed/delayed) and stores them.
Reflects near-real-time updates by creating events with timestamps.
"""

import os
import random
from datetime import datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from .database import PickupEventModel
from .models import PickupStatus

# Planning service base URL (set PLANNING_SERVICE_URL for Docker; default for local)
PLANNING_SERVICE_URL = os.environ.get("PLANNING_SERVICE_URL", "http://localhost:8000")


def fetch_route(route_id: int, base_url: str = PLANNING_SERVICE_URL) -> dict | None:
    """Fetch route details from Planning Service."""
    url = f"{base_url.rstrip('/')}/api/routes/{route_id}"
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(url)
            if r.status_code == 200:
                return r.json()
    except Exception as e:
        # Log for debugging (e.g. connection refused if Planning not running)
        import logging
        logging.getLogger(__name__).warning("Failed to fetch route %s from Planning: %s", route_id, e)
    return None


def simulate_route(
    db: Session,
    route_id: int,
    planning_base_url: str = PLANNING_SERVICE_URL,
    miss_chance: float = 0.05,
    delay_chance: float = 0.08,
) -> tuple[int, int, int, int]:
    """
    Simulate pickups for a route. Fetches route from Planning Service,
    creates one event per stop with status completed/missed/delayed.
    Returns (events_created, completed, missed, delayed).
    """
    route = fetch_route(route_id, planning_base_url)
    if not route or not route.get("stops"):
        return 0, 0, 0, 0

    stops = route["stops"]
    waste_type = route.get("waste_type", "garbage")
    # Simulate start time within 7 AM - 5 PM
    base_time = datetime.utcnow().replace(hour=7, minute=0, second=0, microsecond=0)
    completed = missed = delayed = 0

    for i, stop in enumerate(stops):
        house_id = stop.get("house_id")
        if house_id is None:
            continue
        # Random status for simulation
        rnd = random.random()
        if rnd < miss_chance:
            status = PickupStatus.missed
            missed += 1
        elif rnd < miss_chance + delay_chance:
            status = PickupStatus.delayed
            delayed += 1
        else:
            status = PickupStatus.completed
            completed += 1

        event_time = base_time + timedelta(minutes=i * 3)  # ~3 min per stop
        event = PickupEventModel(
            route_id=route_id,
            house_id=house_id,
            waste_type=waste_type,
            timestamp=event_time,
            status=status.value,
        )
        db.add(event)

    db.flush()
    total = completed + missed + delayed
    return total, completed, missed, delayed
