"""
Data models for the Operations Service.
Pickup events and simulation requests. Does not store city/route structure;
that comes from the Planning Service via API or passed payloads.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class PickupStatus(str, Enum):
    completed = "completed"
    missed = "missed"
    delayed = "delayed"


class PickupEventBase(BaseModel):
    route_id: int
    house_id: int
    waste_type: str
    timestamp: Optional[datetime] = None
    status: PickupStatus = PickupStatus.completed


class PickupEventCreate(PickupEventBase):
    pass


class PickupEvent(PickupEventBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class SimulateRouteResponse(BaseModel):
    route_id: int
    events_created: int
    completed: int
    missed: int
    delayed: int
