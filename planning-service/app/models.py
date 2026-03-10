"""
Data models for the Planning Service.
Represents city structure: neighbourhoods, houses, collection rules, schedules, and routes.
"""

from datetime import date, time
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WasteType(str, Enum):
    """Supported waste types for collection."""
    garbage = "garbage"
    recycling = "recycling"
    organics = "organics"


# --- Request/Response DTOs ---

class NeighbourhoodBase(BaseModel):
    name: str


class NeighbourhoodCreate(NeighbourhoodBase):
    pass


class Neighbourhood(NeighbourhoodBase):
    id: int

    class Config:
        from_attributes = True


class HouseBase(BaseModel):
    address: str
    neighbourhood_id: int
    estimated_residents: int = Field(ge=1, le=20)
    bin_types_supported: list[WasteType] = Field(default_factory=lambda: [WasteType.garbage])


class HouseCreate(HouseBase):
    pass


class House(HouseBase):
    id: int

    class Config:
        from_attributes = True


class CollectionRuleBase(BaseModel):
    waste_type: WasteType
    assigned_day: int  # 0=Monday .. 4=Friday
    frequency: str = "weekly"
    allowed_time_start: str = "07:00"  # 7 AM
    allowed_time_end: str = "17:00"   # 5 PM


class CollectionRule(CollectionRuleBase):
    id: int

    class Config:
        from_attributes = True


class WeeklyScheduleItem(BaseModel):
    id: Optional[int] = None
    neighbourhood_id: int
    waste_type: WasteType
    scheduled_day: int  # 0=Monday .. 4=Friday

    class Config:
        from_attributes = True


class RouteStop(BaseModel):
    house_id: int
    address: str
    order_index: int


class RouteBase(BaseModel):
    truck_id: str
    date: date
    neighbourhood_id: int
    waste_type: WasteType
    stops: list[RouteStop] = Field(default_factory=list)


class Route(RouteBase):
    id: int

    class Config:
        from_attributes = True


class GenerateScheduleRequest(BaseModel):
    week_start: Optional[date] = None  # defaults to current week


class GenerateRouteRequest(BaseModel):
    date: date
    neighbourhood_id: Optional[int] = None  # if None, generate for all
    waste_type: Optional[WasteType] = None  # if None, generate for all types that day
