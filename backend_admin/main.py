import os
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.middleware.sessions import SessionMiddleware

# Ajouter le chemin parent pour importer les modèles
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.models.db_models import Base, Cable, Layer  # noqa: E402


@dataclass(frozen=True)
class AdminSettings:
    """Configuration de l'interface admin chargée depuis l'environnement."""

    db_path: Path
    admin_user: str
    admin_pass: str
    admin_secret: str


def _load_env_file(env_path: Path) -> None:
    """Charge les variables depuis un fichier .env si présent."""

    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@lru_cache
def get_settings() -> AdminSettings:
    """Charge et met en cache la configuration admin."""

    project_root = Path(__file__).resolve().parents[1]
    _load_env_file(project_root / ".env")

    db_path = Path(os.getenv("CELESTEX_DB_PATH", "./data/celestex.db"))
    admin_user = os.getenv("ADMIN_USER", "admin")
    admin_pass = os.getenv("ADMIN_PASS", "admin")
    admin_secret = os.getenv("ADMIN_SECRET", "change-me")

    if not admin_user or not admin_pass:
        raise RuntimeError("Les identifiants admin ne peuvent pas être vides")

    return AdminSettings(
        db_path=db_path,
        admin_user=admin_user,
        admin_pass=admin_pass,
        admin_secret=admin_secret,
    )


settings = get_settings()
DB_PATH = settings.db_path
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
)
Base.metadata.create_all(engine)
app = FastAPI(title="CELESTE X — DB Admin")
app.add_middleware(SessionMiddleware, secret_key=settings.admin_secret)
security = HTTPBasic(auto_error=False)


def _credentials_valid(username: Optional[str], password: Optional[str]) -> bool:
    """Compare les identifiants fournis avec ceux de la configuration."""

    return bool(
        username
        and password
        and username == settings.admin_user
        and password == settings.admin_pass
    )


async def require_basic(credentials: Optional[HTTPBasicCredentials] = Depends(security)):
    """Authentification HTTP Basic dédiée aux checks automatisés."""

    if not credentials or not _credentials_valid(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


class AdminAuthBackend(AuthenticationBackend):
    """Auth backend SQLAdmin basé sur la configuration environnement."""

    SESSION_FLAG = "admin_authenticated"

    def __init__(self) -> None:
        super().__init__(secret_key=settings.admin_secret)

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get(self.SESSION_FLAG))

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if not _credentials_valid(username, password):
            return False

        request.session[self.SESSION_FLAG] = True
        return True

    async def logout(self, request: Request) -> bool:
        request.session.pop(self.SESSION_FLAG, None)
        return True


@app.get("/admin/health")
async def health(_=Depends(require_basic)):
    """Endpoint de santé de l'admin"""
    return {"status": "ok", "db": str(DB_PATH)}


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
        Cable.diameter_mm,
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
        Layer.strand_diameter_mm,
    ]

    column_searchable_list = [Layer.nature, Layer.wire_shape]
    column_sortable_list = [Layer.cable_id, Layer.nature, Layer.strands]


# Créer l'interface admin
admin = Admin(
    app,
    engine,
    title="CELESTE X — Admin",
    base_url="/",
    authentication_backend=AdminAuthBackend(),
)

admin.add_view(CableAdmin)
admin.add_view(LayerAdmin)
