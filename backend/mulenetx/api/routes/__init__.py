"""Router registration. Each task adds its routers here."""

from __future__ import annotations

from fastapi import FastAPI

from mulenetx.api.routes import health


def register_routes(app: FastAPI) -> None:
    app.include_router(health.router)
