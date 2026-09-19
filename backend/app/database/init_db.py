from app.database.database import Base, engine
from app.database.models import (
    InvestigationDB,
    EvidenceDB,
    InvestigationEventDB,
)


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Threatly database initialized successfully.")


if __name__ == "__main__":
    init_db()