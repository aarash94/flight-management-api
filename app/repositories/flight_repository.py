# app/repositories/flight_repository.py
from typing import Optional, Tuple, List

from sqlalchemy import select, func, asc, desc
from sqlalchemy.orm import Session

from app import models
from app.schemas import FlightCreate, FlightUpdate, FlightStatus


SORTABLE_FIELDS = {
    "flight_number": models.Flight.flight_number,
    "departure_time": models.Flight.departure_time,
    "arrival_time": models.Flight.arrival_time,
    "created_at": models.Flight.created_at,
    "updated_at": models.Flight.updated_at,
    "seats_available": models.Flight.seats_available,
}


def create_flight(db: Session, flight_in: FlightCreate) -> models.Flight:
    # Creates a flight ORM entity and saves it to the database.
    duration = int(
        (flight_in.arrival_time - flight_in.departure_time).total_seconds() // 60
    )
    seats_available = (
        flight_in.seats_available
        if flight_in.seats_available is not None
        else flight_in.seats_total
    )
    status = flight_in.status or FlightStatus.scheduled

    db_flight = models.Flight(
        flight_number=flight_in.flight_number,
        origin=flight_in.origin,
        destination=flight_in.destination,
        departure_time=flight_in.departure_time,
        arrival_time=flight_in.arrival_time,
        duration_minutes=duration,
        aircraft_type=flight_in.aircraft_type,
        seats_total=flight_in.seats_total,
        seats_available=seats_available,
        status=status,
        process_id=flight_in.process_id,
    )
    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    return db_flight


def get_flight(db: Session, flight_id: int) -> Optional[models.Flight]:
    # Fetches a flight row by its primary key.
    return db.get(models.Flight, flight_id)


def list_flights(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 10,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    status: Optional[FlightStatus] = None,
    process_id: Optional[str] = None,
    sort_by: str = "departure_time",
    sort_order: str = "asc",
) -> Tuple[List[models.Flight], int]:
    # Returns a filtered list of flights plus a count for pagination.
    stmt = select(models.Flight)
    count_stmt = select(func.count(models.Flight.flight_id))

    def apply_filters(q):
        # Applies any optional filters to a SQLAlchemy select statement.
        if origin:
            q = q.where(models.Flight.origin == origin)
        if destination:
            q = q.where(models.Flight.destination == destination)
        if status:
            q = q.where(models.Flight.status == status)
        if process_id:
            q = q.where(models.Flight.process_id == process_id)
        return q

    stmt = apply_filters(stmt)
    count_stmt = apply_filters(count_stmt)

    total = db.execute(count_stmt).scalar() or 0

    sort_col = SORTABLE_FIELDS.get(sort_by, models.Flight.departure_time)
    if sort_order.lower() == "desc":
        stmt = stmt.order_by(desc(sort_col))
    else:
        stmt = stmt.order_by(asc(sort_col))

    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    flights = db.execute(stmt).scalars().all()
    return flights, total


def update_flight(db: Session, db_flight: models.Flight, flight_in: FlightUpdate) -> models.Flight:
    # Updates a flight row in place and recalculates derived fields if needed.
    data = flight_in.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(db_flight, field, value)

    if any(k in data for k in ("departure_time", "arrival_time")):
        if db_flight.departure_time and db_flight.arrival_time:
            db_flight.duration_minutes = int(
                (db_flight.arrival_time - db_flight.departure_time).total_seconds()
                // 60
            )

    db.commit()
    db.refresh(db_flight)
    return db_flight


def delete_flight(db: Session, db_flight: models.Flight) -> None:
    # Deletes a flight row permanently.
    db.delete(db_flight)
    db.commit()
