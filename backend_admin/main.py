"""SQLAdmin dashboard for CELESTE X."""
from __future__ import annotations

import os
import secrets
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base
from sqladmin import Admin, ModelView

DB_PATH = Path(os.getenv("CELESTEX_DB_PATH", "./data/celestex.db")).resolve()
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()


class Cable(Base):
    """Minimal cable table to bootstrap SQLAdmin."""

    __tablename__ = "cable"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # conducteur/garde/mixte
    mass_lin_greased = Column(Float)
    e_mpa = Column(Float)
    section_mm2 = Column(Float)
    alpha_1e6_per_c = Column(Float)
    rupture_dan = Column(Float)
    admissible_dan = Column(Float)
    diameter_mm = Column(Float)


class Layer(Base):
    """Layers associated to a cable."""

    __tablename__ = "layer"

    id = Column(Integer, primary_key=True)
    cable_id = Column(Integer, nullable=False)
    nature = Column(String)
    wire_shape = Column(String)
    strands = Column(Integer)
    strand_diameter_mm = Column(Float)


Base.metadata.create_all(bind=engine)

security = HTTPBasic()


def require_basic(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Validate HTTP Basic credentials for every request."""

    username = os.getenv("ADMIN_USER")
    password = os.getenv("ADMIN_PASS")
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin credentials are not configured.",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not (
        secrets.compare_digest(credentials.username, username)
        and secrets.compare_digest(credentials.password, password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


app = FastAPI(
    title="CELESTE X — DB Admin",
    dependencies=[Depends(require_basic)],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("ADMIN_SECRET", "change-this-too"),
)


@app.get("/admin/health")
def health() -> dict[str, str]:
    """Simple probe to check DB connectivity."""

    return {"status": "ok", "db": str(DB_PATH)}


class CableAdmin(ModelView, model=Cable):
    name = "Cable"
    name_plural = "Cables"
    icon = "fa-solid fa-bolt"


class LayerAdmin(ModelView, model=Layer):
    name = "Layer"
    name_plural = "Layers"
    icon = "fa-solid fa-layer-group"


admin = Admin(
    app,
    engine,
    title="CELESTE X — Admin",
    base_url="/admin",
)
admin.add_view(CableAdmin)
admin.add_view(LayerAdmin)
