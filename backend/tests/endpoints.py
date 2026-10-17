"""Registry of implemented protected endpoints with their SRS §19.2 permission.

Each task adds its endpoints. Used by AT-SEC-01 (unauthenticated), AT-SEC-04 (role denials) and the
inventory test. Path parameters use placeholder IDs; permission checks run before resource lookups.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PLACEHOLDER = "00000000-0000-4000-8000-000000000000"


@dataclass(frozen=True)
class Endpoint:
    method: str
    path: str
    permission: str  # "authenticated" for endpoints that only need a session
    body: dict[str, Any] | None = None
    params: dict[str, Any] = field(default_factory=dict)
    also: tuple[str, ...] = ()  # other permissions checked first on the same endpoint

    @property
    def url(self) -> str:
        return self.path.replace("{id}", PLACEHOLDER).replace("{version}", "v0")


ENDPOINTS: list[Endpoint] = [
    Endpoint("POST", "/api/v1/auth/logout", "authenticated"),
    Endpoint("GET", "/api/v1/auth/me", "authenticated"),
    Endpoint("GET", "/api/v1/users", "user.read"),
    Endpoint("POST", "/api/v1/users", "user.manage", {"username": "x-user", "role": "ANALYST", "password": "p" * 16}),
    Endpoint("PATCH", "/api/v1/users/{id}", "user.manage", {"is_active": True}),
    Endpoint("PATCH", "/api/v1/users/{id}", "role.manage", {"role": "ANALYST"}, also=("user.manage",)),
]
