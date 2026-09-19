# Running and deploying ClauseGraph

## Local PostgreSQL stack
`docker compose up --build` starts PostgreSQL 17, applies migrations, and starts API, worker and frontend. Open http://localhost:3000. No cloud resources are created. The PostgreSQL service is internal; API and frontend ports bind to localhost. Documents and database records persist in named volumes. `docker compose down` stops the stack while preserving those volumes. Reset one demo through the UI or `python scripts/demo_session.py --reset-session TOKEN`; deleting all volumes is deliberately not part of normal reset.

## DigitalOcean App Platform template

ClauseGraph Verify adds checksum-tracked migration `003_verification_history.sql` for session-private verification runs and daily outcome points. Apply the same migrations before starting the updated API/worker. SQLite creates matching tables automatically. The PostgreSQL CI check now writes and reads a verification result after applying migrations twice. No Timescale extension is required; no Tiger Data service, hypertable performance or remote deployment has been live-tested in this delivery.
`deploy/digitalocean.app.yaml` is a template, not a completed deployment. Replace the repository and runtime secret placeholders, choose the branch containing the implementation, and review resource costs before submitting it. API and worker share the backend image; a PRE_DEPLOY job applies checksum-tracked migrations. Frontend `/api` traffic routes directly to the API with the prefix preserved. The app needs an existing Tiger Data PostgreSQL connection URL (`sslmode=require`) and an existing private Spaces bucket/key pair. Production configuration rejects SQLite and missing Spaces. Provider keys are runtime server secrets and never `NEXT_PUBLIC_*` values.

Use App Platform encrypted per-component environment settings for secrets. Model IDs and base URLs remain configurable. For Spaces, use a scoped key with only the target bucket permissions needed for private object read/write/delete. Do not enable a public document CDN. API original-download routes authenticate the session and stream bytes, not public object links.

After approval to deploy, validate the filled template with `doctl apps spec validate deploy/digitalocean.app.yaml`; create/update the app using that reviewed spec. Then check health, migrations, worker pickup, per-session deletion, synthetic demo arithmetic, provider smoke status and one consenting synthetic-document extraction before processing real financial documents.

This build does not provision paid resources. Local Docker execution and remote deployment depend on an available Docker daemon/accounts. Session bearer credentials grant access to one private workspace; keep them private. Application-level account recovery, multi-device sign-in, operational retention policy and production abuse controls are not supplied by this prototype.

Configuration follows the official [App Platform specification](https://docs.digitalocean.com/products/app-platform/reference/app-spec/) and [Spaces private ACL/API documentation](https://docs.digitalocean.com/products/spaces/reference/s3-compatibility/). Paid instance sizing is a deployment-time choice.
