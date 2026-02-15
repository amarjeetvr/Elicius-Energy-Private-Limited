"""
Threshold validation and alert generation service.
"""

import json
import logging
from typing import Dict, List, Tuple, Any
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Alert

logger = logging.getLogger("energy.threshold")


def check_thresholds(
    topic: str,
    payload: Dict[str, Any],
    db: Session,
) -> Tuple[bool, List[str]]:
    """
    Validate sensor payload against configured thresholds.

    Returns:
        (has_violation, violated_keys)
    """
    thresholds = settings.thresholds
    violated_keys: List[str] = []
    actual_values: Dict[str, Any] = {}
    threshold_info: Dict[str, Any] = {}

    for param, limits in thresholds.items():
        value = payload.get(param)
        if value is None:
            continue

        min_val = limits["min"]
        max_val = limits["max"]

        if value < min_val or value > max_val:
            violated_keys.append(param)
            actual_values[param] = value
            threshold_info[param] = limits
            logger.warning(
                "Threshold breach on topic=%s | %s=%.2f (limits: %.2f–%.2f)",
                topic, param, value, min_val, max_val,
            )

    if violated_keys:
        # Determine severity
        severity = "critical" if len(violated_keys) >= 3 else "warning"

        message_parts = [
            f"{k}={actual_values[k]} (limit {threshold_info[k]['min']}–{threshold_info[k]['max']})"
            for k in violated_keys
        ]
        message = f"Threshold breach on {topic}: " + ", ".join(message_parts)

        alert = Alert(
            topic=topic,
            violated_keys=violated_keys,
            actual_values=actual_values,
            threshold_limits=threshold_info,
            message=message,
            severity=severity,
        )
        db.add(alert)
        db.commit()
        logger.info("Alert #%d created: %s", alert.id, message)

    return bool(violated_keys), violated_keys
