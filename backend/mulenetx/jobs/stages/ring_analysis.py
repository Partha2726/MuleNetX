"""RING_ANALYSIS stage (SRS §9, §9A) followed by activation (§6.9) in the same final transaction.
Ring analysis is a recorded no-op until T32."""

from __future__ import annotations

from sqlalchemy.orm import Session

from mulenetx.jobs.stages.activate import activate
from mulenetx.jobs.stages.base import Stage, StageContext, StageOutcome


class RingAnalysisStage(Stage):
    name = "RING_ANALYSIS"

    def execute(self, ctx: StageContext) -> StageOutcome:
        def finalize(session: Session) -> None:
            activate(session, ctx.run(session))

        return StageOutcome(finalize=finalize)
