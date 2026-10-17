# Open questions, assumptions and conflicts

Every assumption the build makes where the SRS is silent, every conflict between the plan and the SRS,
and every environment limitation. Format per PLAN §0.3. Status: `open` (affects observable behavior,
needs Partha), `default` (plan or agent default applied; invisible or easy to change), `resolved`.

| ID | Task | Question / conflict | Options | Chosen | Status |
|---|---|---|---|---|---|
| OQ-01 | T01 | FastAPI needs `python-multipart` to parse the multipart upload of `POST /api/v1/ingestion` (SRS §19.2). It is not in PLAN §2. | add it / hand-parse multipart | Added `python-multipart` (transitive requirement of a SRS-mandated endpoint; no behavior beyond the SRS). | default |
| OQ-02 | T01 | Integration tests need PostgreSQL and Neo4j reachable from the host, but the app stack must publish only dashboard and backend ports (SR-22). | publish DB ports in main compose / run tests in containers / separate test compose | Separate `docker-compose.test.yml` (project `mulenetx-test`) with `postgres-test` and `neo4j-test` bound to 127.0.0.1 only. The app `docker-compose.yml` is unaffected and AT-OPS-01 checks it alone. | default |
| OQ-03 | T01 | Build host differs from the SRS §25.1 reference (8 vCPU / 32 GiB): this host has 8 vCPU / 8 GiB RAM, Docker VM 3.8 GiB. | — | Recorded; AT-OPS-05 results are reported against this hardware (T29). | open |
