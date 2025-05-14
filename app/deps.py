# app/deps.py
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Dependencia que provee una sesión de SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
