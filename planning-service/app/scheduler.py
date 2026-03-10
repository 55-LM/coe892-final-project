"""
Schedule and route generation logic for the Planning Service.
Generates weekly schedules and daily truck routes based on collection rules and city data.
"""

from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from .database import (
    NeighbourhoodModel,
    HouseModel,
    CollectionRuleModel,
    WeeklyScheduleModel,
    RouteModel,
)
from .models import WasteType, RouteStop


def get_week_start(d: date) -> date:
    """Return Monday of the week containing d."""
    return d - timedelta(days=d.weekday())


def generate_weekly_schedule(db: Session, week_start: Optional[date] = None) -> list[WeeklyScheduleModel]:
    """
    Generate weekly collection schedule: for each neighbourhood and waste type,
    assign a day based on collection rules. Weekdays only (0=Mon .. 4=Fri).
    """
    if week_start is None:
        week_start = get_week_start(date.today())

    # Clear existing schedule for this week
    db.query(WeeklyScheduleModel).filter(WeeklyScheduleModel.week_start == week_start).delete()

    neighbourhoods = db.query(NeighbourhoodModel).all()
    rules = db.query(CollectionRuleModel).all()
    created = []

    for n in neighbourhoods:
        for rule in rules:
            schedule = WeeklyScheduleModel(
                neighbourhood_id=n.id,
                waste_type=rule.waste_type,
                scheduled_day=rule.assigned_day,
                week_start=week_start,
            )
            db.add(schedule)
            db.flush()
            created.append(schedule)

    return created


def generate_daily_routes(
    db: Session,
    route_date: date,
    neighbourhood_id: Optional[int] = None,
    waste_type: Optional[str] = None,
) -> list[RouteModel]:
    """
    Generate routes for a given day. Each route is one truck, one neighbourhood, one waste type.
    Stops are a simple ordered list of houses that have that bin type in that neighbourhood.
    """
    week_start = get_week_start(route_date)
    day_of_week = route_date.weekday()  # 0=Monday .. 4=Friday
    if day_of_week > 4:
        return []  # No collection on weekend

    # Get schedule entries for this day
    schedule_q = db.query(WeeklyScheduleModel).filter(
        WeeklyScheduleModel.week_start == week_start,
        WeeklyScheduleModel.scheduled_day == day_of_week,
    )
    if neighbourhood_id is not None:
        schedule_q = schedule_q.filter(WeeklyScheduleModel.neighbourhood_id == neighbourhood_id)
    if waste_type is not None:
        schedule_q = schedule_q.filter(WeeklyScheduleModel.waste_type == waste_type)

    schedule_entries = schedule_q.all()
    routes_created = []

    for entry in schedule_entries:
        # Houses in this neighbourhood that support this waste type
        houses_q = db.query(HouseModel).filter(
            HouseModel.neighbourhood_id == entry.neighbourhood_id,
        )
        houses = houses_q.all()
        # Filter by bin_types_supported (JSON list)
        stops_list = []
        for idx, h in enumerate(houses):
            if entry.waste_type in (h.bin_types_supported or []):
                stops_list.append({
                    "house_id": h.id,
                    "address": h.address,
                    "order_index": idx,
                })

        if not stops_list:
            continue

        truck_id = f"T-{entry.neighbourhood_id}-{entry.waste_type[:2].upper()}-{route_date.isoformat().replace('-','')}"
        route = RouteModel(
            truck_id=truck_id,
            date=route_date,
            neighbourhood_id=entry.neighbourhood_id,
            waste_type=entry.waste_type,
            stops=stops_list,
        )
        db.add(route)
        db.flush()
        routes_created.append(route)

    return routes_created
