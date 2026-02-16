"""
FastAPI application entry-point.

- Initialises DB tables on startup
- Starts MQTT subscriber background thread
- Registers all API routers
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models import SensorData, Alert  # noqa: F401 – ensure models are imported
from app.routers import sensor_data, alerts, dashboard
from app.services.mqtt_service import mqtt_subscriber

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("energy")


# ── Lifespan (startup / shutdown) ────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Creating database tables (if not exist)…")
    Base.metadata.create_all(bind=engine)

    logger.info("Starting MQTT subscriber…")
    mqtt_subscriber.start()

    yield

    # Shutdown
    logger.info("Stopping MQTT subscriber…")
    mqtt_subscriber.stop()


# ── App ──────────────────────────────────────────────────────
app = FastAPI(
    title="Energy Sensor Monitoring API",
    description="Real-time sensor data ingestion via MQTT with threshold-based alerting.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS – allow the React frontend (dev port 3000 + prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(dashboard.router)
app.include_router(sensor_data.router)
app.include_router(alerts.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Energy Sensor Monitoring API"}
