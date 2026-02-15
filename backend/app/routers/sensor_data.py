"""
Sensor data API endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
import math

from app.database import get_db
from app.models import SensorData
from app.schemas import SensorDataOut, SensorDataPaginated

router = APIRouter(prefix="/api/sensor-data", tags=["Sensor Data"])


@router.get("/", response_model=SensorDataPaginated)
def get_sensor_data(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    topic: Optional[str] = Query(None, description="Filter by MQTT topic"),
    start_time: Optional[str] = Query(None, description="ISO format start time"),
    end_time: Optional[str] = Query(None, description="ISO format end time"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated raw sensor data with optional filters."""
    query = db.query(SensorData)

    if topic:
        query = query.filter(SensorData.topic == topic)
    if start_time:
        query = query.filter(SensorData.received_at >= start_time)
    if end_time:
        query = query.filter(SensorData.received_at <= end_time)

    total = query.count()
    total_pages = max(1, math.ceil(total / page_size))

    items = (
        query
        .order_by(desc(SensorData.received_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return SensorDataPaginated(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/latest", response_model=list[SensorDataOut])
def get_latest_readings(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get the most recent sensor readings."""
    items = (
        db.query(SensorData)
        .order_by(desc(SensorData.received_at))
        .limit(limit)
        .all()
    )
    return items


@router.get("/topics")
def get_unique_topics(db: Session = Depends(get_db)):
    """List all unique MQTT topics that have sent data."""
    topics = db.query(SensorData.topic).distinct().all()
    return [t[0] for t in topics]
