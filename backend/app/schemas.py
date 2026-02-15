"""
Pydantic schemas for request/response serialization.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


# ── Sensor Data ──────────────────────────────────────────────

class SensorPayload(BaseModel):
    """Schema for incoming MQTT JSON payload."""
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    voltage: Optional[float] = None
    current: Optional[float] = None
    pressure: Optional[float] = None


class SensorDataOut(BaseModel):
    id: int
    topic: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    voltage: Optional[float] = None
    current: Optional[float] = None
    pressure: Optional[float] = None
    received_at: datetime

    class Config:
        from_attributes = True


class SensorDataPaginated(BaseModel):
    items: List[SensorDataOut]
    total: int
    page: int
    page_size: int
    total_pages: int


# ── Alerts ───────────────────────────────────────────────────

class AlertOut(BaseModel):
    id: int
    topic: str
    violated_keys: List[str]
    actual_values: Dict[str, Any]
    threshold_limits: Dict[str, Any]
    message: Optional[str] = None
    severity: str
    resolved: int
    created_at: datetime

    class Config:
        from_attributes = True


class AlertPaginated(BaseModel):
    items: List[AlertOut]
    total: int
    page: int
    page_size: int
    total_pages: int


# ── Dashboard Stats ──────────────────────────────────────────

class DashboardStats(BaseModel):
    total_messages: int
    total_alerts: int
    active_alerts: int
    latest_readings: Dict[str, Any]
    topics: List[str]
    thresholds: Dict[str, Any]
