"""RingIntelligenceService (SRS §9, §9A, §18.1): candidates from communities after SCORING, then ring
intelligence for POTENTIAL_FRAUD_RING_CANDIDATE. Computation happens outside the database transaction; the
RING_ANALYSIS stage writes everything in its final transaction (idempotent inserts)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from mulenetx.core import ids
from mulenetx.core.runtime import Runtime
from mulenetx.db.models.lineage import AnalyticsRun, GraphSnapshot, ScoringRun
from mulenetx.db.models.rings import RingCandidate
from mulenetx.flow.analytic_paths import Budget
from mulenetx.rings import inputs
from mulenetx.rings.candidates import CandidateScore, score_communities


@dataclass
class RingAnalysis:
    snapshot: GraphSnapshot
    analytics: AnalyticsRun
    scoring: ScoringRun
    candidates: dict[str, CandidateScore]  # persisted classes only, by community_id
    context: inputs.ContextInputs


class RingIntelligenceService:
    def __init__(self, runtime: Runtime) -> None:
        self.rt = runtime

    def budget(self) -> Budget:
        s = self.rt.settings
        return Budget(s.analytic_max_depth, s.analytic_max_paths, s.analytic_max_expansions)

    def analyze(
        self, dataset_id: uuid.UUID, snapshot_id: uuid.UUID, analytics_run_id: uuid.UUID, scoring_run_id: uuid.UUID
    ) -> RingAnalysis:
        with self.rt.session_factory() as db:
            snapshot = db.get(GraphSnapshot, snapshot_id)
            analytics = db.get(AnalyticsRun, analytics_run_id)
            scoring = db.get(ScoringRun, scoring_run_id)
            assert snapshot is not None and analytics is not None and scoring is not None
            assert snapshot.data_cutoff is not None
            db.expunge_all()
        ctx = inputs.load(
            self.rt.engine,
            dataset_id,
            snapshot_id,
            snapshot.data_cutoff,
            analytics_run_id,
            analytics.analytics_version,
            scoring_run_id,
            self.budget(),
        )
        scored = score_communities(ctx)
        persisted = {cid: c for cid, c in scored.items() if c.candidate_class != "NOT_SUSPICIOUS"}
        return RingAnalysis(snapshot, analytics, scoring, persisted, ctx)

    @staticmethod
    def persist(db: Session, analysis: RingAnalysis, now: datetime) -> list[uuid.UUID]:
        """Insert candidates (ON CONFLICT DO NOTHING: a rerun of the same scoring run derives the same IDs)."""
        snap, run = analysis.snapshot.graph_snapshot_id, analysis.scoring.scoring_run_id
        written: list[uuid.UUID] = []
        for community_id, c in sorted(analysis.candidates.items()):
            candidate_id = ids.candidate_id(snap, run, community_id)
            db.execute(
                insert(RingCandidate)
                .values(
                    candidate_id=candidate_id,
                    community_id=community_id,
                    analytics_run_id=analysis.analytics.analytics_run_id,
                    graph_snapshot_id=snap,
                    scoring_run_id=run,
                    candidate_score=c.score,
                    candidate_class=c.candidate_class,
                    signal_summary=c.signals,
                    candidate_status="CANDIDATE",
                    analytics_version=analysis.analytics.analytics_version,
                    risk_logic_version=analysis.scoring.risk_logic_version,
                    created_at=now,
                )
                .on_conflict_do_nothing()
            )
            written.append(candidate_id)
        return written


def candidates_of_run(db: Session, scoring_run_id: uuid.UUID) -> list[RingCandidate]:
    return list(
        db.execute(
            select(RingCandidate)
            .where(RingCandidate.scoring_run_id == scoring_run_id)
            .order_by(RingCandidate.candidate_score.desc(), RingCandidate.candidate_id)
        ).scalars()
    )
