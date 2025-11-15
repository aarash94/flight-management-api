# Flight Management API

This service keeps track of flights: creating them, updating their status, and letting clients page through everything that is scheduled. It is built with FastAPI, SQLAlchemy, and SQLite so it stays light enough to run locally while still feeling close to a production stack.

## What You Get
- CRUD endpoints for managing flights with validation on departure and arrival times.
- Filtering by origin, destination, status, or process id plus paging and sorting.
- Pydantic response envelopes so clients always receive the same `status / message / data` shape.
- Tests that cover the happy path for every endpoint.

## Getting Started
1. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Start the API**
   ```bash
   uvicorn app.main:app --reload
   ```
3. **Browse the docs** – visit http://localhost:8000/docs to try requests directly inside Swagger UI.

The SQLite database lives in `flights.db`. Delete the file if you ever want to start over with a clean slate.

## Example Requests
```bash
# Create a flight
curl -X POST http://localhost:8000/flights/ \
  -H "Content-Type: application/json" \
  -d '{
        "flight_number": "AC101",
        "origin": "YYZ",
        "destination": "JFK",
        "departure_time": "2024-09-01T13:30:00",
        "arrival_time": "2024-09-01T15:05:00",
        "aircraft_type": "A220",
        "seats_total": 120
      }'

# List flights with filtering and paging
curl "http://localhost:8000/flights/?origin=YYZ&page=1&page_size=5&sort_by=departure_time"
```

## Available Endpoints
| Method | Path | Description |
| --- | --- | --- |
| POST | `/flights/` | Create a flight. |
| GET | `/flights/{flight_id}` | Retrieve a single flight by id. |
| GET | `/flights/` | List flights with paging, sorting, and filters. |
| PUT | `/flights/{flight_id}` | Update any mutable field on a flight. |
| DELETE | `/flights/{flight_id}` | Remove a flight (204 No Content). |

All responses use the `APIResponse` wrapper:
```json
{
  "status": "success",
  "message": "Flight created",
  "data": { "... flight fields ..." }
}
```
Errors return the usual FastAPI problem responses (404, 409, 422, etc.).

## Running Tests
```bash
pytest
```
The tests run against an in-memory SQLite database so they stay fast and leave `flights.db` untouched.

## Configuration Notes
- Update `DATABASE_URL` in `app/db.py` if you would rather point at PostgreSQL or another RDBMS.
- Add any environment variables you need to a `.env` file (already ignored by git).
- When you deploy somewhere else, remember to run the FastAPI app with a production server such as `uvicorn --host 0.0.0.0 --workers 4 app.main:app`.

## Helpful Links
- [FastAPI docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 docs](https://docs.sqlalchemy.org/en/20/)
- [Pydantic docs](https://docs.pydantic.dev/latest/)
