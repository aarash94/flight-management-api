# app/routers/flights.py
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import (
    FlightCreate,
    FlightUpdate,
    FlightStatus,
    APIResponse,
)
from app.services.flight_service import (
    create_flight,
    get_flight_by_id,
    list_flights_service,
    update_flight_service,
    delete_flight_service,
)

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
# Handles POST /flights by creating a new flight record.
def create_flight_endpoint(
    flight_in: FlightCreate,
    db: Session = Depends(get_db),
):
    flight = create_flight(db, flight_in)
    return APIResponse(
        status="success",
        message="Flight created",
        data=flight,
    )


@router.get("/{flight_id}", response_model=APIResponse)
# Handles GET /flights/{flight_id} to fetch a single flight.
def get_flight_endpoint(
    flight_id: int,
    db: Session = Depends(get_db),
):
    flight = get_flight_by_id(db, flight_id)
    return APIResponse(
        status="success",
        message="Flight retrieved",
        data=flight,
    )


@router.get("/", response_model=APIResponse)
# Lists flights with optional filters, paging, and sorting.
def list_flights_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    status: Optional[FlightStatus] = None,
    process_id: Optional[str] = None,
    sort_by: str = Query("departure_time"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    result = list_flights_service(
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
    return APIResponse(
        status="success",
        message="Flights list",
        data=result,
    )


@router.put("/{flight_id}", response_model=APIResponse)
# Handles PUT /flights/{flight_id} to update an existing flight.
def update_flight_endpoint(
    flight_id: int,
    flight_in: FlightUpdate,
    db: Session = Depends(get_db),
):
    updated = update_flight_service(db, flight_id, flight_in)
    return APIResponse(
        status="success",
        message="Flight updated",
        data=updated,
    )


@router.delete("/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
# Deletes a flight and returns an empty 204 response.
def delete_flight_endpoint(
    flight_id: int,
    db: Session = Depends(get_db),
):
    delete_flight_service(db, flight_id)
    # 204 responses must not include a body, so we end the request here.
    return
