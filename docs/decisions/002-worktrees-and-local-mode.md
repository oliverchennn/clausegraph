# ADR 002: Isolated workstreams and credential-free local development
Accepted. Three workstreams use separate Git branches/worktrees and publish live checkpoints through agent messages. Integration owns schema, migrations, dependency lockfiles and generated types. Existing main history is preserved; final work is integrated on codex/integration.

Local development may use SQLite with a prominent synthetic demo. Production configuration targets Tiger Data PostgreSQL and private DigitalOcean Spaces. No credential or Docker daemon was available at initial inspection. Actual provider requests and deployment must not be claimed as tested until they run. HTTP adapters expose bounded timeouts/retries and failures without silently substituting fixtures.
