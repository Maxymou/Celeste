"""FastAPI application serving the CELESTE X API and static frontend."""
from pathlib import Path

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict

app = FastAPI(title="CELESTE X")
api = APIRouter(prefix="/api", tags=["api"])


class SpanInput(BaseModel):
    """Placeholder payload for future span calculations."""

    span_length_m: float
    delta_h_m: float
    angle_topo_grade: float
    chain_mass_kg: float | None = None
    cable_mass_per_m_kg: float | None = None
    tension_ini_dan: float | None = None

    model_config = ConfigDict(extra="forbid")


@api.get("/health")
def health() -> dict[str, str]:
    """Simple readiness probe."""

    return {"status": "ok"}


@api.post("/calc/span")
def calc_span(payload: SpanInput) -> dict[str, object]:
    """Temporary stub that echoes the input and returns constant values."""

    return {
        "input": payload.model_dump(),
        "result": {
            "cos_theta": 1.0,
            "sag_m": 0.0,
            "tension_final_dan": payload.tension_ini_dan or 0.0,
        },
        "messages": [],
    }


app.include_router(api)

DIST_DIR = Path(__file__).resolve().parents[1] / "frontend" / "dist"
INDEX_FILE = DIST_DIR / "index.html"


if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="static")

    @app.middleware("http")
    async def spa_fallback(request: Request, call_next):  # type: ignore[override]
        """Serve index.html when a non-API route returns 404 (SPA fallback)."""

        response = await call_next(request)
        if (
            response.status_code == 404
            and request.method == "GET"
            and not request.url.path.startswith("/api/")
            and INDEX_FILE.exists()
        ):
            return FileResponse(str(INDEX_FILE))
        return response
else:
    @app.get("/", include_in_schema=False)
    def frontend_placeholder() -> dict[str, str]:
        """Helpful message when the Vite build has not been generated yet."""

        return {"detail": "Frontend build missing. Run npm run build in frontend/."}
