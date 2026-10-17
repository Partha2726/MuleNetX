"""GRAPH_BUILDING stage (SRS §6.8). Recorded no-op until T11: records a READY snapshot row only."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mulenetx.core.timeutil import utcnow
from mulenetx.db.models.canonical import Transaction
from mulenetx.db.models.lineage import GraphSnapshot
from mulenetx.db.models.pipeline import IngestionRun, PipelineRun
from mulenetx.jobs.runner import JobFailedError
from mulenetx.jobs.stages.base import Stage, StageContext, StageOutcome


class GraphBuildStage(Stage):
    name = "GRAPH_BUILDING"

    def prerequisites_ok(self, session: Session, run: PipelineRun) -> bool:
        if run.ingestion_run_id is None:
            return False
        ingestion = session.get(IngestionRun, run.ingestion_run_id)
        return ingestion is not None and ingestion.status == "SUCCEEDED"

    def execute(self, ctx: StageContext) -> StageOutcome:
        snapshot_id = ctx.load_run().graph_snapshot_id or uuid.uuid4()
        with ctx.runtime.session_factory() as session:
            if session.get(GraphSnapshot, snapshot_id) is None:
                run = ctx.run(session)
                cutoff, count = session.execute(
                    select(func.max(Transaction.timestamp), func.count()).where(
                        Transaction.dataset_id == ctx.dataset_id
                    )
                ).one()
                if cutoff is None:
                    raise JobFailedError("PIPELINE_PREREQUISITE_MISSING", "the dataset has no accepted transactions")
                now = utcnow()
                session.add(
                    GraphSnapshot(
                        graph_snapshot_id=snapshot_id,
                        dataset_id=ctx.dataset_id,
                        ingestion_run_id=run.ingestion_run_id,
                        purpose="OPERATIONAL",
                        data_cutoff=cutoff,
                        pipeline_version="noop",
                        graph_schema_version="noop",
                        source_record_count=count,
                        status="READY",
                        created_at=now,
                        ready_at=now,
                    )
                )
                session.commit()
        ctx.set_once("graph_snapshot_id", snapshot_id)
        return StageOutcome()
