"""
Response models for Analytics Service.
Metrics are computed from Operations (pickup events) and Planning (houses, neighbourhoods).
"""

from pydantic import BaseModel
from typing import Optional


class SummaryMetrics(BaseModel):
    total_pickups_completed: int
    total_pickups_missed: int
    total_pickups_delayed: int
    total_pickups: int
    completion_rate: float  # 0-100
    active_route_count: Optional[int] = None


class NeighbourhoodMetric(BaseModel):
    neighbourhood_id: int
    neighbourhood_name: str
    completed: int
    missed: int
    delayed: int
    total: int
    completion_rate: float


class WasteTypeMetric(BaseModel):
    waste_type: str
    completed: int
    missed: int
    delayed: int
    total: int
    completion_rate: float


class MissedPickupItem(BaseModel):
    id: int
    route_id: int
    house_id: int
    waste_type: str
    timestamp: str
    status: str
