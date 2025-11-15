# app/schemas.py
from datetime import datetime
from enum import Enum
from typing import Optional, List, Any

from pydantic import BaseModel, Field, validator


class FlightStatus(str, Enum):
    scheduled = "scheduled"
    departed = "departed"
    arrived = "arrived"
    delayed = "delayed"
    cancelled = "cancelled"


class FlightBase(BaseModel):
    flight_number: str = Field(..., max_length=20)
    origin: str = Field(..., max_length=10)
    destination: str = Field(..., max_length=10)
    departure_time: datetime
    arrival_time: datetime
    aircraft_type: str
    seats_total: int = Field(..., gt=0)
    seats_available: Optional[int] = Field(None, ge=0)
    status: Optional[FlightStatus] = None
    process_id: Optional[str] = None

    @validator("arrival_time")
    def arrival_after_departure(cls, v, values):
        # Guards against schedules where the arrival happens before departure.
        dep = values.get("departure_time")
        if dep and v <= dep:
            raise ValueError("arrival_time must be after departure_time")
        return v


class FlightCreate(FlightBase):
    pass


class FlightUpdate(BaseModel):
    flight_number: Optional[str] = Field(None, max_length=20)
    origin: Optional[str] = Field(None, max_length=10)
    destination: Optional[str] = Field(None, max_length=10)
    departure_time: Optional[datetime]
    arrival_time: Optional[datetime]
    aircraft_type: Optional[str]
    seats_total: Optional[int] = Field(None, gt=0)
    seats_available: Optional[int] = Field(None, ge=0)
    status: Optional[FlightStatus] = None
    process_id: Optional[str] = None


class FlightOut(BaseModel):
    flight_id: int
    flight_number: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    aircraft_type: str
    seats_total: int
    seats_available: int
    status: FlightStatus
    created_at: datetime
    updated_at: datetime
    process_id: Optional[str]

    model_config = {
        "from_attributes": True
    }


class PaginatedFlights(BaseModel):
    items: List[FlightOut]
    total: int
    page: int
    page_size: int


class APIResponse(BaseModel):
    status: str
    message: str
    data: Any = None
