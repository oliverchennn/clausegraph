"""Transactional snapshots, audit projections, and a leased PostgreSQL job queue.

SQLite is a local development fallback. Production schema creation is explicit.
Bearer tokens never occur in object keys or log messages.
"""
import hashlib
import secrets
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import boto3
from botocore.config import Config
from sqlalchemy import (
    JSON, BigInteger, Column, Date, DateTime, ForeignKey, Index, Integer, MetaData,
    String, Table, and_, create_engine, delete, insert, or_, select, update,
)
from sqlalchemy.pool import StaticPool

from clausegraph.config import Settings
from clausegraph.schemas import DailyBalance, JobStatus, PlanResult, VerificationResult, Workspace

metadata = MetaData()
sessions = Table(
    "sessions", metadata,
    Column("id", String(128), primary_key=True),
    Column("snapshot", JSON, nullable=False),
    Column("revision", Integer, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


def session_column():
    return Column("session_id", String(128), ForeignKey("sessions.id", ondelete="CASCADE"),
                  primary_key=True)


document_versions = Table(
    "document_versions", metadata, session_column(),
    Column("id", String(128), primary_key=True), Column("version", Integer, primary_key=True),
    Column("sha256", String(64), nullable=False), Column("original_key", String(512)),
    Column("payload", JSON, nullable=False),
)
rule_versions = Table(
    "rule_versions", metadata, session_column(),
    Column("id", String(128), primary_key=True), Column("version", Integer, primary_key=True),
    Column("payload", JSON, nullable=False),
)
financial_events = Table(
    "financial_events", metadata, session_column(), Column("id", String(128), primary_key=True),
    Column("event_date", Date, nullable=False), Column("amount_cents", BigInteger, nullable=False),
    Column("direction", String(16), nullable=False), Column("kind", String(16), nullable=False),
    Column("payload", JSON, nullable=False),
)
scenario_runs = Table(
    "scenario_runs", metadata, session_column(), Column("id", String(128), primary_key=True),
    Column("revision", Integer, nullable=False), Column("payload", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)
daily_balances = Table(
    "daily_balances", metadata, session_column(),
    Column("run_id", String(128), primary_key=True), Column("series", String(16), primary_key=True),
    Column("event_date", Date, primary_key=True), Column("balance_cents", BigInteger, nullable=False),
    Column("income_cents", BigInteger, nullable=False), Column("expense_cents", BigInteger, nullable=False),
    Column("kind", String(16), nullable=False),
)
verification_runs = Table(
    "verification_runs", metadata, session_column(), Column("id", String(128), primary_key=True),
    Column("plan_id", String(128), nullable=False), Column("revision", Integer, nullable=False),
    Column("status", String(16), nullable=False), Column("payload", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)
verification_points = Table(
    "verification_points", metadata, session_column(),
    Column("run_id", String(128), primary_key=True), Column("series", String(16), primary_key=True),
    Column("event_date", Date, primary_key=True), Column("balance_cents", BigInteger, nullable=False),
    Column("income_cents", BigInteger, nullable=False), Column("expense_cents", BigInteger, nullable=False),
    Column("kind", String(16), nullable=False),
)
jobs = Table(
    "jobs", metadata,
    Column("id", String(128), primary_key=True),
    Column("session_id", String(128), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
    Column("document_id", String(128), nullable=False), Column("base_revision", Integer, nullable=False),
    Column("status", String(16), nullable=False), Column("stage", String(128), nullable=False),
    Column("progress", Integer, nullable=False), Column("error", String(512)),
    Column("payload", JSON, nullable=False), Column("lease_owner", String(128)),
    Column("lease_until", DateTime(timezone=True)), Column("attempts", Integer, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)
Index("ix_jobs_claim", jobs.c.status, jobs.c.lease_until, jobs.c.created_at)
Index("ix_events_timeline", financial_events.c.session_id, financial_events.c.event_date,
      financial_events.c.kind)


class MissingSession(Exception):
    pass


class StaleRevision(Exception):
    pass


def utcnow() -> datetime:
    return datetime.now(UTC)


class Store:
    def __init__(self, settings: Settings):
        self.settings = settings
        url = settings.database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        options: dict[str, Any] = {"pool_pre_ping": True}
        if url.startswith("sqlite"):
            options["connect_args"] = {"check_same_thread": False, "timeout": 15}
            if ":memory:" in url:
                options["poolclass"] = StaticPool
            elif url.startswith("sqlite:///"):
                Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(url, **options)

    def initialize(self):
        if self.engine.dialect.name == "sqlite":
            metadata.create_all(self.engine)
        else:
            # Fail early with a visible migration error; no implicit production DDL.
            with self.engine.connect() as connection:
                connection.execute(select(sessions.c.id).limit(0))

    def create(self, workspace: Workspace) -> Workspace:
        with self.engine.begin() as connection:
            connection.execute(insert(sessions).values(id=workspace.session_id,
                revision=workspace.revision, snapshot=workspace.model_dump(mode="json"), created_at=utcnow()))
            self._project(connection, workspace)
        return workspace

    def get(self, session_id: str) -> Workspace:
        with self.engine.connect() as connection:
            payload = connection.execute(select(sessions.c.snapshot).where(sessions.c.id == session_id)).scalar_one_or_none()
        if payload is None:
            raise MissingSession()
        workspace = Workspace.model_validate(payload)
        if workspace.plan:
            self._restore_series(session_id, workspace.plan)
        workspace.jobs = self.list_jobs(session_id)
        return workspace

    def _restore_series(self, session_id: str, plan: PlanResult):
        with self.engine.connect() as connection:
            rows = connection.execute(select(daily_balances).where(daily_balances.c.session_id == session_id,
                daily_balances.c.run_id == plan.id).order_by(daily_balances.c.event_date)).mappings().all()
        for series in ("baseline", "proposed"):
            simulation = getattr(plan, series)
            event_ids = {point.date: point.event_ids for point in simulation.daily}
            selected = [row for row in rows if row["series"] == series]
            if len(selected) != len(simulation.daily):
                raise RuntimeError("Persisted chart series is incomplete")
            simulation.daily = [DailyBalance(date=row["event_date"], balance_cents=row["balance_cents"],
                income_cents=row["income_cents"], expense_cents=row["expense_cents"],
                event_ids=event_ids.get(row["event_date"], [])) for row in selected]

    def history(self, session_id: str) -> list[PlanResult]:
        with self.engine.connect() as connection:
            payloads = connection.execute(select(scenario_runs.c.payload).where(scenario_runs.c.session_id == session_id)
                .order_by(scenario_runs.c.created_at.desc(), scenario_runs.c.id.desc()).limit(30)).scalars().all()
        plans = [PlanResult.model_validate(payload) for payload in payloads]
        for plan in plans:
            self._restore_series(session_id, plan)
        return plans

    def save_verification(self, session_id: str, result: VerificationResult) -> VerificationResult:
        """Persist against the still-active plan without changing its snapshot or revision."""
        with self.engine.begin() as connection:
            # A no-op conditional write acquires a row/write lock on both PostgreSQL and
            # SQLite before the active-plan check; SELECT FOR UPDATE alone does not on SQLite.
            locked = connection.execute(update(sessions).where(sessions.c.id == session_id,
                sessions.c.revision == result.revision).values(revision=result.revision))
            if locked.rowcount != 1:
                if connection.execute(select(sessions.c.id).where(sessions.c.id == session_id)).first() is None:
                    raise MissingSession()
                raise StaleRevision()
            snapshot = connection.execute(select(sessions.c.snapshot).where(
                sessions.c.id == session_id)).scalar_one()
            active = snapshot.get("plan")
            if not active or active["id"] != result.plan_id or active["revision"] != result.revision:
                raise StaleRevision()
            connection.execute(insert(verification_runs).values(session_id=session_id, id=result.id,
                plan_id=result.plan_id, revision=result.revision, status=result.status,
                payload=result.model_dump(mode="json"), created_at=result.generated_at))
            if result.worst_case and result.worst_case.daily:
                connection.execute(insert(verification_points), [dict(session_id=session_id, run_id=result.id,
                    series="worst_case", event_date=point.date, balance_cents=point.balance_cents,
                    income_cents=point.income_cents, expense_cents=point.expense_cents,
                    kind="projected") for point in result.worst_case.daily])
        return result

    def verifications(self, session_id: str) -> list[VerificationResult]:
        # Persisted points are authoritative; missing rows fail closed instead of
        # silently reverting to the duplicate series in the result payload.
        with self.engine.connect() as connection:
            payloads = connection.execute(select(verification_runs.c.payload).where(
                verification_runs.c.session_id == session_id).order_by(
                    verification_runs.c.created_at.desc(), verification_runs.c.id.desc()).limit(30)).scalars().all()
            results = [VerificationResult.model_validate(payload) for payload in payloads]
            if not results:
                return []
            rows = connection.execute(select(verification_points).where(
                verification_points.c.session_id == session_id,
                verification_points.c.run_id.in_([result.id for result in results]))
                .order_by(verification_points.c.event_date)).mappings().all()
            for result in results:
                if result.worst_case is None:
                    continue
                points = [row for row in rows if row["run_id"] == result.id and row["series"] == "worst_case"]
                if len(points) != len(result.worst_case.daily):
                    raise RuntimeError("Persisted verification chart series is incomplete")
                event_ids = {point.date: point.event_ids for point in result.worst_case.daily}
                result.worst_case.daily = [DailyBalance(date=row["event_date"], balance_cents=row["balance_cents"],
                    income_cents=row["income_cents"], expense_cents=row["expense_cents"],
                    event_ids=event_ids.get(row["event_date"], [])) for row in points]
        return results

    def mutate(self, session_id: str, change: Callable[[Workspace], None],
               expected_revision: int | None = None, invalidate: bool = True,
               job_guard: tuple[str, str] | None = None, job_result: dict | None = None,
               original: tuple[str, int, str] | None = None, enqueue: dict | None = None,
               purge_document_id: str | None = None, purge_rule_ids: list[str] | None = None,
               reset_history: bool = False, supersede_document_id: str | None = None) -> Workspace:
        with self.engine.begin() as connection:
            row = connection.execute(select(sessions).where(sessions.c.id == session_id).with_for_update()).mappings().first()
            if row is None:
                raise MissingSession()
            if expected_revision is not None and row["revision"] != expected_revision:
                raise StaleRevision()
            if job_guard:
                job = connection.execute(select(jobs).where(jobs.c.id == job_guard[0],
                    jobs.c.session_id == session_id, jobs.c.lease_owner == job_guard[1],
                    jobs.c.status == "running", jobs.c.lease_until > utcnow()).with_for_update()).mappings().first()
                if job is None:
                    raise StaleRevision()
            workspace = Workspace.model_validate(row["snapshot"])
            change(workspace)
            if invalidate:
                workspace.revision += 1
                workspace.plan = None
            updated = connection.execute(update(sessions).where(
                sessions.c.id == session_id, sessions.c.revision == row["revision"]
            ).values(snapshot=workspace.model_dump(mode="json"), revision=workspace.revision))
            if updated.rowcount != 1:
                raise StaleRevision()
            if reset_history:
                for table in (jobs, verification_points, verification_runs, daily_balances, scenario_runs,
                              financial_events, rule_versions, document_versions):
                    connection.execute(delete(table).where(table.c.session_id == session_id))
            if purge_document_id:
                self._purge_document_history(connection, session_id, purge_document_id, purge_rule_ids or [])
            if supersede_document_id:
                connection.execute(update(jobs).where(jobs.c.session_id == session_id,
                    jobs.c.document_id == supersede_document_id, jobs.c.status.in_(("queued", "running"))).values(
                        status="failed", stage="superseded", error="A newer document version replaced this source.", updated_at=utcnow()))
            self._project(connection, workspace)
            if original:
                connection.execute(update(document_versions).where(document_versions.c.session_id == session_id,
                    document_versions.c.id == original[0], document_versions.c.version == original[1]).values(original_key=original[2]))
            if enqueue:
                connection.execute(insert(jobs).values(**self._job_values(session_id, enqueue["document_id"],
                    workspace.revision, enqueue["payload"])))
            if job_guard:
                connection.execute(update(jobs).where(jobs.c.id == job_guard[0]).values(
                    status="completed", stage="needs_review", progress=100, updated_at=utcnow(),
                    payload={**job["payload"], "result": job_result}))
        workspace.jobs = self.list_jobs(session_id)
        return workspace

    def extraction_candidates(self, session_id: str) -> list[dict]:
        with self.engine.connect() as connection:
            payloads = connection.execute(select(jobs.c.payload).where(jobs.c.session_id == session_id,
                jobs.c.status == "completed")).scalars()
            return [payload["result"] for payload in payloads if payload.get("result")]

    def _project(self, connection, workspace: Workspace):
        sid = workspace.session_id
        for document in workspace.documents:
            key = and_(document_versions.c.session_id == sid, document_versions.c.id == document.id,
                       document_versions.c.version == document.version)
            exists = connection.execute(select(document_versions.c.id).where(key)).first()
            if exists:
                connection.execute(update(document_versions).where(key).values(payload=document.model_dump(mode="json")))
            else:
                connection.execute(insert(document_versions).values(session_id=sid, id=document.id,
                    version=document.version, sha256=document.sha256, payload=document.model_dump(mode="json")))
        for rule in workspace.rules:
            existing = connection.execute(select(rule_versions.c.id).where(rule_versions.c.session_id == sid,
                rule_versions.c.id == rule.id, rule_versions.c.version == workspace.revision)).first()
            if not existing:
                connection.execute(insert(rule_versions).values(session_id=sid, id=rule.id,
                    version=workspace.revision, payload=rule.model_dump(mode="json")))
        connection.execute(delete(financial_events).where(financial_events.c.session_id == sid))
        if workspace.scenario.events:
            connection.execute(insert(financial_events), [dict(session_id=sid, id=event.id,
                event_date=event.date, amount_cents=event.amount_cents, direction=event.direction,
                kind=event.kind, payload=event.model_dump(mode="json")) for event in workspace.scenario.events])
        if workspace.plan:
            exists = connection.execute(select(scenario_runs.c.id).where(scenario_runs.c.session_id == sid,
                scenario_runs.c.id == workspace.plan.id)).first()
            if not exists:
                connection.execute(insert(scenario_runs).values(session_id=sid, id=workspace.plan.id,
                    revision=workspace.revision, payload=workspace.plan.model_dump(mode="json"), created_at=utcnow()))
                for series in ("baseline", "proposed"):
                    points = getattr(workspace.plan, series).daily
                    if points:
                        connection.execute(insert(daily_balances), [dict(session_id=sid, run_id=workspace.plan.id,
                            series=series, event_date=point.date, balance_cents=point.balance_cents,
                            income_cents=point.income_cents, expense_cents=point.expense_cents,
                            kind="projected") for point in points])

    def set_original(self, session_id: str, document_id: str, key: str, version: int = 1):
        with self.engine.begin() as connection:
            connection.execute(update(document_versions).where(document_versions.c.session_id == session_id,
                document_versions.c.id == document_id, document_versions.c.version == version).values(original_key=key))

    def original_key(self, session_id: str, document_id: str, version: int) -> str | None:
        with self.engine.connect() as connection:
            return connection.execute(select(document_versions.c.original_key).where(
                document_versions.c.session_id == session_id, document_versions.c.id == document_id,
                document_versions.c.version == version)).scalar_one_or_none()

    def document_version(self, session_id: str, document_id: str, version: int) -> dict | None:
        with self.engine.connect() as connection:
            return connection.execute(select(document_versions.c.payload).where(
                document_versions.c.session_id == session_id, document_versions.c.id == document_id,
                document_versions.c.version == version)).scalar_one_or_none()

    def original_keys(self, session_id: str, document_id: str | None = None) -> list[str]:
        statement = select(document_versions.c.original_key).where(document_versions.c.session_id == session_id)
        if document_id:
            statement = statement.where(document_versions.c.id == document_id)
        with self.engine.connect() as connection:
            return [value for value in connection.execute(statement).scalars() if value]

    def purge_document_history(self, session_id: str, document_id: str, rule_ids: list[str]):
        with self.engine.begin() as connection:
            self._purge_document_history(connection, session_id, document_id, rule_ids)

    @staticmethod
    def _purge_document_history(connection, session_id: str, document_id: str, rule_ids: list[str]):
        connection.execute(delete(jobs).where(jobs.c.session_id == session_id, jobs.c.document_id == document_id))
        connection.execute(delete(document_versions).where(document_versions.c.session_id == session_id,
            document_versions.c.id == document_id))
        historical_rules = connection.execute(select(rule_versions.c.id, rule_versions.c.payload).where(
            rule_versions.c.session_id == session_id)).mappings()
        all_rule_ids = set(rule_ids) | {row["id"] for row in historical_rules
            if any(item.get("document_id") == document_id for item in row["payload"].get("evidence", []))}
        if all_rule_ids:
            connection.execute(delete(rule_versions).where(rule_versions.c.session_id == session_id,
                rule_versions.c.id.in_(all_rule_ids)))
        # Old plan narratives can contain extracted wording. Purge them on source deletion.
        connection.execute(delete(scenario_runs).where(scenario_runs.c.session_id == session_id))
        connection.execute(delete(daily_balances).where(daily_balances.c.session_id == session_id))
        connection.execute(delete(verification_points).where(verification_points.c.session_id == session_id))
        connection.execute(delete(verification_runs).where(verification_runs.c.session_id == session_id))

    def delete_session(self, session_id: str, expected_revision: int | None = None,
                       cleanup: Callable[[], None] | None = None):
        with self.engine.begin() as connection:
            revision = connection.execute(select(sessions.c.revision).where(sessions.c.id == session_id)
                .with_for_update()).scalar_one_or_none()
            if revision is None:
                raise MissingSession()
            if expected_revision is not None and revision != expected_revision:
                raise StaleRevision()
            if cleanup:
                cleanup()
            for table in (jobs, verification_points, verification_runs, daily_balances, scenario_runs,
                          financial_events, rule_versions, document_versions):
                connection.execute(delete(table).where(table.c.session_id == session_id))
            connection.execute(delete(sessions).where(sessions.c.id == session_id))

    def enqueue(self, session_id: str, document_id: str, revision: int, payload: dict) -> JobStatus:
        values = self._job_values(session_id, document_id, revision, payload)
        with self.engine.begin() as connection:
            connection.execute(insert(jobs).values(**values))
        return self.public_job(values)

    @staticmethod
    def _job_values(session_id: str, document_id: str, revision: int, payload: dict) -> dict:
        now = utcnow()
        return dict(id=secrets.token_urlsafe(18), session_id=session_id, document_id=document_id,
            base_revision=revision, status="queued", stage="queued", progress=0, error=None,
            payload=payload, attempts=0, created_at=now, updated_at=now)

    @staticmethod
    def public_job(row) -> JobStatus:
        return JobStatus(**{key: row[key] for key in ("id", "status", "stage", "progress",
            "document_id", "error", "updated_at")})

    def get_job(self, session_id: str, job_id: str) -> JobStatus | None:
        with self.engine.connect() as connection:
            row = connection.execute(select(jobs).where(jobs.c.session_id == session_id,
                jobs.c.id == job_id)).mappings().first()
            return self.public_job(row) if row else None

    def list_jobs(self, session_id: str) -> list[JobStatus]:
        with self.engine.connect() as connection:
            rows = connection.execute(select(jobs).where(jobs.c.session_id == session_id)
                .order_by(jobs.c.created_at.desc()).limit(100)).mappings()
            return [self.public_job(row) for row in rows]

    def document_jobs(self, session_id: str, document_id: str, version: int) -> list[JobStatus]:
        with self.engine.connect() as connection:
            rows = connection.execute(select(jobs).where(jobs.c.session_id == session_id,
                jobs.c.document_id == document_id).order_by(jobs.c.created_at.desc())).mappings()
            return [self.public_job(row) for row in rows if row["payload"].get("document_version", 1) == version]

    def claim(self, owner: str) -> dict | None:
        now = utcnow()
        eligible = or_(jobs.c.status == "queued", and_(jobs.c.status == "running", jobs.c.lease_until < now))
        with self.engine.begin() as connection:
            statement = select(jobs).where(eligible, jobs.c.attempts < 3).order_by(jobs.c.created_at).limit(1)
            if self.engine.dialect.name == "postgresql":
                statement = statement.with_for_update(skip_locked=True)
            row = connection.execute(statement).mappings().first()
            if row is None:
                # A crashed final attempt must not remain eternally running.
                connection.execute(update(jobs).where(jobs.c.status == "running", jobs.c.lease_until < now,
                    jobs.c.attempts >= 3).values(status="failed", stage="failed", error="Worker lease expired after 3 attempts",
                    updated_at=now))
                return None
            values = dict(status="running", stage="extracting", lease_owner=owner,
                lease_until=now + timedelta(seconds=self.settings.job_lease_seconds),
                attempts=row["attempts"] + 1, updated_at=now)
            result = connection.execute(update(jobs).where(jobs.c.id == row["id"], eligible).values(**values))
            if result.rowcount != 1:
                return None
            return {**row, **values}

    def progress(self, job_id: str, owner: str, stage: str, progress: int,
                 status: str = "running", error: str | None = None) -> bool:
        with self.engine.begin() as connection:
            result = connection.execute(update(jobs).where(jobs.c.id == job_id,
                jobs.c.lease_owner == owner, jobs.c.status == "running", jobs.c.lease_until > utcnow()).values(
                stage=stage, progress=progress, status=status, error=error, updated_at=utcnow(),
                lease_until=utcnow() + timedelta(seconds=self.settings.job_lease_seconds)))
            return result.rowcount == 1


class Originals:
    """No public URLs. A session-keyed opaque object prefix scopes every access."""
    def __init__(self, settings: Settings):
        self.settings = settings
        self.root = settings.local_storage_path.resolve()
        self.client = None
        if settings.spaces_configured:
            self.client = boto3.client("s3", endpoint_url=settings.spaces_endpoint,
                region_name=settings.spaces_region, aws_access_key_id=settings.spaces_access_key_id,
                aws_secret_access_key=settings.spaces_secret_access_key,
                config=Config(connect_timeout=5, read_timeout=20, retries={"max_attempts": 2}))
        else:
            self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def prefix(session_id: str) -> str:
        return hashlib.sha256(session_id.encode()).hexdigest()

    def key(self, session_id: str, document_id: str, version: int = 1) -> str:
        return f"{self.prefix(session_id)}/{document_id}/v{version}"

    def _path(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if self.root not in path.parents:
            raise ValueError("Invalid object key")
        return path

    def put(self, session_id: str, document_id: str, content: bytes, media_type: str, version: int = 1) -> str:
        # A random suffix prevents concurrent same-name uploads overwriting each other's originals.
        key = self.key(session_id, document_id, version) + "-" + secrets.token_hex(8)
        if self.client:
            self.client.put_object(Bucket=self.settings.spaces_bucket, Key=key, Body=content,
                ContentType=media_type, ACL="private")
        else:
            path = self._path(key)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        return key

    def get(self, key: str) -> bytes:
        if self.client:
            response = self.client.get_object(Bucket=self.settings.spaces_bucket, Key=key)
            with response["Body"] as stream:
                return stream.read(self.settings.max_upload_bytes + 1)
        return self._path(key).read_bytes()

    def delete(self, key: str):
        if self.client:
            self.client.delete_object(Bucket=self.settings.spaces_bucket, Key=key)
        else:
            self._path(key).unlink(missing_ok=True)
