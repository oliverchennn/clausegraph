"""Apply versioned PostgreSQL migrations; local SQLite uses matching metadata."""
import hashlib
import sys
from pathlib import Path

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


def migrate():
    from clausegraph.config import Settings
    from clausegraph.storage import Store, metadata

    store = Store(Settings())
    if store.engine.dialect.name == "sqlite":
        metadata.create_all(store.engine)
        print("Initialized local SQLite development schema.")
        return
    with store.engine.begin() as connection:
        connection.execute(text("SELECT pg_advisory_xact_lock(748302191)"))
        connection.exec_driver_sql("CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, checksum TEXT NOT NULL, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())")
        for path in sorted((ROOT / "migrations").glob("*.sql")):
            source = path.read_text(encoding="utf-8").replace("\r\n", "\n")
            checksum = hashlib.sha256(source.encode()).hexdigest()
            existing = connection.execute(text("SELECT checksum FROM schema_migrations WHERE name=:name"), {"name": path.name}).scalar_one_or_none()
            if existing is not None:
                if checksum != existing:
                    raise RuntimeError(f"Previously applied migration changed: {path.name}")
                continue
            connection.exec_driver_sql(source)
            connection.execute(text("INSERT INTO schema_migrations (name,checksum) VALUES (:name,:checksum)"), {"name": path.name, "checksum": checksum})
            print(f"Applied {path.name}")
    store.engine.dispose()


if __name__ == "__main__":
    migrate()
