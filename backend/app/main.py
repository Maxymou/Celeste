from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api.routes import router as api_router
from .core.config import get_settings
from .db import engine
from .models import Base

settings = get_settings()
settings.database_path.parent.mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.include_router(api_router)

build_path = Path(settings.frontend_dist_path).resolve()
assets_path = build_path / "assets"
if assets_path.exists():
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")


@app.get("/", include_in_schema=False)
async def read_index() -> FileResponse:
    index_file = build_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Frontend build not found. Run the build process and try again.")


@app.get("/{full_path:path}", include_in_schema=False)
async def read_spa(full_path: str) -> FileResponse:
    return await read_index()
