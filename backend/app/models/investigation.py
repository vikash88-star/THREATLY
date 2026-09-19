from datetime import datetime
from typing import Any


investigations: dict[str, dict[str, Any]] = {}


def create_investigation(
    investigation_id: str,
    input_type: str,
    input_value: str,
) -> dict:
    investigation = {
        "id": investigation_id,
        "input_type": input_type,
        "input": input_value,
        "status": "created",
        "risk_score": 0,
        "risk_level": "UNKNOWN",
        "classification": "Pending Analysis",
        "confidence": 0,
        "evidence": [],
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    investigations[investigation_id] = investigation

    return investigation