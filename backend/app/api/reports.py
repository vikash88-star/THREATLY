from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.agent import generate_investigation_report
from app.database.database import get_db
from app.database.events import add_event
from app.database.models import InvestigationDB

router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"],
)

@router.post("/{investigation_id}")
def generate_report(
    investigation_id: str,
    db: Session = Depends(get_db),
):

    investigation = (
        db.query(InvestigationDB)
        .filter(
            InvestigationDB.id == investigation_id
        )
        .first()
    )

    if not investigation:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    evidence = [
        {
            "id": f"E-{item.id:03d}",
            "type": item.evidence_type,
            "title": item.title,
            "description": item.description,
            "severity": item.severity,
            "source": item.source,
        }
        for item in investigation.evidence
    ]

    investigation_data = {
        "id": investigation.id,
        "input_type": investigation.input_type,
        "input": investigation.input_value,
        "status": investigation.status,
        "risk_score": investigation.risk_score,
        "risk_level": investigation.risk_level,
        "classification": investigation.classification,
        "confidence": investigation.confidence,
        "evidence": evidence,
    }

    try:
        report = generate_investigation_report(
            investigation_data
        )

        add_event(
            db,
            investigation_id,
            "ai_report",
            "AI analyst report generated.",
        )

        db.commit()

    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI investigation service failed.",
        )

    return {
        "investigation_id": investigation_id,
        "report": report,
    }
