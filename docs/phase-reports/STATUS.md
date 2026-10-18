# Build status

Live handoff file. A fresh session reads this first, then the latest `PHASE_n.md`, then `docs/PLAN.md`.

- **Branch:** `rebuild` (one commit per task, message `Tnn: ...`).
- **Current task:** T22 — interactive money-flow paths (Phase 3).
- **Completed tasks:** T01–T21 (Phase 1 and Phase 2 gates passed).
- **Test status (last run):** `cd backend && uv run pytest -m "not docker"` → 351 passed, 1 xfailed (AT-SEC-02 strict xfail until T24). Docker acceptance AT-OPS-01/03 passed in Phase 1.
- **Environment:** test services `docker compose -f docker-compose.test.yml -p mulenetx-test up -d --wait`. App stack `docker compose up --build -d` with a local `.env` (not committed). Keep ≥ 3 GB host disk free (Docker hangs when the disk fills). Other projects' containers auto-start with Docker Desktop and are stopped for this work.
- **Blockers:** none.
- **Next action:** T22 per PLAN §10.
