"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { History, LoaderCircle, RefreshCw } from "lucide-react";
import { Badge, Button } from "./ui";
import { ApiError, humanize, money, request } from "@/lib/api";
import type { FinancialEvent, PlanRequest, PlanResult, Simulation, VerificationResult, Workspace } from "@/lib/types";

const CashChart = dynamic(() => import("./cash-chart"), { ssr: false });
type Snapshot = { workspace: Workspace; plans: PlanResult[]; verifications: VerificationResult[] };
type Selection = { kind: "plan" | "verification"; id: string } | null;
type Props = { workspace: Workspace; onSessionLost: (sessionId: string) => void };

function Warnings({ warnings }: { warnings?: string[] }) {
  return warnings?.length ? <ul className="history-warnings">{warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul> : <p>No saved warnings.</p>;
}

function NominalAssumptions({ value }: { value?: PlanRequest }) {
  if (!value) return <p>Nominal assumptions were not included in this saved record.</p>;
  return <div className="history-assumptions">
    <p>Overrides are hypothetical. Unspecified values use the inputs saved with this run; today’s financial picture is not substituted.</p>
    <dl className="history-facts">
      <div><dt>Opening cash override</dt><dd>{value.opening_balance_cents != null ? `${money(value.opening_balance_cents, true)} · hypothetical, not evidence of funding` : "No override saved"}</dd></div>
      <div><dt>Income amount override</dt><dd>{value.income_cents != null ? money(value.income_cents, true) : "No override saved"}</dd></div>
      <div><dt>Income date override</dt><dd>{value.income_date ?? "No override saved"}</dd></div>
      <div><dt>Horizon override</dt><dd>{value.horizon_days != null ? `${value.horizon_days} days` : "No override saved"}</dd></div>
      <div><dt>Conditional assumptions permitted</dt><dd>{value.include_conditional ? "Yes · not recorded approval" : "No"}</dd></div>
      <div><dt>Forced actions</dt><dd>{value.force_action_ids?.join(", ") || "None"}</dd></div>
      <div><dt>Excluded actions</dt><dd>{value.exclude_action_ids?.join(", ") || "None"}</dd></div>
      {Object.entries(value.approval_overrides ?? {}).map(([id, status]) => <div key={`approval-${id}`}><dt>Approval assumption · {id}</dt><dd>{humanize(status)} · hypothetical</dd></div>)}
      {Object.entries(value.action_dates ?? {}).map(([id, date]) => <div key={`date-${id}`}><dt>Action date override · {id}</dt><dd>{date}</dd></div>)}
    </dl>
  </div>;
}

function SavedEvent({ event }: { event: FinancialEvent }) {
  return <div className="history-event"><strong>{event.title}</strong><span>{event.date} · {event.direction} · {money(event.amount_cents, true)}{event.essential ? " · Essential retained" : ""}</span><small>Event {event.id} · historical rule IDs: {event.source_rule_ids?.join(", ") || "None"}</small></div>;
}

function SavedSimulation({ value, label }: { value: Simulation; label: string }) {
  return <section className="history-simulation" aria-label={label}>
    <h4>{label}</h4>
    <dl className="history-facts">
      <div><dt>Minimum / ending balance</dt><dd>{money(value.minimum_balance_cents, true)} / {money(value.ending_balance_cents, true)}</dd></div>
      <div><dt>First shortfall</dt><dd>{value.first_shortfall_date ?? "None in saved horizon"}</dd></div>
      <div><dt>Additional cash diagnostic</dt><dd>{money(value.additional_cash_required_cents, true)} · not funding</dd></div>
    </dl>
    <details><summary>Saved daily balances ({value.daily.length})</summary><div className="history-table-wrap"><table><caption>{label} · persisted cash series</caption><thead><tr><th>Date</th><th>Closing balance (USD)</th></tr></thead><tbody>{value.daily.map(day => <tr key={day.date}><td>{day.date}</td><td>{money(day.balance_cents, true)}</td></tr>)}</tbody></table></div></details>
    <details><summary>Beyond-horizon obligations ({value.beyond_horizon?.length ?? 0})</summary>{value.beyond_horizon?.length ? value.beyond_horizon.map(event => <SavedEvent key={event.id} event={event} />) : <p>None recorded beyond this horizon.</p>}</details>
  </section>;
}

function SavedActions({ actions }: { actions: PlanResult["actions"] }) {
  return actions.length ? <ul className="history-actions">{actions.map(action => <li key={action.action_id}><strong>{action.action_id} · {action.execution_date}</strong><p>{action.explanation}</p><p>{action.conditional ? "Conditional assumption" : "Saved as nonconditional"} · historical rule IDs: {action.source_rule_ids.join(", ") || "None"}</p></li>)}</ul> : <p>No actions selected in this saved schedule.</p>;
}

function SavedPlan({ plan }: { plan: PlanResult }) {
  return <>
    <dl className="history-facts"><div><dt>Saved state</dt><dd>{humanize(plan.state)} · not current permission or funding</dd></div><div><dt>Plan generation</dt><dd>{plan.generation_mode === "resilient" ? "Verified fixed schedule · no optimization claim" : `${plan.solver_status} · ${plan.solver_wall_time_seconds.toFixed(3)}s`}</dd></div><div><dt>Nominal objective proven</dt><dd>{plan.generation_mode === "resilient" ? "Not a synthesis objective" : plan.objective_proven ? "Yes" : "No"} · separate from fixed-plan safety verification</dd></div></dl>
    {plan.synthesis_provenance && <details><summary>Saved synthesis provenance</summary><p>Source plan: {plan.synthesis_provenance.source_plan_id}</p><p>Fixed schedule constructed under recorded permissions and independently verified. The saved verification has its original bounds and horizon.</p><p>Declared uncertainty IDs: {plan.synthesis_provenance.request.uncertainties?.map(item => item.id).join(", ") || "None; one concrete case"}</p></details>}
    <h3>Saved nominal assumptions</h3><NominalAssumptions value={plan.assumptions} />
    <h3>Saved cash projection</h3><p>Baseline and proposed series from this record. Deferrals change timing, not savings.</p><CashChart plan={plan} />
    <div className="history-columns"><SavedSimulation value={plan.baseline} label="Saved baseline" /><SavedSimulation value={plan.proposed} label="Saved proposed plan" /></div>
    <h3>Saved actions</h3><SavedActions actions={plan.actions} />
    <h3>Saved decision traces</h3>
    {plan.decision_traces?.length ? plan.decision_traces.map(trace => <details key={`${trace.action_id}:${trace.execution_date}`}><summary>{trace.action_id} · {trace.execution_date}</summary><p>Historical document IDs: {trace.source_document_ids.join(", ") || "None"}</p><p>Historical rule IDs: {trace.source_rule_ids.join(", ") || "None"}</p>{trace.changes?.map((change, index) => <div className="history-change" key={index}><strong>{humanize(change.operation)}</strong>{change.before && <><p>Before</p><SavedEvent event={change.before} /></>}{change.after && <><p>After</p><SavedEvent event={change.after} /></>}</div>)}</details>) : <p>No decision traces saved.</p>}
    {!!Object.keys(plan.excluded_actions ?? {}).length && <details><summary>Saved excluded actions</summary>{Object.entries(plan.excluded_actions ?? {}).map(([id, reason]) => <p key={id}><strong>{id}:</strong> {reason}</p>)}</details>}
    <h3>Saved warnings</h3><Warnings warnings={plan.warnings} />
  </>;
}

function SavedVerification({ result, plans }: { result: VerificationResult; plans: PlanResult[] }) {
  const witness = result.counterexample;
  return <>
    <Badge tone={result.status === "SAFE" ? "success" : result.status === "UNSAFE" ? "danger" : "warning"}>{result.status}</Badge>
    <p>{result.statement}</p><p>This historical result applies only to its fixed schedule, declared finite bounds and saved horizon. UNKNOWN is not success; SAFE is not a guarantee about today’s facts or other uncertainties.</p>
    <dl className="history-facts">
      <div><dt>Saved plan ID</dt><dd>{result.plan_id}</dd></div>
      <div><dt>Horizon</dt><dd>{result.horizon_start} inclusive → {result.horizon_end_exclusive} exclusive</dd></div>
      <div><dt>Cases checked</dt><dd>{result.checked_cases} / {Number.isSafeInteger(result.total_cases) ? result.total_cases : "Total exceeds exact browser integer precision"} · {result.dimension_count} dimensions</dd></div>
      <div><dt>Full coverage</dt><dd>{result.coverage_complete ? "Yes · every modeled combination" : "No · incomplete check"}</dd></div>
      <div><dt>Solver termination</dt><dd>{humanize(result.solver)} · {result.solver_status} · {result.runtime_seconds.toFixed(3)}s</dd></div>
      <div><dt>Worst-case minimum proven</dt><dd>{result.worst_case_proven && result.coverage_complete && result.worst_case ? money(result.worst_case.minimum_balance_cents, true) : "Not proven"}</dd></div>
    </dl>
    {!plans.some(plan => plan.id === result.plan_id) && <p className="history-caution">The associated plan is outside the returned plan list. This verification retains its own assumptions, fixed actions and proof records.</p>}
    <h3>Saved nominal assumptions</h3><NominalAssumptions value={result.nominal_assumptions} />
    <h3>Declared uncertainty assumptions</h3>
    {result.assumptions.uncertainties?.length ? <ul className="history-actions">{result.assumptions.uncertainties.map(dimension => <li key={dimension.id}><strong>{dimension.id} · {humanize(dimension.kind)}</strong><p>{dimension.kind === "approval" ? `${dimension.target_id}: ${dimension.outcomes.join(" / ")}` : dimension.kind === "income_date" ? `${dimension.event_id}: every date ${dimension.earliest} through ${dimension.latest}, inclusive` : `${dimension.event_id}: every cent ${money(dimension.minimum_cents, true)} through ${money(dimension.maximum_cents, true)}, inclusive`}</p><p>User assumption · {dimension.rationale}</p></li>)}</ul> : <p>No uncertainty dimensions; one concrete case.</p>}
    <p>Saved budgets: {result.assumptions.max_cases ?? 10000} cases · {result.assumptions.time_limit_seconds ?? 5} seconds (cooperative).</p>
    <h3>Actions and dates held fixed</h3><SavedActions actions={result.fixed_actions} />
    {witness && <section className="history-witness"><h3>Saved counterexample</h3><ul>{witness.assignment.map(item => <li key={item.dimension_id}>{item.dimension_id}: {String(item.value)}</li>)}</ul><p><strong>{result.coverage_complete ? "Earliest failing date in the declared model" : "Failing date in this case"}: {witness.earliest_failing_date ?? "Schedule authorization failed"}</strong></p><p>{witness.balance_cents != null ? `Saved failing balance: ${money(witness.balance_cents, true)}` : "No permitted cash balance for this invalid schedule."}</p>{witness.failures.map((failure, index) => <div key={index}><strong>{humanize(failure.property)}</strong><p>{failure.message}</p><p>Historical rule IDs: {failure.source_rule_ids?.join(", ") || "None"}</p></div>)}{witness.simulation ? <SavedSimulation value={witness.simulation} label="Saved counterexample cash" /> : <p>No permitted cash projection was saved.</p>}<details><summary>Saved counterexample timeline</summary>{witness.events?.map(({ event, action_ids }) => <div key={event.id}><SavedEvent event={event} /><p>Historical action IDs: {action_ids?.join(", ") || "None"}</p></div>)}</details></section>}
    {result.worst_case && <details><summary>{result.worst_case_proven && result.coverage_complete ? "Proven worst-case cash and assignment" : "Lowest observed cash and assignment · not a proven worst case"}</summary><ul>{result.worst_case_assignment?.map(item => <li key={item.dimension_id}>{item.dimension_id}: {String(item.value)}</li>)}</ul><SavedSimulation value={result.worst_case} label="Saved lowest cash" /></details>}
    <h3>Saved warnings</h3><Warnings warnings={result.warnings} />
  </>;
}

export default function SavedHistory({ workspace, onSessionLost }: Props) {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);
  const [selected, setSelected] = useState<Selection>(null);
  const { session_id: sessionId, revision } = workspace;
  const activePlanId = workspace.plan?.id;

  useEffect(() => {
    const controller = new AbortController();
    const signal = AbortSignal.any([controller.signal, AbortSignal.timeout(30_000)]);
    setSnapshot(null); setSelected(null); setError("");
    async function load() {
      try {
        const before = await request<Workspace>("/workspace", sessionId, { signal });
        const [plans, verifications] = await Promise.all([
          request<PlanResult[]>("/history", sessionId, { signal }),
          request<VerificationResult[]>("/verifications", sessionId, { signal }),
        ]);
        const after = await request<Workspace>("/workspace", sessionId, { signal });
        if (controller.signal.aborted) return;
        if (before.revision !== after.revision || before.plan?.id !== after.plan?.id) throw new Error("The workspace changed during this read. Refresh history to load a consistent view.");
        setSnapshot({ workspace: after, plans, verifications });
      } catch (caught) {
        if (controller.signal.aborted) return;
        if (caught instanceof ApiError && caught.status === 401) { onSessionLost(sessionId); return; }
        setError(caught instanceof Error ? caught.message : "Saved results could not be loaded.");
      }
    }
    void load();
    return () => controller.abort();
  }, [sessionId, revision, activePlanId, retry, onSessionLost]);

  const plan = selected?.kind === "plan" ? snapshot?.plans.find(item => item.id === selected.id) : undefined;
  const verification = selected?.kind === "verification" ? snapshot?.verifications.find(item => item.id === selected.id) : undefined;
  function label(planId: string, savedRevision: number) {
    if (!snapshot) return "Historical record";
    if (snapshot.workspace.plan?.id === planId && snapshot.workspace.revision === savedRevision) return "Active plan when refreshed";
    return savedRevision === snapshot.workspace.revision ? "Inactive plan · same input revision" : "Historical input revision";
  }
  function select(kind: "plan" | "verification", id: string) {
    setSelected(current => current?.kind === kind && current.id === id ? null : { kind, id });
  }

  return <section className="panel saved-history" aria-labelledby="history-heading" data-testid="saved-history">
    <div className="section-title"><h2 id="history-heading"><History size={18} /> Saved history</h2><Button onClick={() => { setSnapshot(null); setSelected(null); setRetry(value => value + 1); }}><RefreshCw size={14} /> Refresh history</Button></div>
    <p>Read-only records of previous calculations. Browsing does not restore a plan, run a calculation, or authorize an action.</p>
    <p>Each list contains up to the latest 30 available records in server order. Older records remain stored until deletion or reset; they cannot be loaded here. The two lists have independent limits.</p>
    <p className="history-caution">Historical references may differ from today’s documents, evidence and approvals. Only saved IDs and content appear below; current source text is not proof of an older result.</p>
    {error ? <div role="alert"><p>History could not be loaded. {error}</p><Button onClick={() => setRetry(value => value + 1)}>Try history again</Button></div> : !snapshot ? <p role="status"><LoaderCircle className="spin" size={16} /> Loading saved history…</p> : <>
      <p>Workspace input revision when refreshed: <strong>{snapshot.workspace.revision}</strong>. {snapshot.workspace.mode === "synthetic" ? "Synthetic demo records · fictional financial details." : "Private session records."}</p>
      <div className="history-columns">
        <section aria-labelledby="history-plans-heading"><h3 id="history-plans-heading">Saved plans ({snapshot.plans.length})</h3><div className="history-list">{snapshot.plans.length ? snapshot.plans.map(item => <button key={item.id} className="history-record" data-testid={`history-plan-${item.id}`} aria-expanded={selected?.kind === "plan" && selected.id === item.id} aria-controls="history-detail" onClick={() => select("plan", item.id)}><strong>Plan · revision {item.revision}</strong><span>{humanize(item.state)} · {label(item.id, item.revision)}</span><time>{item.generated_at}</time><small>{item.id}</small></button>) : <p>No saved plans in this session.</p>}</div></section>
        <section aria-labelledby="history-verifications-heading"><h3 id="history-verifications-heading">Saved verifications ({snapshot.verifications.length})</h3><div className="history-list">{snapshot.verifications.length ? snapshot.verifications.map(item => <button key={item.id} className="history-record" data-testid={`history-verification-${item.id}`} aria-expanded={selected?.kind === "verification" && selected.id === item.id} aria-controls="history-detail" onClick={() => select("verification", item.id)}><strong>{item.status} · revision {item.revision}</strong><span>{label(item.plan_id, item.revision)}</span><time>{item.generated_at}</time><small>{item.id} · plan {item.plan_id}</small></button>) : <p>No saved verifications in this session.</p>}</div></section>
      </div>
      <div id="history-detail" className="history-detail" role="region" aria-label="Saved record details" aria-live="polite">
        {plan || verification ? <><h2>{plan ? "Saved plan details" : "Saved verification details"}</h2><p>Record {plan?.id ?? verification?.id} · saved revision {plan?.revision ?? verification?.revision}</p><p>Generated {plan?.generated_at ?? verification?.generated_at}</p>{plan ? <SavedPlan plan={plan} /> : verification && <SavedVerification result={verification} plans={snapshot.plans} />}</> : <p>Select a saved record to inspect its assumptions and results.</p>}
      </div>
    </>}
  </section>;
}
