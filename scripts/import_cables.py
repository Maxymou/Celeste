"""Placeholder script for importing cable data from XML sources.

This module will be implemented in a future iteration to parse the XML files
(`Câble.xml` and `Couche câble.xml`) and populate the SQLite database. The
structure is laid out to make it easy to expand later.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from backend.app.db import SessionLocal
from backend.app.models import Cable

BASE_DIR = Path(__file__).resolve().parent.parent
CABLE_XML_PATH = BASE_DIR / "Câble.xml"
LAYER_XML_PATH = BASE_DIR / "Couche câble.xml"


def import_cables(session: Session) -> None:
    """Import placeholder that confirms XML files exist."""

    if not CABLE_XML_PATH.exists() or not LAYER_XML_PATH.exists():
        raise FileNotFoundError(
            "Expected cable XML files are missing. Ensure 'Câble.xml' and 'Couche câble.xml' are present."
        )

    # Placeholder implementation. Future iterations will parse the XML files
    # and insert/update records in the database.
    print("XML files located. Implement parsing in a future iteration.")


if __name__ == "__main__":
    with SessionLocal() as session:
        import_cables(session)
