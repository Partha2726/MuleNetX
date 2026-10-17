# Build status

Live handoff file. A fresh session reads this first, then the latest `PHASE_n.md`, then `docs/PLAN.md`.

- **Branch:** `rebuild` (one commit per task, message `Tnn: ...`).
- **Current task:** T09 — ingestion (PaySim adapter).
- **Completed tasks:** T01–T08.
- **Test status (last run):** `cd backend && uv run pytest -m "not docker"` → 154 passed, 1 xfailed (AT-SEC-02 strict xfail until T24, permitted by PLAN T06). `-m docker` AT-OPS-01 passed against the Compose stack.
- **Environment:** test services `docker compose -f docker-compose.test.yml -p mulenetx-test up -d --wait` (PostgreSQL 127.0.0.1:55432, Neo4j 127.0.0.1:57687). App stack `docker compose up --build -d` with a local `.env` (not committed; secrets generated). Host: 8 vCPU / 8 GiB, Docker VM 3.8 GiB, ~6 GiB free disk.
- **Blockers:** none.
- **Next action:** implement T09 per PLAN §10 T09.
