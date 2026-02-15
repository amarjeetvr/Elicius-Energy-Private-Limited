"""
Application configuration using Pydantic Settings.
Loads values from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mysql+pymysql://energy_user:energy_pass@db:3306/energy_db"

    # MQTT
    MQTT_BROKER_HOST: str = "mqtt-broker"
    MQTT_BROKER_PORT: int = 1883
    MQTT_CLIENT_ID: str = "energy-fastapi-client"
    MQTT_TOPICS: str = "sensor/temperature,sensor/humidity,sensor/voltage,sensor/current,sensor/pressure,sensor/power,sensor/energy,sensor/frequency"

    # Thresholds  (min, max) for each sensor parameter
    THRESHOLD_TEMPERATURE_MIN: float = 0
    THRESHOLD_TEMPERATURE_MAX: float = 80
    THRESHOLD_HUMIDITY_MIN: float = 10
    THRESHOLD_HUMIDITY_MAX: float = 95
    THRESHOLD_VOLTAGE_MIN: float = 180
    THRESHOLD_VOLTAGE_MAX: float = 260
    THRESHOLD_CURRENT_MIN: float = 0
    THRESHOLD_CURRENT_MAX: float = 30
    THRESHOLD_PRESSURE_MIN: float = 900
    THRESHOLD_PRESSURE_MAX: float = 1100

    @property
    def mqtt_topics_list(self) -> List[str]:
        return [t.strip() for t in self.MQTT_TOPICS.split(",") if t.strip()]

    @property
    def thresholds(self) -> dict:
        """Return threshold dictionary keyed by parameter name."""
        return {
            "temperature": {"min": self.THRESHOLD_TEMPERATURE_MIN, "max": self.THRESHOLD_TEMPERATURE_MAX},
            "humidity":    {"min": self.THRESHOLD_HUMIDITY_MIN,    "max": self.THRESHOLD_HUMIDITY_MAX},
            "voltage":     {"min": self.THRESHOLD_VOLTAGE_MIN,     "max": self.THRESHOLD_VOLTAGE_MAX},
            "current":     {"min": self.THRESHOLD_CURRENT_MIN,     "max": self.THRESHOLD_CURRENT_MAX},
            "pressure":    {"min": self.THRESHOLD_PRESSURE_MIN,    "max": self.THRESHOLD_PRESSURE_MAX},
        }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
