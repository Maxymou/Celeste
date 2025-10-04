import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker, declarative_base
from sqladmin import Admin, ModelView
from starlette.requests import Request

DB_PATH = os.getenv("CELESTEX_DB_PATH", "./data/celestex.db")
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Cable(Base):
    __tablename__ = "cable"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # conducteur/garde/mixte
    mass_lin_greased = Column(Float)
    E_MPa = Column(Float)
    section_mm2 = Column(Float)
    alpha_1e6_per_C = Column(Float)
    rupture_dan = Column(Float)
    admissible_dan = Column(Float)
    diameter_mm = Column(Float)

class Layer(Base):
    __tablename__ = "layer"
    id = Column(Integer, primary_key=True)
    cable_id = Column(Integer, nullable=False)
    nature = Column(String)      # acier, alu, ...
    wire_shape = Column(String)  # cyl, Z, trap
    strands = Column(Integer)
    strand_diameter_mm = Column(Float)

Base.metadata.create_all(engine)

app = FastAPI(title="CELESTE X — DB Admin")
security = HTTPBasic()

def require_basic(credentials: HTTPBasicCredentials = Depends(security)):
    user = os.getenv("ADMIN_USER")
    pwd = os.getenv("ADMIN_PASS")
    if not user or not pwd or credentials.username != user or credentials.password != pwd:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    return True

@app.get("/admin/health")
def health(_=Depends(require_basic)):
    return {"status": "ok", "db": DB_PATH}

class CableAdmin(ModelView, model=Cable):
    name = "Cable"
    name_plural = "Cables"
    icon = "fa-solid fa-bolt"

class LayerAdmin(ModelView, model=Layer):
    name = "Layer"
    name_plural = "Layers"
    icon = "fa-solid fa-layer-group"

admin = Admin(app, engine, title="CELESTE X — Admin", base_url="/", templates_dir=None,
              csrf_secret=os.getenv("ADMIN_SECRET","change-me"))
admin.add_view(CableAdmin)
admin.add_view(LayerAdmin)
