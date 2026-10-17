"""SCORING stage (SRS §11 inference, §12, §13). Recorded no-op until T19."""

from __future__ import annotations

from mulenetx.jobs.stages.base import Stage, StageContext, StageOutcome


class ScoringStage(Stage):
    name = "SCORING"

    def execute(self, ctx: StageContext) -> StageOutcome:
        return StageOutcome()
