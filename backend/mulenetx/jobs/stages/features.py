"""FEATURES_RUNNING stage (SRS §10). Recorded no-op until T15."""

from __future__ import annotations

from sqlalchemy.orm import Session

from mulenetx.db.models.lineage import AnalyticsRun
from mulenetx.db.models.pipeline import PipelineRun
from mulenetx.jobs.stages.base import Stage, StageContext, StageOutcome


class FeaturesStage(Stage):
    name = "FEATURES_RUNNING"

    def prerequisites_ok(self, session: Session, run: PipelineRun) -> bool:
        if run.analytics_run_id is None:
            return False
        analytics = session.get(AnalyticsRun, run.analytics_run_id)
        return analytics is not None and analytics.status == "SUCCEEDED"

    def execute(self, ctx: StageContext) -> StageOutcome:
        return StageOutcome()
