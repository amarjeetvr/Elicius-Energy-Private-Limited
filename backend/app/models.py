"""
SQLAlchemy ORM models for sensor_data and alerts tables.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class SensorData(Base):
    """Stores every raw MQTT message received from sensors."""
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    topic = Column(String(255), nullable=False, index=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    voltage = Column(Float, nullable=True)
    current = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    raw_payload = Column(Text, nullable=True)
    received_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<SensorData(id={self.id}, topic='{self.topic}', received_at={self.received_at})>"


class Alert(Base):
    """Stores threshold-breach alerts with metadata."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    topic = Column(String(255), nullable=False, index=True)
    violated_keys = Column(JSON, nullable=False)       # e.g. ["temperature", "voltage"]
    actual_values = Column(JSON, nullable=False)        # e.g. {"temperature": 95.2, "voltage": 270}
    threshold_limits = Column(JSON, nullable=False)     # e.g. {"temperature": {"min":0,"max":80}, ...}
    message = Column(Text, nullable=True)
    severity = Column(String(50), default="warning")    # warning | critical
    resolved = Column(Integer, default=0)               # 0 = active, 1 = resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<Alert(id={self.id}, topic='{self.topic}', violated_keys={self.violated_keys})>"
