-- Bounded verification histories use the existing private PostgreSQL database.
-- Plain PostgreSQL works on Tiger Data without requiring a Timescale extension.
CREATE TABLE verification_runs (
    session_id VARCHAR(128) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    id VARCHAR(128) NOT NULL,
    plan_id VARCHAR(128) NOT NULL,
    revision INTEGER NOT NULL,
    status VARCHAR(16) NOT NULL,
    payload JSON NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (session_id, id)
);

CREATE TABLE verification_points (
    session_id VARCHAR(128) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    run_id VARCHAR(128) NOT NULL,
    series VARCHAR(16) NOT NULL,
    event_date DATE NOT NULL,
    balance_cents BIGINT NOT NULL,
    income_cents BIGINT NOT NULL,
    expense_cents BIGINT NOT NULL,
    kind VARCHAR(16) NOT NULL,
    PRIMARY KEY (session_id, run_id, series, event_date)
);
