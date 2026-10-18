# Build status

Live handoff file. A fresh session reads this first, then the latest `PHASE_n.md`, then `docs/PLAN.md`.

- **Branch:** `rebuild` (one commit per task, message `Tnn: ...`).
- **Current task:** T40, the copilot backend (optional track). Phase 6 follows.
- **Completed tasks:** T01–T39. Gates passed: Phases 1, 2, 4 and 5. Phase 3 is **not passed** because AT-OPS-05 needs the reference environment and slice (OQ-72).
- **Test status (last run):** `cd backend && uv run pytest -m "not docker and not perf"` → 486 passed. Docker: AT-OPS-01, AT-OPS-02 and AT-OPS-03 passed. `cd frontend && npm test` → 49 passed; lint and build are clean.
- **Environment:** test services `docker compose -f docker-compose.test.yml -p mulenetx-test up -d --wait`. App stack `docker compose up --build -d` with a local `.env` (not committed). Keep ≥ 3 GB host disk free (Docker hangs when the disk fills). Other projects' containers auto-start with Docker Desktop and are stopped for this work.
- **Blockers:** AT-OPS-05 / Phase 3 gate. It needs the PaySim file plus reference hardware, or Partha's approval of the documented exception (OQ-72). Work continues with Phase 4 as instructed.
- **Next action:** T40 per PLAN §10. Never run a dev worker against the test database while tests run; it claims test jobs.
- **Local demo:** `PYTHONPATH=. uv run python <scratch>/seed_demo.py` is not in the repo. To demo, use the Compose stack and upload a PaySim CSV from the dashboard (Ingestion page).
- **Frontend:** `frontend/` (see its README). Design context lives in `PRODUCT.md`, `DESIGN.md` and `.impeccable/`. The type contract comes from `make gen-types` after any API change (`docs/openapi.json` is checked by `tests/api/test_inventory.py`).
