from typing import Generator
from sqlalchemy.orm import Session
from app.core.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependencia que provee una sesión de SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
