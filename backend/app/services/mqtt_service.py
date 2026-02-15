"""
MQTT Subscriber Service.

Connects to the MQTT broker, subscribes to configured topics,
and processes each incoming message:
  1. Parse JSON payload
  2. Store raw data in MySQL
  3. Validate against thresholds → create alerts
"""

import json
import logging
import threading
import time

import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import SensorData
from app.services.threshold_service import check_thresholds

logger = logging.getLogger("energy.mqtt")


class MQTTSubscriber:
    """Manages MQTT connection lifecycle and message handling."""

    def __init__(self):
        self.client = mqtt.Client(client_id=settings.MQTT_CLIENT_ID, clean_session=True)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self._thread: threading.Thread | None = None

    # ── Callbacks ────────────────────────────────────────────

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker at %s:%s", settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT)
            for topic in settings.mqtt_topics_list:
                client.subscribe(topic, qos=1)
                logger.info("Subscribed to topic: %s", topic)
        else:
            logger.error("MQTT connection failed with code %d", rc)

    def _on_disconnect(self, client, userdata, rc):
        logger.warning("Disconnected from MQTT broker (rc=%d). Reconnecting…", rc)

    def _on_message(self, client, userdata, msg):
        """Process every incoming MQTT message."""
        topic = msg.topic
        try:
            payload_str = msg.payload.decode("utf-8")
            payload = json.loads(payload_str)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error("Invalid payload on %s: %s", topic, e)
            return

        logger.debug("Message on %s: %s", topic, payload)

        # Persist to database in a fresh session
        db: Session = SessionLocal()
        try:
            sensor_record = SensorData(
                topic=topic,
                temperature=payload.get("temperature"),
                humidity=payload.get("humidity"),
                voltage=payload.get("voltage"),
                current=payload.get("current"),
                pressure=payload.get("pressure"),
                raw_payload=payload_str,
            )
            db.add(sensor_record)
            db.commit()

            # Threshold check
            check_thresholds(topic=topic, payload=payload, db=db)

        except Exception:
            db.rollback()
            logger.exception("DB error while processing message on %s", topic)
        finally:
            db.close()

    # ── Lifecycle ────────────────────────────────────────────

    def start(self):
        """Connect and start the MQTT loop in a background daemon thread."""
        def _run():
            while True:
                try:
                    self.client.connect(
                        settings.MQTT_BROKER_HOST,
                        settings.MQTT_BROKER_PORT,
                        keepalive=60,
                    )
                    self.client.loop_forever()
                except Exception:
                    logger.exception("MQTT loop error – retrying in 5 s")
                    time.sleep(5)

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        logger.info("MQTT subscriber thread started")

    def stop(self):
        self.client.disconnect()
        logger.info("MQTT subscriber stopped")


# Module-level singleton
mqtt_subscriber = MQTTSubscriber()
