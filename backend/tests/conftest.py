"""Shared test configuration."""

from __future__ import annotations

from typing import Any

import pytest

from mulenetx.core.config import Settings

BASE_ENV: dict[str, Any] = {
    "postgres_dsn": "postgresql+psycopg://mulenetx_app:test-app-secret@127.0.0.1:55432/mulenetx",
    "postgres_owner_dsn": "postgresql+psycopg://mulenetx_owner:test-owner-secret@127.0.0.1:55432/mulenetx",
    "neo4j_uri": "bolt://127.0.0.1:57687",
    "neo4j_user": "neo4j",
    "neo4j_password": "test-neo4j-secret",
    "cors_allowed_origins": ["http://localhost:8080"],
    "artifact_dir": "/tmp/mulenetx-test/artifacts",
    "staging_dir": "/tmp/mulenetx-test/staging",
}


def make_settings(**overrides: Any) -> Settings:
    values = {**BASE_ENV, **overrides}
    return Settings(**values)


@pytest.fixture
def settings() -> Settings:
    return make_settings()
