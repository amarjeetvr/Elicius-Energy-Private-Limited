"""
Alerts API endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
import math

from app.database import get_db
from app.models import Alert
from app.schemas import AlertOut, AlertPaginated

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("/", response_model=AlertPaginated)
def get_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    topic: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    resolved: Optional[int] = Query(None, description="0=active, 1=resolved"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated alerts with optional filters."""
    query = db.query(Alert)

    if topic:
        query = query.filter(Alert.topic == topic)
    if severity:
        query = query.filter(Alert.severity == severity)
    if resolved is not None:
        query = query.filter(Alert.resolved == resolved)

    total = query.count()
    total_pages = max(1, math.ceil(total / page_size))

    items = (
        query
        .order_by(desc(Alert.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return AlertPaginated(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/active", response_model=list[AlertOut])
def get_active_alerts(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get unresolved alerts."""
    items = (
        db.query(Alert)
        .filter(Alert.resolved == 0)
        .order_by(desc(Alert.created_at))
        .limit(limit)
        .all()
    )
    return items


@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as resolved."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.resolved = 1
    db.commit()
    return {"message": f"Alert {alert_id} resolved"}
