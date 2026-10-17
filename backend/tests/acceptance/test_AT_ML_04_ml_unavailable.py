"""AT-ML-04: when no model can be trained, the pipeline still reaches READY with the ML component unavailable
and no historical score is substituted (§7.6 rule 4, §11.12). The risk-API half is asserted in T19."""

import pytest
from sqlalchemy import select

from mulenetx.api.deps import get_services
from mulenetx.db.models.lineage import ModelVersion, RiskLogicVersion
from tests.apiutil import _Req
from tests.ingestutil import seed_and_activate

pytestmark = pytest.mark.integration


def test_AT_ML_04_no_model_pipeline_still_ready(app, client, users) -> None:
    admin = users("ADMIN")
    edges = [(f"C{i}", f"C{i + 1}", 10.0 + i, i) for i in range(30)]  # no fraud labels → no positives
    seed_and_activate(app, client, admin, edges, key="noml")
    rt = get_services(_Req(app)).runtime
    with rt.session_factory() as db:
        assert db.execute(select(ModelVersion)).first() is None
        rl = db.execute(select(RiskLogicVersion)).scalars().all()
    assert len(rl) == 1  # the risk logic version is still created (§11 / PLAN T17)
    assert rl[0].normalization_reference["model_version"] is None
    assert "positive and negative" in rl[0].normalization_reference["training_failure"]
    ctx = client.get("/api/v1/context", headers=admin.headers).json()
    assert ctx["model_version"] is None and ctx["is_active"] is True
