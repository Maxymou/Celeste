import os
import sys
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status
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


def require_basic(credentials: HTTPBasicCredentials = Depends(security)):
    """Authentification Basic Auth"""
    user = os.getenv("ADMIN_USER")
    pwd = os.getenv("ADMIN_PASS")
    
    if not user or not pwd or credentials.username != user or credentials.password != pwd:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"}
        )
    return True


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
    templates_dir=None,
    csrf_secret=os.getenv("ADMIN_SECRET", "change-me")
)

admin.add_view(CableAdmin)
admin.add_view(LayerAdmin)
