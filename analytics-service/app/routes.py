#REST API routes for the Analytics Service
#metrics are computed by aggregating data from Operations and Planning services

from fastapi import APIRouter, Query

from .analytics import (
    fetch_pickup_events,
    fetch_houses,
    fetch_neighbourhoods,
    fetch_routes_count,
    compute_summary,
    compute_by_neighbourhood,
    compute_by_waste_type,
    get_missed_pickups,
)
from .models import SummaryMetrics, NeighbourhoodMetric, WasteTypeMetric, MissedPickupItem

router = APIRouter()


@router.get("/health")
def health():
    return {"service": "analytics", "status": "ok"}


@router.get("/metrics/summary", response_model=SummaryMetrics)
def metrics_summary():
    #total completed/missed/delayed, completion rate, active route count
    events = fetch_pickup_events()
    routes_count = fetch_routes_count()
    data = compute_summary(events, routes_count=routes_count)
    return SummaryMetrics(**data)


@router.get("/metrics/by-neighbourhood", response_model=list[NeighbourhoodMetric])
def metrics_by_neighbourhood():
    #breakdown of pickups and completion rate by neighbourhood
    events = fetch_pickup_events()
    houses = fetch_houses()
    neighbourhoods = fetch_neighbourhoods()
    data = compute_by_neighbourhood(events, houses, neighbourhoods)
    return [NeighbourhoodMetric(**d) for d in data]


@router.get("/metrics/by-waste-type", response_model=list[WasteTypeMetric])
def metrics_by_waste_type():
    #breakdown of pickups and completion rate by waste type
    events = fetch_pickup_events()
    data = compute_by_waste_type(events)
    return [WasteTypeMetric(**d) for d in data]


@router.get("/metrics/missed-pickups", response_model=list[MissedPickupItem])
def metrics_missed_pickups(limit: int = Query(100, le=500)):
    #list missed pickup events 
    events = fetch_pickup_events()
    missed = get_missed_pickups(events, limit=limit)
    return [
        MissedPickupItem(
            id=e.get("id"),
            route_id=e.get("route_id"),
            house_id=e.get("house_id"),
            waste_type=e.get("waste_type", ""),
            timestamp=str(e.get("timestamp", "")),
            status=e.get("status", "missed"),
        )
        for e in missed
    ]
