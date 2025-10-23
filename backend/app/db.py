from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .core.config import get_settings

settings = get_settings()
DATABASE_URL = f"sqlite:///{Path(settings.database_path).resolve()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
