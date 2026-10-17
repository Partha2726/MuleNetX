"""Job-kind → handler registry. Each task registers its handlers here."""

from __future__ import annotations

from mulenetx.jobs.runner import Handler


def build_handlers() -> dict[str, Handler]:
    return {}
