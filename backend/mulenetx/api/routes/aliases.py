"""Compatibility aliases of SRS §19.2.1. Each alias has its target's permission, parameters, response and
errors, and adds `Deprecation: true` and a `Link` header naming the target."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from mulenetx.api.deps import Services, get_db, get_services, require
from mulenetx.api.routes.pipelines import retry_run
from mulenetx.auth.service import Principal
from mulenetx.core import error_codes as ec
from mulenetx.core.errors import AppError
from mulenetx.db.models.pipeline import PipelineRun

router = APIRouter(prefix="/api/v1", tags=["aliases"])


def deprecate(response: JSONResponse, target: str) -> JSONResponse:
    response.headers["Deprecation"] = "true"
    response.headers["Link"] = f'<{target}>; rel="successor-version"'
    return response


@router.post("/ingestion/{ingestion_run_id}/retry", status_code=202, deprecated=True)
def ingestion_retry(
    ingestion_run_id: uuid.UUID,
    request: Request,
    principal: Principal = Depends(require("pipeline.control")),
    db: Session = Depends(get_db),
    services: Services = Depends(get_services),
) -> JSONResponse:
    run_id = db.execute(
        select(PipelineRun.pipeline_run_id)
        .where(PipelineRun.ingestion_run_id == ingestion_run_id)
        .order_by(PipelineRun.started_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    if run_id is None:
        raise AppError(ec.NOT_FOUND, details={"resource": "ingestion"})
    response = retry_run(run_id, request, principal, db, services)
    return deprecate(response, f"/api/v1/pipeline-runs/{run_id}/retry")
