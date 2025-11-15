# app/main.py
from fastapi import FastAPI

from app.db import Base, engine
from app.routers import flights as flights_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Flight Service")

app.include_router(flights_router.router)
