from sqlalchemy.orm import Session

from app.database.models import InvestigationEventDB


def add_event(
    db: Session,
    investigation_id: str,
    event_type: str,
    message: str,
):
    event = InvestigationEventDB(
        investigation_id=investigation_id,
        event_type=event_type,
        message=message,
    )

    db.add(event)
    db.flush()

    return event
