"""AT-GRAPH-05: a neighborhood request naming a retired snapshot returns 410 SNAPSHOT_RETIRED."""

import pytest
from sqlalchemy import select

from mulenetx.api.deps import get_services
from mulenetx.db.models.lineage import GraphSnapshot
from tests.apiutil import _Req
from tests.ingestutil import run_worker, seed_and_activate

pytestmark = pytest.mark.integration


def test_AT_GRAPH_05_retired_snapshot(app, client, users) -> None:
    admin = users("ADMIN")
    ds = seed_and_activate(app, client, admin, [("CA", "CB", 1.0, 1)], key="g5")
    rt = get_services(_Req(app)).runtime
    with rt.session_factory() as db:
        first = db.execute(select(GraphSnapshot.graph_snapshot_id)).scalar_one()
    # a second pipeline run activates a new snapshot and queues retirement of the first
    resp = client.post("/api/v1/pipeline-runs", json={"dataset_id": str(ds.dataset_id)}, headers=admin.headers)
    assert resp.status_code == 202
    run_worker(app)
    with rt.session_factory() as db:
        assert db.get(GraphSnapshot, first).status == "RETIRED"
    retired = client.get(
        "/api/v1/graph/neighborhood",
        params={"account_id": "g5:CA", "graph_snapshot_id": str(first)},
        headers=admin.headers,
    )
    assert retired.status_code == 410 and retired.json()["error"]["code"] == "SNAPSHOT_RETIRED"
    current = client.get("/api/v1/graph/neighborhood", params={"account_id": "g5:CA"}, headers=admin.headers)
    assert current.status_code == 200 and current.json()["graph_snapshot_id"] != str(first)
