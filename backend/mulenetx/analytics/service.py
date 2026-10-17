"""AnalyticsService (SRS §8, §18.1): metrics, components and communities for one snapshot, persisted with
the analytics run in a single transaction."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from importlib.metadata import version as pkg_version
from typing import Any

import networkx as nx

from mulenetx.analytics.algorithms import AccountMetrics, AlgorithmConfig, compute_metrics
from mulenetx.analytics.communities import Community, canonical_communities
from mulenetx.analytics.projection import Projection, export
from mulenetx.core.config import Settings
from mulenetx.core.runtime import Runtime
from mulenetx.core.timeutil import utcnow

ENGINE = "NETWORKX"


def algorithm_configuration(settings: Settings) -> dict[str, Any]:
    """Every §8 parameter, seed and library version — the inputs of `analytics_version` (§8.4, §23.1 V)."""
    cfg = AlgorithmConfig(settings.pagerank_damping, settings.pagerank_max_iterations, settings.pagerank_tolerance)
    return {
        "engine": "networkx",
        "tier": "REFERENCE",
        "libraries": {"networkx": nx.__version__, "numpy": pkg_version("numpy"), "scipy": pkg_version("scipy")},
        **cfg.as_dict(),
        "louvain": {
            "algorithm": "Louvain",
            "projection": "undirected weighted simple",
            "weight": "total_amount summed over both directions",
            "resolution": settings.louvain_resolution,
            "seed": settings.louvain_seed,
        },
        "projection_order": "nodes by account_id; edges by (source, destination); self-pairs excluded",
        "normalization": {"pagerank_norm": "snapshot min-max; constant series -> 0"},
        "motifs": None,
    }


def analytics_version(configuration: dict[str, Any]) -> str:
    canonical = json.dumps(configuration, sort_keys=True, separators=(",", ":"))
    return f"nx-{nx.__version__}-{hashlib.sha256(canonical.encode()).hexdigest()[:12]}"


@dataclass(frozen=True)
class AnalyticsResult:
    analytics_run_id: uuid.UUID
    analytics_version: str
    community_count: int


class AnalyticsService:
    def __init__(self, runtime: Runtime) -> None:
        self.rt = runtime

    def compute(
        self, snapshot_id: uuid.UUID, dataset_id: uuid.UUID, cutoff: datetime
    ) -> tuple[Projection, dict[str, AccountMetrics], list[Community], dict[str, Any], str]:
        s = self.rt.settings
        configuration = algorithm_configuration(s)
        version = analytics_version(configuration)
        proj = export(self.rt.engine, dataset_id, cutoff)
        cfg = AlgorithmConfig(s.pagerank_damping, s.pagerank_max_iterations, s.pagerank_tolerance)
        metrics = compute_metrics(proj, cfg)
        communities = canonical_communities(proj, snapshot_id, version, s.louvain_resolution, s.louvain_seed)
        return proj, metrics, communities, configuration, version

    def run(
        self, snapshot_id: uuid.UUID, dataset_id: uuid.UUID, cutoff: datetime, analytics_run_id: uuid.UUID | None = None
    ) -> AnalyticsResult:
        started = utcnow()
        _proj, metrics, communities, configuration, version = self.compute(snapshot_id, dataset_id, cutoff)
        run_id = analytics_run_id or uuid.uuid4()
        configuration = {**configuration, "community_count": len(communities)}
        persist(self.rt, run_id, snapshot_id, version, configuration, started, metrics, communities)
        return AnalyticsResult(run_id, version, len(communities))


def persist(
    rt: Runtime,
    run_id: uuid.UUID,
    snapshot_id: uuid.UUID,
    version: str,
    configuration: dict[str, Any],
    started: datetime,
    metrics: dict[str, AccountMetrics],
    communities: list[Community],
) -> None:
    """One transaction: the SUCCEEDED analytics run, its communities, memberships and account metrics."""
    now = utcnow()
    membership = {member: (c.community_id, len(c.members)) for c in communities for member in c.members}
    raw = rt.engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.execute(
            "INSERT INTO analytics_runs (analytics_run_id, graph_snapshot_id, analytics_version, engine, "
            "algorithm_configuration, started_at, completed_at, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (run_id, snapshot_id, version, ENGINE, json.dumps(configuration), started, now, "SUCCEEDED"),
        )
        with cur.copy(
            "COPY communities (community_id, analytics_run_id, graph_snapshot_id, algorithm, algorithm_version, "
            "member_count, computed_at) FROM STDIN"
        ) as copy:
            for c in communities:
                copy.write_row(
                    (c.community_id, run_id, snapshot_id, "louvain", f"networkx-{nx.__version__}", len(c.members), now)
                )
        with cur.copy("COPY community_memberships (analytics_run_id, community_id, account_id) FROM STDIN") as copy:
            for c in communities:
                for member in c.members:
                    copy.write_row((run_id, c.community_id, member))
        with cur.copy(
            "COPY account_graph_metrics (analytics_run_id, account_id, degree, in_degree, out_degree, pagerank_raw, "
            "pagerank_norm, betweenness_raw, component_id, component_size, community_id, community_size) FROM STDIN"
        ) as copy:
            for account_id in sorted(metrics):
                m = metrics[account_id]
                cid, csize = membership[account_id]
                copy.write_row(
                    (
                        run_id,
                        account_id,
                        m.degree,
                        m.in_degree,
                        m.out_degree,
                        m.pagerank_raw,
                        m.pagerank_norm,
                        m.betweenness_raw,
                        m.component_id,
                        m.component_size,
                        cid,
                        csize,
                    )
                )
        raw.commit()
    except BaseException:
        raw.rollback()
        raise
    finally:
        raw.close()
