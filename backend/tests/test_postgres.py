"""Real PostgreSQL check in CI; skipped locally unless a disposable DB is supplied."""
import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import text


@pytest.mark.skipif(not os.getenv("POSTGRES_TEST_URL"), reason="POSTGRES_TEST_URL not configured")
def test_postgres_migration_job_lease_and_session_isolation(tmp_path):
    from clausegraph.config import Settings
    from clausegraph.demo import load_demo
    from clausegraph.schemas import DependencyGraph, Workspace
    from clausegraph.storage import Store

    url = os.environ["POSTGRES_TEST_URL"]
    root = Path(__file__).resolve().parents[2]
    env = {**os.environ, "DATABASE_URL": url, "ENVIRONMENT": "development"}
    for _ in range(2):
        subprocess.run([sys.executable, str(root / "scripts" / "migrate.py")], env=env, cwd=root, check=True)
    store = Store(Settings(database_url=url, environment="development", local_storage_path=tmp_path))
    store.initialize()
    scenario, documents, rules = load_demo()
    import secrets
    sid = "ci-" + secrets.token_urlsafe(18)
    workspace = Workspace(session_id=sid, mode="synthetic", revision=1, scenario=scenario,
                          documents=documents, rules=rules, graph=DependencyGraph())
    store.create(workspace)
    try:
        job = store.enqueue(sid, documents[0].id, 1, {"synthetic": True})
        first = store.claim("worker-a")
        assert first and first["id"] == job.id
        assert store.claim("worker-b") is None
        assert store.get_job("different-session", job.id) is None
        with store.engine.connect() as connection:
            rows = connection.execute(text("SELECT kind, SUM(expense_cents) FROM financial_event_daily_totals WHERE session_id=:sid GROUP BY kind"), {"sid": sid}).all()
        assert rows == [("projected", 288000)]
    finally:
        store.delete_session(sid)
        store.engine.dispose()
