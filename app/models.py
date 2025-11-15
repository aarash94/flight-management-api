# app/models.py
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum as SAEnum,
)

from app.db import Base


class FlightStatus(str, Enum):
    scheduled = "scheduled"
    departed = "departed"
    arrived = "arrived"
    delayed = "delayed"
    cancelled = "cancelled"


class Flight(Base):
    __tablename__ = "flights"

    flight_id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String(20), unique=True, index=True, nullable=False)
    origin = Column(String(10), index=True, nullable=False)
    destination = Column(String(10), index=True, nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    aircraft_type = Column(String(50), nullable=False)
    seats_total = Column(Integer, nullable=False)
    seats_available = Column(Integer, nullable=False)
    status = Column(SAEnum(FlightStatus), default=FlightStatus.scheduled, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    process_id = Column(String(20), nullable=True)
