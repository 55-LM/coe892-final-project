"""
REST API routes for the Planning Service.
Exposes neighbourhoods, houses, schedule generation, and route generation.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .database import get_db, init_db, NeighbourhoodModel, HouseModel, CollectionRuleModel, WeeklyScheduleModel, RouteModel
from .models import (
    Neighbourhood,
    House,
    WeeklyScheduleItem,
    Route,
    RouteStop,
    WasteType,
    GenerateScheduleRequest,
    GenerateRouteRequest,
)
from .seed_data import run_seed
from .scheduler import generate_weekly_schedule, generate_daily_routes

router = APIRouter()


def neighbourhood_to_pydantic(m: NeighbourhoodModel) -> Neighbourhood:
    return Neighbourhood(id=m.id, name=m.name)


def house_to_pydantic(m: HouseModel) -> House:
    return House(
        id=m.id,
        address=m.address,
        neighbourhood_id=m.neighbourhood_id,
        estimated_residents=m.estimated_residents or 1,
        bin_types_supported=[WasteType(t) for t in (m.bin_types_supported or ["garbage"])],
    )


def schedule_to_pydantic(m: WeeklyScheduleModel) -> WeeklyScheduleItem:
    return WeeklyScheduleItem(
        id=m.id,
        neighbourhood_id=m.neighbourhood_id,
        waste_type=WasteType(m.waste_type),
        scheduled_day=m.scheduled_day,
    )


def route_to_pydantic(m: RouteModel) -> Route:
    return Route(
        id=m.id,
        truck_id=m.truck_id,
        date=m.date,
        neighbourhood_id=m.neighbourhood_id,
        waste_type=WasteType(m.waste_type),
        stops=[RouteStop(**s) for s in (m.stops or [])],
    )


@router.get("/health")
def health():
    return {"service": "planning", "status": "ok"}


@router.get("/neighbourhoods", response_model=list[Neighbourhood])
def list_neighbourhoods(db: Session = Depends(get_db)):
    """List all neighbourhoods."""
    rows = db.query(NeighbourhoodModel).all()
    return [neighbourhood_to_pydantic(r) for r in rows]


@router.get("/houses", response_model=list[House])
def list_houses(
    neighbourhood_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """List houses, optionally filtered by neighbourhood."""
    q = db.query(HouseModel)
    if neighbourhood_id is not None:
        q = q.filter(HouseModel.neighbourhood_id == neighbourhood_id)
    rows = q.all()
    return [house_to_pydantic(r) for r in rows]


@router.post("/generate-schedule", response_model=list[WeeklyScheduleItem])
def generate_schedule(
    body: Optional[GenerateScheduleRequest] = None,
    db: Session = Depends(get_db),
):
    """Generate weekly collection schedule. Optionally specify week_start."""
    week_start = body.week_start if body else None
    created = generate_weekly_schedule(db, week_start)
    db.commit()
    return [schedule_to_pydantic(c) for c in created]


@router.get("/schedule", response_model=list[WeeklyScheduleItem])
def get_schedule(
    week_start: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Get weekly schedule. If week_start not given, use current week."""
    from .scheduler import get_week_start
    ws = week_start or get_week_start(date.today())
    rows = db.query(WeeklyScheduleModel).filter(WeeklyScheduleModel.week_start == ws).all()
    return [schedule_to_pydantic(r) for r in rows]


@router.post("/generate-route", response_model=list[Route])
def generate_route(
    body: GenerateRouteRequest,
    db: Session = Depends(get_db),
):
    """Generate daily routes for a given date. Optionally filter by neighbourhood or waste type."""
    nid = body.neighbourhood_id
    wt = body.waste_type.value if body.waste_type else None
    created = generate_daily_routes(db, body.date, neighbourhood_id=nid, waste_type=wt)
    db.commit()
    return [route_to_pydantic(c) for c in created]


@router.get("/routes", response_model=list[Route])
def list_routes(
    date_param: Optional[date] = Query(None, alias="date"),
    neighbourhood_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """List routes, optionally by date and/or neighbourhood."""
    q = db.query(RouteModel)
    if date_param is not None:
        q = q.filter(RouteModel.date == date_param)
    if neighbourhood_id is not None:
        q = q.filter(RouteModel.neighbourhood_id == neighbourhood_id)
    rows = q.all()
    return [route_to_pydantic(r) for r in rows]


@router.get("/routes/{route_id}", response_model=Route)
def get_route(route_id: int, db: Session = Depends(get_db)):
    """Get a single route by ID."""
    r = db.query(RouteModel).filter(RouteModel.id == route_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Route not found")
    return route_to_pydantic(r)
