"""PROFILING stage (SRS §7.9). Recorded no-op until T10."""

from __future__ import annotations

from sqlalchemy.dialects.postgresql import insert

from mulenetx.core.timeutil import utcnow
from mulenetx.db.models.datasets import DatasetProfile
from mulenetx.jobs.stages.base import Stage, StageContext, StageOutcome


class ProfileStage(Stage):
    name = "PROFILING"

    def execute(self, ctx: StageContext) -> StageOutcome:
        with ctx.runtime.session_factory() as session:
            session.execute(
                insert(DatasetProfile)
                .values(dataset_id=ctx.dataset_id, profile_version="noop", metrics={"noop": True}, created_at=utcnow())
                .on_conflict_do_nothing()
            )
            session.commit()
        return StageOutcome()
