"""
Planning Service - Entry point.
Responsible for city data, weekly schedules, and daily route generation.
Part of the distributed Real-Time City Waste Collection Management System.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.seed_data import run_seed
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """On startup: init DB and seed mock data if empty."""
    init_db()
    run_seed()
    yield
    # shutdown if needed
    pass


app = FastAPI(
    title="Planning Service",
    description="City data, weekly schedules, and daily route generation for waste collection.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api", tags=["planning"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
