-- Keep booked transactions separate from expected/scenario projections.
CREATE VIEW financial_event_daily_totals AS
SELECT session_id, event_date, kind,
       SUM(CASE WHEN direction = 'income' THEN amount_cents ELSE 0 END) AS income_cents,
       SUM(CASE WHEN direction = 'expense' THEN amount_cents ELSE 0 END) AS expense_cents
FROM financial_events
GROUP BY session_id, event_date, kind;

CREATE INDEX ix_balances_timeline ON daily_balances (session_id, event_date, series);
