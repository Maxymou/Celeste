from pathlib import Path
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="CELESTE X")
api = APIRouter(prefix="/api")

@api.get("/health")
def health():
    return {"status": "ok"}

class SpanInput(BaseModel):
    span_length_m: float
    delta_h_m: float
    angle_topo_grade: float
    chain_mass_kg: float | None = None
    cable_mass_per_m_kg: float | None = None
    tension_ini_dan: float | None = None

@api.post("/calc/span")
def calc_span(payload: SpanInput):
    # stub: return payload with placeholders
    return {
        "input": payload.dict(),
        "result": {
            "cos_theta": 1.0,
            "sag_m": 0.0,
            "tension_final_dan": payload.tension_ini_dan or 0.0
        },
        "messages": []
    }

app.include_router(api)

DIST_DIR = Path(__file__).resolve().parents[1] / "frontend" / "dist"
INDEX_FILE = DIST_DIR / "index.html"
if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="static")

    @app.middleware("http")
    async def spa_fallback(request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 404 and request.method == "GET":
            path = request.url.path
            if not path.startswith("/api/") and INDEX_FILE.exists():
                return FileResponse(str(INDEX_FILE))
        return response
