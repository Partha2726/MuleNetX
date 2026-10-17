# Build status

Live handoff file. A fresh session reads this first, then the latest `PHASE_n.md`, then `docs/PLAN.md`.

- **Branch:** `rebuild` (one commit per task, message `Tnn: ...`).
- **Current task:** T13 — graph analytics and communities (Phase 2).
- **Completed tasks:** T01–T12 (Phase 1 gate passed; see `PHASE_1.md`).
- **Test status (last run):** `cd backend && uv run pytest -m "not docker"` → 219 passed, 1 xfailed (AT-SEC-02 strict xfail until T24, permitted by PLAN T06). Docker acceptance AT-OPS-01 and AT-OPS-03 passed.
- **Environment:** test services `docker compose -f docker-compose.test.yml -p mulenetx-test up -d --wait`. App stack `docker compose up --build -d` with a local `.env` (not committed). Host 8 vCPU / 8 GiB, Docker VM 3.8 GiB, ~6 GiB free disk.
- **Blockers:** none.
- **Next action:** T13 per PLAN §10.
