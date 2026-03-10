"""
REST API routes for the Operations Service.
Pickup events and route simulation.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .database import get_db, init_db, PickupEventModel
from .models import PickupEvent, PickupEventCreate, PickupStatus, SimulateRouteResponse
from .simulator import simulate_route

router = APIRouter()


def event_to_pydantic(m: PickupEventModel) -> PickupEvent:
    return PickupEvent(
        id=m.id,
        route_id=m.route_id,
        house_id=m.house_id,
        waste_type=m.waste_type,
        timestamp=m.timestamp or datetime.utcnow(),
        status=PickupStatus(m.status),
    )


@router.get("/health")
def health():
    return {"service": "operations", "status": "ok"}


@router.post("/simulate-route/{route_id}", response_model=SimulateRouteResponse)
def simulate_route_endpoint(
    route_id: int,
    db: Session = Depends(get_db),
):
    """Simulate waste collection for a route; creates pickup events."""
    total, completed, missed, delayed = simulate_route(db, route_id)
    if total == 0:
        raise HTTPException(
            status_code=400,
            detail="Could not load route from Planning service. Ensure Planning is running, generate routes for this date on Daily Routes, then try again.",
        )
    db.commit()
    return SimulateRouteResponse(
        route_id=route_id,
        events_created=total,
        completed=completed,
        missed=missed,
        delayed=delayed,
    )


@router.post("/pickup-events", response_model=PickupEvent)
def create_pickup_event(
    body: PickupEventCreate,
    db: Session = Depends(get_db),
):
    """Manually record a pickup event (e.g. from external system)."""
    from datetime import datetime
    event = PickupEventModel(
        route_id=body.route_id,
        house_id=body.house_id,
        waste_type=body.waste_type,
        timestamp=body.timestamp or datetime.utcnow(),
        status=body.status.value,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event_to_pydantic(event)


@router.get("/pickup-events", response_model=list[PickupEvent])
def list_pickup_events(
    route_id: Optional[int] = Query(None),
    limit: int = Query(500, le=5000),
    db: Session = Depends(get_db),
):
    """List pickup events, optionally filtered by route_id."""
    q = db.query(PickupEventModel).order_by(PickupEventModel.timestamp.desc())
    if route_id is not None:
        q = q.filter(PickupEventModel.route_id == route_id)
    rows = q.limit(limit).all()
    return [event_to_pydantic(r) for r in rows]


@router.get("/pickup-events/route/{route_id}", response_model=list[PickupEvent])
def list_pickup_events_by_route(route_id: int, db: Session = Depends(get_db)):
    """List all pickup events for a specific route."""
    rows = db.query(PickupEventModel).filter(PickupEventModel.route_id == route_id).order_by(PickupEventModel.timestamp).all()
    return [event_to_pydantic(r) for r in rows]
