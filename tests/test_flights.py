# tests/test_flights.py
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_get_flight():
    # Verifies that a flight can be created and then read back from the API.
    payload = {
        "flight_number": "SP9999",
        "origin": "IKA",
        "destination": "MHD",
        "departure_time": "2025-11-10T10:00:00",
        "arrival_time": "2025-11-10T11:30:00",
        "aircraft_type": "A320",
        "seats_total": 150,
        "process_id": "P-999",
    }

    resp = client.post("/flights/", json=payload)
    assert resp.status_code == 201

    body = resp.json()
    assert body["status"] == "success"
    flight = body["data"]
    assert flight["flight_number"] == "SP9999"

    flight_id = flight["flight_id"]

    get_resp = client.get(f"/flights/{flight_id}")
    assert get_resp.status_code == 200
    get_body = get_resp.json()
    assert get_body["data"]["flight_id"] == flight_id
