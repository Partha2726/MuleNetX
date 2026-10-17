"""TRAINING stage (SRS §11) and the rule that decides whether it runs (§7.6 rule 3). No-op until T17."""

from __future__ import annotations

from sqlalchemy.orm import Session

from mulenetx.db.models.pipeline import PipelineRun
from mulenetx.jobs.stages.base import Stage, StageContext, StageOutcome


def compatible_model(session: Session, run: PipelineRun) -> str | None:
    """A registered model with the current feature version, feature regime and target definition, if any."""
    return None


class TrainingStage(Stage):
    name = "TRAINING"
    kind = "TRAIN"

    def execute(self, ctx: StageContext) -> StageOutcome:
        return StageOutcome()
