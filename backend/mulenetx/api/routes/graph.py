"""Graph exploration (SRS §19.2, §19.9, §25.2)."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from mulenetx.api.deps import Services, get_db, get_services, require
from mulenetx.auth.service import Principal
from mulenetx.core import error_codes as ec
from mulenetx.core.errors import AppError, limit_exceeded
from mulenetx.graph.neighborhood import neighborhood

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])

DEFAULT_MAX_NODES = 100  # agent default (OQ-33)
DEFAULT_MAX_EDGES = 500


def bounded(name: str, value: int, maximum: int) -> int:
    """Reject (never clamp) out-of-range limits (§19.1)."""
    if value < 1:
        raise AppError(ec.VALIDATION_ERROR, details={"field": name})
    if value > maximum:
        raise limit_exceeded(name, maximum)
    return value


@router.get("/neighborhood")
def get_neighborhood(
    account_id: str = Query(...),
    depth: int = Query(default=1),
    max_nodes: int = Query(default=DEFAULT_MAX_NODES),
    max_edges: int = Query(default=DEFAULT_MAX_EDGES),
    graph_snapshot_id: uuid.UUID | None = Query(default=None),
    _p: Principal = Depends(require("graph.read")),
    db: Session = Depends(get_db),
    services: Services = Depends(get_services),
) -> dict[str, Any]:
    s = services.runtime.settings
    d = bounded("depth", depth, s.graph_max_depth)
    n = bounded("max_nodes", max_nodes, s.graph_max_nodes)
    e = bounded("max_edges", max_edges, s.graph_max_edges)
    return neighborhood(services.runtime, db, account_id, d, n, e, graph_snapshot_id)
