"""Activation of a READY pipeline run (SRS §6.9). Extended with projections and retirement in T12."""

from __future__ import annotations

from sqlalchemy import update
from sqlalchemy.orm import Session

from mulenetx.audit.service import AuditService
from mulenetx.core.timeutil import utcnow
from mulenetx.db.models.lineage import ActiveContext
from mulenetx.db.models.pipeline import PipelineRun


def activate(session: Session, run: PipelineRun, risk_logic_version: str | None = None) -> None:
    """Steps 1 and 3 of §6.9 inside the caller's transaction (step 2, projections, arrives in T12)."""
    session.execute(
        update(ActiveContext)
        .where(ActiveContext.singleton.is_(True))
        .values(
            dataset_id=run.dataset_id,
            graph_snapshot_id=run.graph_snapshot_id,
            analytics_run_id=run.analytics_run_id,
            scoring_run_id=run.scoring_run_id,
            model_version=run.model_version,
            risk_logic_version=risk_logic_version,
            updated_at=utcnow(),
            updated_by_pipeline_run_id=run.pipeline_run_id,
        )
    )
    session.add(
        AuditService.build(
            "pipeline.activate",
            "pipeline_run",
            "SUCCESS",
            resource_id=str(run.pipeline_run_id),
            metadata={"graph_snapshot_id": str(run.graph_snapshot_id), "scoring_run_id": str(run.scoring_run_id)},
        )
    )
