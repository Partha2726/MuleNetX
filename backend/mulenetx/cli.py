"""Command-line entry points (`mulenetx <command>`)."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable

from mulenetx.core.config import get_settings
from mulenetx.core.logging import configure_logging


def cmd_migrate_neo4j(args: argparse.Namespace) -> int:
    from mulenetx.graph.neo4j_client import Neo4jClient

    s = get_settings()
    client = Neo4jClient(s.neo4j_uri, s.neo4j_user, s.neo4j_password)
    try:
        client.create_schema()
    finally:
        client.close()
    print("neo4j constraints and indexes are in place")
    return 0


def cmd_check_schema(args: argparse.Namespace) -> int:
    from mulenetx.db.engine import make_engine
    from mulenetx.db.schema_version import code_head, database_revision

    engine = make_engine(get_settings().postgres_dsn, pool_size=1)
    try:
        revision = database_revision(engine)
    finally:
        engine.dispose()
    if revision != code_head():
        print(f"schema version mismatch: database={revision} code={code_head()}", file=sys.stderr)
        return 1
    print(f"schema version {revision} matches")
    return 0


def cmd_bootstrap_admin(args: argparse.Namespace) -> int:
    from mulenetx.audit.service import AuditService
    from mulenetx.auth.passwords import Passwords
    from mulenetx.auth.service import AuthService
    from mulenetx.core.errors import AppError
    from mulenetx.core.runtime import Runtime

    s = get_settings()
    username = s.mulenetx_bootstrap_admin_username
    password = s.mulenetx_bootstrap_admin_password
    if not username or not password:
        print("MULENETX_BOOTSTRAP_ADMIN_USERNAME and MULENETX_BOOTSTRAP_ADMIN_PASSWORD are required", file=sys.stderr)
        return 2
    rt = Runtime(s)
    service = AuthService(s, AuditService(rt.session_factory), Passwords(s))
    try:
        with rt.session_factory() as db:
            user = service.bootstrap_admin(db, username, password)
    except AppError as exc:
        print(exc.message, file=sys.stderr)
        return 1
    finally:
        rt.close()
    print(f"administrator {user.username} created")
    return 0


COMMANDS: dict[str, tuple[Callable[[argparse.Namespace], int], str]] = {
    "bootstrap-admin": (cmd_bootstrap_admin, "create the first ADMIN from the environment (refuses if one exists)"),
    "migrate-neo4j": (cmd_migrate_neo4j, "create the Neo4j constraints and indexes (SRS §6.8.1)"),
    "check-schema": (cmd_check_schema, "exit 1 unless the database schema version equals the code head"),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mulenetx")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, (_fn, help_text) in COMMANDS.items():
        sub.add_parser(name, help=help_text)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(get_settings().log_level)
    fn, _ = COMMANDS[args.command]
    return fn(args)


if __name__ == "__main__":
    sys.exit(main())
