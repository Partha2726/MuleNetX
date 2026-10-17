"""Worker entrypoint (SRS §4.4). The claim loop is implemented in T07."""

from __future__ import annotations

import logging
import sys
import time

from mulenetx.core.config import get_settings
from mulenetx.core.logging import configure_logging
from mulenetx.core.runtime import Runtime
from mulenetx.db.schema_version import code_head, schema_matches

logger = logging.getLogger("mulenetx.worker")


def main() -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    runtime = Runtime(settings)
    if not schema_matches(runtime.engine):
        logger.error("schema version does not match code head %s; refusing to start", code_head())
        return 1
    logger.info("worker started")
    while True:
        time.sleep(settings.worker_poll_seconds)


if __name__ == "__main__":
    sys.exit(main())
