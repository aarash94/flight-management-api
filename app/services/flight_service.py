# app/services/flight_service.py
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.schemas import (
    FlightCreate,
    FlightUpdate,
    FlightOut,
    PaginatedFlights,
    FlightStatus,
)
from app.repositories.flight_repository import (
    create_flight as repo_create,
    get_flight as repo_get,
    list_flights as repo_list,
    update_flight as repo_update,
    delete_flight as repo_delete,
)


def create_flight(db: Session, flight_in: FlightCreate) -> FlightOut:
    # Persists a new flight after handling constraint errors.
    try:
        flight = repo_create(db, flight_in)
        return FlightOut.from_orm(flight)
    except IntegrityError as e:
        db.rollback()
        if "UNIQUE constraint failed: flights.flight_number" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Flight number already exists"
            )
        raise

def get_flight_by_id(db: Session, flight_id: int) -> FlightOut:
    # Looks up a flight by id and raises 404 if it is missing.
    flight = repo_get(db, flight_id)
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found",
        )
    return FlightOut.from_orm(flight)


def list_flights_service(
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
) -> PaginatedFlights:
    # Retrieves a filtered, paged list of flights plus a total count.
    flights, total = repo_list(
        db,
        page=page,
        page_size=page_size,
        origin=origin,
        destination=destination,
        status=status,
        process_id=process_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return PaginatedFlights(
        items=[FlightOut.from_orm(f) for f in flights],
        total=total,
        page=page,
        page_size=page_size,
    )


def update_flight_service(db: Session, flight_id: int, flight_in: FlightUpdate) -> FlightOut:
    # Applies updates to a flight and returns the refreshed object.
    db_flight = repo_get(db, flight_id)
    if not db_flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found",
        )
    updated = repo_update(db, db_flight, flight_in)
    return FlightOut.from_orm(updated)


def delete_flight_service(db: Session, flight_id: int) -> None:
    # Removes a flight from the database or raises if it does not exist.
    db_flight = repo_get(db, flight_id)
    if not db_flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found",
        )
    repo_delete(db, db_flight)
