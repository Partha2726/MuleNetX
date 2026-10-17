# Open questions, assumptions and conflicts

Every assumption the build makes where the SRS is silent, every conflict between the plan and the SRS,
and every environment limitation. Format per PLAN §0.3. Status: `open` (affects observable behavior,
needs Partha), `default` (plan or agent default applied; invisible or easy to change), `resolved`.

| ID | Task | Question / conflict | Options | Chosen | Status |
|---|---|---|---|---|---|
| OQ-01 | T01 | FastAPI needs `python-multipart` to parse the multipart upload of `POST /api/v1/ingestion` (SRS §19.2). It is not in PLAN §2. | add it / hand-parse multipart | Added `python-multipart` (transitive requirement of a SRS-mandated endpoint; no behavior beyond the SRS). | default |
| OQ-02 | T01 | Integration tests need PostgreSQL and Neo4j reachable from the host, but the app stack must publish only dashboard and backend ports (SR-22). | publish DB ports in main compose / run tests in containers / separate test compose | Separate `docker-compose.test.yml` (project `mulenetx-test`) with `postgres-test` and `neo4j-test` bound to 127.0.0.1 only. The app `docker-compose.yml` is unaffected and AT-OPS-01 checks it alone. | default |
| OQ-03 | T01 | Build host differs from the SRS §25.1 reference (8 vCPU / 32 GiB): this host has 8 vCPU / 8 GiB RAM, Docker VM 3.8 GiB. | — | Recorded; AT-OPS-05 results are reported against this hardware (T29). | open |
| OQ-04 | T02 | HTTP statuses outside the generic list (for example 405 Method Not Allowed) need an error code; the plan forbids adding codes. | add codes / reuse | Unlisted 4xx statuses keep their HTTP status and use code `VALIDATION_ERROR`; unlisted 5xx use `INTERNAL`. | default |
| OQ-05 | T02 | SRS §19.2 gives body limits only for some routes. | per-route only / default cap | Routes without an SRS limit get a 64 KiB body cap → `413 PAYLOAD_TOO_LARGE`. Upload route: `max_upload_bytes` + 64 KiB multipart overhead at the middleware; the file itself is capped exactly while streaming. | default |
| OQ-06 | T03 | PLAN §6 puts `transactions` in 0001 and `ingestion_runs` in 0002, but `transactions.ingestion_run_id` is an FK to `ingestion_runs` (parents first, §6.7). | move table / defer FK | Column created in 0001; FK constraint `transactions_ingestion_run_fk` added in 0002 after `ingestion_runs`. | default |
| OQ-07 | T03 | PLAN names `docker/postgres/init.sql`, but role passwords must come from the environment (SR-15) and plain `.sql` init files cannot read env. | sql / shell | `docker/postgres/init.sh` (psql with `-v` variables). | default |
| OQ-08 | T03 | "FK accounts; same dataset" for `transactions.source_account_id`/`destination_account_id`. | app check / composite FK | Composite FKs `(dataset_id, source_account_id)` → `accounts(dataset_id, account_id)` backed by `UNIQUE(dataset_id, account_id)` on accounts. | default |
| OQ-09 | T03 | Per-run UNLOGGED staging tables (§7.2) need CREATE privilege, which the app role must not have on `public`. | grant on public / separate schema | Migration 0001 creates schema `staging` with `USAGE, CREATE` for `mulenetx_app`. | default |
| OQ-10 | T03 | `auth_sessions.role_at_issue` has no explicit CHECK in §6.3.1. | none / role CHECK | Added CHECK to the three roles (same domain as `users.role`). | default |
