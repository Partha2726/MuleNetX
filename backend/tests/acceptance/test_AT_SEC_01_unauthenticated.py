"""AT-SEC-01: an unauthenticated request to any protected endpoint returns 401 and no protected data."""

import pytest

from tests.endpoints import ENDPOINTS

pytestmark = pytest.mark.integration


def _protected_routes(app):
    out = []
    for route in app.routes:
        path = getattr(route, "path", "")
        if not path.startswith("/api/v1") or path == "/api/v1/auth/login":
            continue
        for method in sorted(getattr(route, "methods", set()) - {"HEAD", "OPTIONS"}):
            out.append((method, path))
    return out


def test_AT_SEC_01_every_protected_route_requires_auth(app, client) -> None:
    routes = _protected_routes(app)
    assert routes, "no protected routes registered"
    for method, path in routes:
        url = path
        for name in ("{id}", "{user_id}", "{version}", "{level}", "{path_id}", "{type}", "{subject_id}"):
            url = url.replace(name, "00000000-0000-4000-8000-000000000000")
        for headers in ({}, {"Authorization": "Bearer not-a-real-token"}, {"Authorization": "Basic abc"}):
            resp = client.request(method, url, headers=headers, json={})
            assert resp.status_code == 401, f"{method} {path} -> {resp.status_code}"
            assert set(resp.json()) == {"error"}
            assert resp.json()["error"]["code"] == "UNAUTHENTICATED"


def test_AT_SEC_01_registry_covers_routes(app) -> None:
    registered = {(e.method, e.path.replace("{id}", "{user_id}")) for e in ENDPOINTS}
    for method, path in _protected_routes(app):
        normalized = path
        assert (method, normalized) in registered or (method, path.replace("{user_id}", "{id}")) in {
            (e.method, e.path) for e in ENDPOINTS
        }, f"{method} {path} missing from tests/endpoints.py"
