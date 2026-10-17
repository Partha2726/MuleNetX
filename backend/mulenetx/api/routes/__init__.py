"""Router registration. Each task adds its routers here."""

from __future__ import annotations

from fastapi import FastAPI

from mulenetx.api.routes import auth, health, users


def register_routes(app: FastAPI) -> None:
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(users.router)
