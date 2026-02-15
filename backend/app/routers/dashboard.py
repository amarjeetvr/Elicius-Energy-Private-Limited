"""
Dashboard API endpoint – aggregated stats for the frontend.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import SensorData, Alert
from app.schemas import DashboardStats
from app.config import settings

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardStats)
def get_dashboard(db: Session = Depends(get_db)):
    """Return aggregated dashboard statistics."""
    total_messages = db.query(SensorData).count()
    total_alerts = db.query(Alert).count()
    active_alerts = db.query(Alert).filter(Alert.resolved == 0).count()

    # Latest reading per topic
    topics = db.query(SensorData.topic).distinct().all()
    topic_list = [t[0] for t in topics]

    latest_readings = {}
    for topic_name in topic_list:
        row = (
            db.query(SensorData)
            .filter(SensorData.topic == topic_name)
            .order_by(desc(SensorData.received_at))
            .first()
        )
        if row:
            latest_readings[topic_name] = {
                "temperature": row.temperature,
                "humidity": row.humidity,
                "voltage": row.voltage,
                "current": row.current,
                "pressure": row.pressure,
                "received_at": row.received_at.isoformat() if row.received_at else None,
            }

    return DashboardStats(
        total_messages=total_messages,
        total_alerts=total_alerts,
        active_alerts=active_alerts,
        latest_readings=latest_readings,
        topics=topic_list,
        thresholds=settings.thresholds,
    )
