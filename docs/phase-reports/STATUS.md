# Build status

Live handoff file. A fresh session reads this first, then the latest `PHASE_n.md`, then `docs/PLAN.md`.

- **Branch:** `rebuild` (one commit per task, message `Tnn: ...`).
- **Current task:** T30: suspicious-flow vocabulary and analytical path enumeration (Phase 4).
- **Completed tasks:** T01–T29. The Phase 1 and Phase 2 gates passed. The Phase 3 gate is **not passed**: AT-OPS-05 needs the reference environment and slice (OQ-72); every other Phase 3 AT passes.
- **Test status (last run):** `cd backend && uv run pytest -m "not docker and not perf"` → 406 passed. Docker: AT-OPS-01/02/03 passed. `tests/perf`: 2 passed, 1 failed (reference precondition). `cd frontend && npm test` → 40 passed; `npm run lint` and `npm run build` are clean.
- **Environment:** test services `docker compose -f docker-compose.test.yml -p mulenetx-test up -d --wait`. App stack `docker compose up --build -d` with a local `.env` (not committed). Keep ≥ 3 GB host disk free (Docker hangs when the disk fills). Other projects' containers auto-start with Docker Desktop and are stopped for this work.
- **Blockers:** AT-OPS-05 / Phase 3 gate. It needs the PaySim file plus reference hardware, or Partha's approval of the documented exception (OQ-72). Work continues with Phase 4 as instructed.
- **Next action:** T30 per PLAN §10.
- **Local demo:** `PYTHONPATH=. uv run python <scratch>/seed_demo.py` is not in the repo. To demo, use the Compose stack and upload a PaySim CSV from the dashboard (Ingestion page).
- **Frontend:** `frontend/` (see its README). Design context lives in `PRODUCT.md`, `DESIGN.md` and `.impeccable/`. The type contract comes from `make gen-types` after any API change (`docs/openapi.json` is checked by `tests/api/test_inventory.py`).
