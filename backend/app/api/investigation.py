import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.events import add_event
from app.core.security import (
    limiter,
    validate_text_length,
    validate_url_length,
)
from app.database.models import (
    InvestigationDB,
    EvidenceDB,
    InvestigationEventDB,
)

from app.engines.url_engine import analyze_url
from app.engines.text_engine import analyze_text
from app.engines.evidence_engine import findings_to_evidence
from app.engines.risk_engine import calculate_risk, classify_threat
from app.engines.threat_graph import build_threat_graph


router = APIRouter(
    prefix="/api/investigations",
    tags=["Investigations"],
)


class InvestigationRequest(BaseModel):
    input_type: str = Field(
        ...,
        description="URL or TEXT",
    )

    input_value: str = Field(
        ...,
        min_length=3,
        max_length=10000,
    )


def investigation_to_dict(investigation: InvestigationDB) -> dict:
    return {
        "id": investigation.id,
        "input_type": investigation.input_type,
        "input": investigation.input_value,
        "status": investigation.status,
        "risk_score": investigation.risk_score,
        "risk_level": investigation.risk_level,
        "classification": investigation.classification,
        "confidence": investigation.confidence,
        "evidence": [
            {
                "id": f"E-{evidence.id:03d}",
                "type": evidence.evidence_type,
                "title": evidence.title,
                "description": evidence.description,
                "severity": evidence.severity,
                "source": evidence.source,
            }
            for evidence in investigation.evidence
        ],
        "created_at": investigation.created_at.isoformat() + "Z",
    }


@router.post("")
@limiter.limit("20/minute")
def start_investigation(
    request: Request,
    payload: InvestigationRequest,
    db: Session = Depends(get_db),
):
    input_type = payload.input_type.upper().strip()

    if input_type not in {"URL", "TEXT"}:
        raise HTTPException(
            status_code=400,
            detail="input_type must be URL or TEXT.",
        )

    try:
        input_value = (
            validate_url_length(payload.input_value)
            if input_type == "URL"
            else validate_text_length(payload.input_value)
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    investigation_id = str(uuid.uuid4())

    # Create database record
    investigation = InvestigationDB(
        id=investigation_id,
        input_type=input_type,
        input_value=input_value,
        status="analyzing",
        risk_score=0,
        risk_level="UNKNOWN",
        classification="Pending Analysis",
        confidence=0,
    )

    db.add(investigation)
    db.flush()

    add_event(
        db,
        investigation_id,
        "created",
        "Investigation created.",
    )

    # Analyze input
    if input_type == "URL":
        result = analyze_url(input_value)

        if not result["valid"]:
            investigation.status = "failed"
            investigation.classification = "Invalid URL"

            db.commit()

            raise HTTPException(
                status_code=400,
                detail=investigation_to_dict(investigation),
            )

    else:
        result = analyze_text(input_value)

    findings = result["findings"]

    add_event(
        db,
        investigation_id,
        "analysis_completed",
        f"{input_type} analyzer completed.",
    )

    # Convert findings to evidence
    evidence_source = (
        "Threatly URL Analyzer"
        if input_type == "URL"
        else "Threatly Text Analyzer"
    )

    evidence = findings_to_evidence(
        findings,
        source=evidence_source,
    )

    add_event(
        db,
        investigation_id,
        "evidence_detected",
        f"{len(evidence)} security indicator(s) detected.",
    )

    # Calculate risk
    risk = calculate_risk(findings)

    add_event(
        db,
        investigation_id,
        "risk_calculated",
        f"Risk calculated: {risk['risk_level']} ({risk['risk_score']}/100).",
    )

    # Classify threat
    classification = classify_threat(
        findings,
        risk["risk_level"],
    )

    add_event(
        db,
        investigation_id,
        "classified",
        f"Threat classified as: {classification}.",
    )

    # Calculate confidence
    if risk["risk_score"] >= 75:
        confidence = 95
    elif risk["risk_score"] >= 50:
        confidence = 90
    elif risk["risk_score"] >= 25:
        confidence = 75
    else:
        confidence = 60

    # Update investigation
    investigation.status = "completed"
    investigation.risk_score = risk["risk_score"]
    investigation.risk_level = risk["risk_level"]
    investigation.classification = classification
    investigation.confidence = confidence

    add_event(
        db,
        investigation_id,
        "completed",
        "Investigation completed.",
    )

    # Store evidence
    for item in evidence:
        db_evidence = EvidenceDB(
            investigation_id=investigation_id,
            evidence_type=item.get("type", "unknown"),
            title=item.get(
                "title",
                "Security Finding",
            ),
            description=item.get(
                "description",
                "A security-related indicator was detected.",
            ),
            severity=item.get(
                "severity",
                "info",
            ),
            source=item.get(
                "source",
                "Threatly Analyzer",
            ),
        )

        db.add(db_evidence)

    db.commit()
    db.refresh(investigation)

    return investigation_to_dict(investigation)


@router.get("")
def list_investigations(
    db: Session = Depends(get_db),
):
    investigations = (
        db.query(InvestigationDB)
        .order_by(
            InvestigationDB.created_at.desc()
        )
        .limit(50)
        .all()
    )

    return {
        "count": len(investigations),
        "investigations": [
            {
                "id": item.id,
                "input_type": item.input_type,
                "input": item.input_value,
                "status": item.status,
                "risk_score": item.risk_score,
                "risk_level": item.risk_level,
                "classification": item.classification,
                "confidence": item.confidence,
                "created_at": (
                    item.created_at.isoformat()
                    + "Z"
                ),
            }
            for item in investigations
        ],
    }


@router.get("/{investigation_id}/timeline")
def get_investigation_timeline(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    investigation = (
        db.query(InvestigationDB)
        .filter(InvestigationDB.id == investigation_id)
        .first()
    )

    if not investigation:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    events = (
        db.query(InvestigationEventDB)
        .filter(
            InvestigationEventDB.investigation_id == investigation_id
        )
        .order_by(InvestigationEventDB.created_at.asc())
        .all()
    )

    return {
        "investigation_id": investigation_id,
        "count": len(events),
        "timeline": [
            {
                "id": event.id,
                "event_type": event.event_type,
                "message": event.message,
                "created_at": event.created_at.isoformat() + "Z",
            }
            for event in events
        ],
    }


@router.get("/{investigation_id}")
def get_investigation(
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

    return investigation_to_dict(investigation)


@router.get("/{investigation_id}/evidence")
def get_investigation_evidence(
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

    return {
        "investigation_id": investigation_id,
        "evidence_count": len(evidence),
        "evidence": evidence,
    }


@router.get("/{investigation_id}/graph")
def get_investigation_graph(
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

    investigation_data = investigation_to_dict(
        investigation
    )

    return build_threat_graph(
        investigation_data
    )