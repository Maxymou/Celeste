from __future__ import annotations

import base64
import os
import secrets
from typing import Optional

from fastapi import FastAPI, Response, status
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from sqladmin import Admin, ModelView

from backend.app.db import engine
from backend.app.models import Cable

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")
ADMIN_SECRET = os.getenv("ADMIN_SECRET")

if not ADMIN_USER or not ADMIN_PASS or not ADMIN_SECRET:
    raise RuntimeError(
        "ADMIN_USER, ADMIN_PASS, and ADMIN_SECRET environment variables must be set for the admin app."
    )

app = FastAPI(title="Celeste X Admin")
app.add_middleware(SessionMiddleware, secret_key=ADMIN_SECRET)


def _unauthorized_response() -> Response:
    return Response(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Basic"})


def _decode_basic_token(header_value: str) -> Optional[tuple[str, str]]:
    try:
        encoded_credentials = header_value.split(" ", 1)[1]
    except IndexError:
        return None
    try:
        decoded_bytes = base64.b64decode(encoded_credentials)
        decoded = decoded_bytes.decode("utf-8")
        username, password = decoded.split(":", 1)
    except (base64.binascii.Error, UnicodeDecodeError, ValueError):
        return None
    return username, password


@app.middleware("http")
async def basic_auth_middleware(request: Request, call_next):
    header = request.headers.get("Authorization")
    if not header or not header.startswith("Basic "):
        return _unauthorized_response()

    decoded = _decode_basic_token(header)
    if not decoded:
        return _unauthorized_response()

    username, password = decoded
    if not (secrets.compare_digest(username, ADMIN_USER) and secrets.compare_digest(password, ADMIN_PASS)):
        return _unauthorized_response()

    response = await call_next(request)
    return response


class CableAdmin(ModelView, model=Cable):
    column_list = [Cable.id, Cable.name, Cable.description, Cable.diameter_mm]
    name_plural = "Cables"


admin = Admin(app, engine)
admin.add_view(CableAdmin)
