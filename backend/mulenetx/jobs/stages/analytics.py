"""ANALYTICS_RUNNING stage (SRS §8, §15.9). Recorded no-op until T13."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from mulenetx.core.timeutil import utcnow
from mulenetx.db.models.lineage import AnalyticsRun, GraphSnapshot
from mulenetx.db.models.pipeline import PipelineRun
from mulenetx.jobs.stages.base import Stage, StageContext, StageOutcome


class AnalyticsStage(Stage):
    name = "ANALYTICS_RUNNING"

    def prerequisites_ok(self, session: Session, run: PipelineRun) -> bool:
        if run.graph_snapshot_id is None:
            return False
        snapshot = session.get(GraphSnapshot, run.graph_snapshot_id)
        return snapshot is not None and snapshot.status == "READY"

    def execute(self, ctx: StageContext) -> StageOutcome:
        run_id = ctx.load_run().analytics_run_id or uuid.uuid4()
        with ctx.runtime.session_factory() as session:
            if session.get(AnalyticsRun, run_id) is None:
                run = ctx.run(session)
                now = utcnow()
                session.add(
                    AnalyticsRun(
                        analytics_run_id=run_id,
                        graph_snapshot_id=run.graph_snapshot_id,
                        analytics_version="noop",
                        engine="NETWORKX",
                        algorithm_configuration={"noop": True},
                        started_at=now,
                        completed_at=now,
                        status="SUCCEEDED",
                    )
                )
                session.commit()
        ctx.set_once("analytics_run_id", run_id)
        return StageOutcome()
