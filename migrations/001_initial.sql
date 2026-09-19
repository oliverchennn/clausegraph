-- Initial PostgreSQL schema. Matches clausegraph.storage metadata.
CREATE TABLE sessions (
	id VARCHAR(128) NOT NULL, 
	snapshot JSON NOT NULL, 
	revision INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
)

;


CREATE TABLE daily_balances (
	session_id VARCHAR(128) NOT NULL, 
	run_id VARCHAR(128) NOT NULL, 
	series VARCHAR(16) NOT NULL, 
	event_date DATE NOT NULL, 
	balance_cents BIGINT NOT NULL, 
	income_cents BIGINT NOT NULL, 
	expense_cents BIGINT NOT NULL, 
	kind VARCHAR(16) NOT NULL, 
	PRIMARY KEY (session_id, run_id, series, event_date), 
	FOREIGN KEY(session_id) REFERENCES sessions (id) ON DELETE CASCADE
)

;


CREATE TABLE document_versions (
	session_id VARCHAR(128) NOT NULL, 
	id VARCHAR(128) NOT NULL, 
	version INTEGER NOT NULL, 
	sha256 VARCHAR(64) NOT NULL, 
	original_key VARCHAR(512), 
	payload JSON NOT NULL, 
	PRIMARY KEY (session_id, id, version), 
	FOREIGN KEY(session_id) REFERENCES sessions (id) ON DELETE CASCADE
)

;


CREATE TABLE financial_events (
	session_id VARCHAR(128) NOT NULL, 
	id VARCHAR(128) NOT NULL, 
	event_date DATE NOT NULL, 
	amount_cents BIGINT NOT NULL, 
	direction VARCHAR(16) NOT NULL, 
	kind VARCHAR(16) NOT NULL, 
	payload JSON NOT NULL, 
	PRIMARY KEY (session_id, id), 
	FOREIGN KEY(session_id) REFERENCES sessions (id) ON DELETE CASCADE
)

;


CREATE TABLE jobs (
	id VARCHAR(128) NOT NULL, 
	session_id VARCHAR(128) NOT NULL, 
	document_id VARCHAR(128) NOT NULL, 
	base_revision INTEGER NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	stage VARCHAR(128) NOT NULL, 
	progress INTEGER NOT NULL, 
	error VARCHAR(512), 
	payload JSON NOT NULL, 
	lease_owner VARCHAR(128), 
	lease_until TIMESTAMP WITH TIME ZONE, 
	attempts INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(session_id) REFERENCES sessions (id) ON DELETE CASCADE
)

;


CREATE TABLE rule_versions (
	session_id VARCHAR(128) NOT NULL, 
	id VARCHAR(128) NOT NULL, 
	version INTEGER NOT NULL, 
	payload JSON NOT NULL, 
	PRIMARY KEY (session_id, id, version), 
	FOREIGN KEY(session_id) REFERENCES sessions (id) ON DELETE CASCADE
)

;


CREATE TABLE scenario_runs (
	session_id VARCHAR(128) NOT NULL, 
	id VARCHAR(128) NOT NULL, 
	revision INTEGER NOT NULL, 
	payload JSON NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (session_id, id), 
	FOREIGN KEY(session_id) REFERENCES sessions (id) ON DELETE CASCADE
)

;
CREATE INDEX ix_events_timeline ON financial_events (session_id, event_date, kind);
CREATE INDEX ix_jobs_claim ON jobs (status, lease_until, created_at);
