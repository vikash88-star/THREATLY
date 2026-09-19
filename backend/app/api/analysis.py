from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.events import add_event
from app.database.models import InvestigationDB, EvidenceDB
from app.core.security import validate_url_length

from app.engines.url_engine import analyze_url
from app.engines.text_engine import analyze_text
from app.engines.image_engine import extract_text_from_image
from app.engines.risk_engine import calculate_risk, classify_threat
from app.engines.evidence_engine import findings_to_evidence

router = APIRouter(
    prefix="/api/analyze",
    tags=["Analysis"],
)

class URLAnalysisRequest(BaseModel):
    url: str = Field(
        ...,
        min_length=3,
        max_length=2048,
    )

class TextAnalysisRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=3,
        max_length=10000,
    )

def confidence_from_score(score: int) -> int:
    if score >= 75:
        return 95
    if score >= 50:
        return 90
    if score >= 25:
        return 75
    return 60

def save_investigation(
    db: Session,
    input_type: str,
    input_value: str,
    findings: list[dict],
    evidence_source: str,
):
    investigation_id = str(uuid4())

    risk = calculate_risk(findings)

    classification = classify_threat(
        findings,
        risk["risk_level"],
    )

    confidence = confidence_from_score(
        risk["risk_score"]
    )

    investigation = InvestigationDB(
        id=investigation_id,
        input_type=input_type,
        input_value=input_value,
        status="completed",
        risk_score=risk["risk_score"],
        risk_level=risk["risk_level"],
        classification=classification,
        confidence=confidence,
    )

    db.add(investigation)
    db.flush()

    add_event(
        db,
        investigation_id,
        "created",
        "Investigation created.",
    )

    add_event(
        db,
        investigation_id,
        "analysis_completed",
        f"{input_type} analyzer completed.",
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

    add_event(
        db,
        investigation_id,
        "risk_calculated",
        f"Risk calculated: {risk['risk_level']} ({risk['risk_score']}/100).",
    )

    add_event(
        db,
        investigation_id,
        "classified",
        f"Threat classified as: {classification}.",
    )

    for item in evidence:
        db.add(
            EvidenceDB(
                investigation_id=investigation_id,
                evidence_type=item.get(
                    "type",
                    "unknown",
                ),
                title=item.get(
                    "title",
                    "Security Finding",
                ),
                description=item.get(
                    "description",
                    "Security indicator detected.",
                ),
                severity=item.get(
                    "severity",
                    "info",
                ),
                source=item.get(
                    "source",
                    evidence_source,
                ),
            )
        )

    add_event(
        db,
        investigation_id,
        "completed",
        "Investigation completed.",
    )

    db.commit()
    db.refresh(investigation)

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
                "id": f"E-{item.id:03d}",
                "type": item.evidence_type,
                "title": item.title,
                "description": item.description,
                "severity": item.severity,
                "source": item.source,
            }
            for item in investigation.evidence
        ],
        "created_at": (
            investigation.created_at.isoformat()
            + "Z"
        ),
    }

@router.post("/url")
def analyze_url_endpoint(
    request: URLAnalysisRequest,
):
    try:
        url = validate_url_length(request.url)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    result = analyze_url(url)

    if not result["valid"]:
        raise HTTPException(
            status_code=400,
            detail=result,
        )

    return result

@router.post("/text")
def analyze_text_endpoint(
    request: TextAnalysisRequest,
):
    try:
        result = analyze_text(request.text)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    risk = calculate_risk(
        result["findings"]
    )

    classification = classify_threat(
        result["findings"],
        risk["risk_level"],
    )

    evidence = findings_to_evidence(
        result["findings"],
        source="Threatly Text Analyzer",
    )

    return {
        "input_type": "TEXT",
        "text": request.text,
        "urls": result["urls"],
        "findings": result["findings"],
        "evidence": evidence,
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "classification": classification,
    }

@router.post("/image")
async def analyze_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.content_type:
        raise HTTPException(
            status_code=400,
            detail="Missing file content type.",
        )

    try:
        image_bytes = await file.read()

        image_result = extract_text_from_image(
            image_bytes=image_bytes,
            content_type=file.content_type,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    extracted_text = image_result["text"]

    if not extracted_text:
        investigation = save_investigation(
            db=db,
            input_type="IMAGE",
            input_value=file.filename or "uploaded-image",
            findings=[],
            evidence_source="Threatly OCR Analyzer",
        )

        return {
            **investigation,
            "filename": file.filename,
            "content_type": file.content_type,
            "ocr": image_result,
        }

    text_result = analyze_text(
        extracted_text
    )

    investigation = save_investigation(
        db=db,
        input_type="IMAGE",
        input_value=file.filename or "uploaded-image",
        findings=text_result["findings"],
        evidence_source="Threatly OCR + Text Analyzer",
    )

    return {
        **investigation,
        "filename": file.filename,
        "content_type": file.content_type,
        "ocr": image_result,
        "urls": text_result["urls"],
        "findings": text_result["findings"],
    }
