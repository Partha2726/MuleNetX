"""Router registration. Each task adds its routers here."""

from __future__ import annotations

from fastapi import FastAPI

from mulenetx.api.routes import (
    accounts,
    aliases,
    auth,
    communities,
    context,
    graph,
    health,
    ingestion,
    models,
    pipelines,
    users,
)


def register_routes(app: FastAPI) -> None:
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(ingestion.router)
    app.include_router(pipelines.router)
    app.include_router(models.router)
    app.include_router(context.router)
    app.include_router(accounts.router)
    app.include_router(graph.router)
    app.include_router(communities.router)
    app.include_router(aliases.router)
