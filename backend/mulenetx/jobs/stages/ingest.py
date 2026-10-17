"""INGESTING stage (SRS §7.2). For a dataset that is already ingested (POST /pipeline-runs), the stage links
the dataset's successful ingestion run. Upload ingestion is added in T09."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from mulenetx.db.models.pipeline import IngestionRun, PipelineRun
from mulenetx.jobs.runner import JobFailedError
from mulenetx.jobs.stages.base import Stage, StageContext, StageOutcome


def latest_succeeded_ingestion(session: Session, dataset_id: object) -> IngestionRun | None:
    return session.execute(
        select(IngestionRun)
        .where(IngestionRun.dataset_id == dataset_id, IngestionRun.status == "SUCCEEDED")
        .order_by(IngestionRun.started_at.desc())
        .limit(1)
    ).scalar_one_or_none()


class IngestStage(Stage):
    name = "INGESTING"
    kind = "INGEST"

    def execute(self, ctx: StageContext) -> StageOutcome:
        with ctx.runtime.session_factory() as session:
            run = ctx.run(session)
            if run.ingestion_run_id is not None:
                ingestion = session.get(IngestionRun, run.ingestion_run_id)
                if ingestion is not None and ingestion.status == "SUCCEEDED":
                    return StageOutcome()
            existing = latest_succeeded_ingestion(session, ctx.dataset_id)
        if existing is None:
            raise JobFailedError("PIPELINE_PREREQUISITE_MISSING", "the dataset has no successful ingestion run")
        return StageOutcome(run_updates={"ingestion_run_id": existing.ingestion_run_id})

    def prerequisites_ok(self, session: Session, run: PipelineRun) -> bool:
        return True
