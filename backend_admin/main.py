import base64
import binascii
import os
import sys
from pathlib import Path
from typing import Optional, Tuple

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqladmin import Admin, ModelView

# Ajouter le chemin parent pour importer les modèles
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.models.db_models import Base, Cable, Layer

DB_PATH = os.getenv("CELESTEX_DB_PATH", "./data/celestex.db")
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}", 
    connect_args={"check_same_thread": False}
)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="CELESTE X — DB Admin")
security = HTTPBasic()


def _admin_credentials() -> Tuple[Optional[str], Optional[str]]:
    """Retrieve the configured admin credentials from the environment."""
    return os.getenv("ADMIN_USER"), os.getenv("ADMIN_PASS")


def _credentials_valid(username: str, password: str) -> bool:
    expected_user, expected_password = _admin_credentials()
    return bool(
        expected_user
        and expected_password
        and username == expected_user
        and password == expected_password
    )


def _parse_basic_auth_header(header: Optional[str]) -> Optional[Tuple[str, str]]:
    if not header:
        return None

    scheme, _, encoded = header.partition(" ")
    if scheme.lower() != "basic" or not encoded:
        return None

    try:
        decoded = base64.b64decode(encoded).decode()
    except (binascii.Error, UnicodeDecodeError):
        return None

    if ":" not in decoded:
        return None

    username, password = decoded.split(":", 1)
    return username, password


def _unauthorized_response() -> JSONResponse:
    return JSONResponse(
        {"detail": "Unauthorized"},
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Basic"},
    )


def require_basic(credentials: HTTPBasicCredentials = Depends(security)):
    """Authentification Basic Auth"""
    if not _credentials_valid(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


@app.middleware("http")
async def enforce_basic_auth(request: Request, call_next):
    """Protect the SQLAdmin interface with HTTP Basic authentication."""
    # SQLAdmin serves the entire interface from the root path. Every request must
    # include valid credentials to avoid exposing the database over the network.
    credentials = _parse_basic_auth_header(request.headers.get("Authorization"))

    if not credentials or not _credentials_valid(*credentials):
        return _unauthorized_response()

    return await call_next(request)


@app.get("/admin/health")
def health(_=Depends(require_basic)):
    """Endpoint de santé de l'admin"""
    return {"status": "ok", "db": DB_PATH}


class CableAdmin(ModelView, model=Cable):
    """Vue admin pour les câbles"""
    name = "Cable"
    name_plural = "Cables"
    icon = "fa-solid fa-bolt"
    
    column_list = [
        Cable.id,
        Cable.name,
        Cable.type,
        Cable.mass_lin_greased,
        Cable.rupture_dan,
        Cable.diameter_mm
    ]
    
    column_searchable_list = [Cable.name, Cable.type]
    column_sortable_list = [Cable.name, Cable.type, Cable.mass_lin_greased]


class LayerAdmin(ModelView, model=Layer):
    """Vue admin pour les couches de câbles"""
    name = "Layer"
    name_plural = "Layers"
    icon = "fa-solid fa-layer-group"
    
    column_list = [
        Layer.id,
        Layer.cable_id,
        Layer.nature,
        Layer.wire_shape,
        Layer.strands,
        Layer.strand_diameter_mm
    ]
    
    column_searchable_list = [Layer.nature, Layer.wire_shape]
    column_sortable_list = [Layer.cable_id, Layer.nature, Layer.strands]


# Créer l'interface admin
admin = Admin(
    app,
    engine,
    title="CELESTE X — Admin",
    base_url="/",
)

admin.add_view(CableAdmin)
admin.add_view(LayerAdmin)
