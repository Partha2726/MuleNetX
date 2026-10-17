"""AT-SEC-02: an ANALYST calling the audit endpoint receives 403 and no audit data.

`GET /api/v1/audit` is built in T24. Until then this is the single permitted strict xfail of the plan (T06).
"""

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.xfail(strict=True, reason="GET /api/v1/audit is implemented in T24 (PLAN T06)")
def test_AT_SEC_02_analyst_cannot_read_audit(client, users) -> None:
    analyst = users("ANALYST")
    resp = client.get("/api/v1/audit", headers=analyst.headers)
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"
    assert "items" not in resp.json()
