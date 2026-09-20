"use client";

import { useEffect, useRef, useState } from "react";
import { CalendarDays, FileText, ShieldCheck } from "lucide-react";
import { Badge, Button } from "@/components/ui";
import CashGapPanel from "@/components/cash-gap-panel";
import UncertaintyControls, { MAX_CASES, exactCaseCount, duplicateTargets } from "@/components/uncertainty-controls";
import { humanize, money, request } from "@/lib/api";
import type { PlanResult, Uncertainty, VerificationRequest, VerificationResult, Workspace } from "@/lib/types";

type Props = {
  workspace: Workspace;
  plan: PlanResult;
  result: VerificationResult | null;
  onResult: (result: VerificationResult | null) => void;
  onEvidence: (ruleIds: string[]) => void;
};

/**
 * Placeholder for C12's failure view. B ships the seam so the wiring, props and
 * selector are merged and testable; C12 replaces this body only.
 */
function FailureViewSlot({ verification }: { verification: VerificationResult; onEvidence: (ruleIds: string[]) => void }) {
  if (!verification.counterexample) return null;
  return <p className="helper" data-testid="failure-view-placeholder">
    A failing case was found. The detailed failure view is a separate task.
  </p>;
}

export default function VerifyPlan({ workspace, plan, result, onResult, onEvidence }: Props) {
  const incomes = workspace.scenario.events.filter(event => event.direction === "income" && event.kind !== "actual");
  const [dimensions, setDimensions] = useState<Uncertainty[]>(() => result?.assumptions.uncertainties ?? []);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const controller = useRef<AbortController | null>(null);
  useEffect(() => () => controller.current?.abort(), []);

  function clearResult() {
    controller.current?.abort();
    controller.current = null;
    setBusy(false);
    setError("");
    onResult(null);
  }

  async function verify() {
    clearResult();
    const current = new AbortController();
    controller.current = current;
    setBusy(true);
    const uncertainties: NonNullable<VerificationRequest["uncertainties"]> = dimensions;
    const body: VerificationRequest = { plan_id: plan.id, revision: workspace.revision, uncertainties, max_cases: MAX_CASES, time_limit_seconds: 5 };
    try {
      const checked = await request<VerificationResult>("/verify", workspace.session_id, { method: "POST", body: JSON.stringify(body), signal: current.signal });
      if (!current.signal.aborted) onResult(checked);
    } catch (caught) {
      if (!current.signal.aborted) setError(caught instanceof Error ? caught.message : "Verification could not complete. No safety result is available.");
    } finally {
      if (controller.current === current) { controller.current = null; setBusy(false); }
    }
  }

  function preset(end: string) {
    clearResult();
    const income = incomes.find(item => item.date === "2026-09-21") ?? incomes[0];
    if (!income) return;
    setDimensions([{ id: "payday", kind: "income_date", basis: "user_assumption", event_id: income.id,
      earliest: "2026-09-21", latest: end,
      rationale: "Synthetic example bound: the projected paycheck may arrive on any date in this inclusive range." }]);
  }

  function changeDimensions(next: Uncertainty[]) {
    clearResult();
    setDimensions(next);
  }

  const duplicates = duplicateTargets(dimensions);
  const caseCount = exactCaseCount(dimensions);
  const blocked = duplicates.size > 0 || dimensions.some(item => !item.rationale.trim())
    || dimensions.some(item => item.kind === "income_date" && item.latest < item.earliest)
    || dimensions.some(item => item.kind === "income_amount" && item.maximum_cents < item.minimum_cents)
    || caseCount === BigInt(0);

  const counterexample = result?.counterexample;
  const actionTitle = (id: string) => workspace.scenario.actions.find(action => action.id === id)?.title ?? id;
  const eventTitle = (id: string) => workspace.scenario.events.find(event => event.id === id)?.title ?? id;
  const dimensionTitle = (id: string) => {
    const dimension = result?.assumptions.uncertainties?.find(item => item.id === id);
    return dimension ? dimension.kind === "approval" ? `${actionTitle(dimension.target_id)} approval` : `${eventTitle(dimension.event_id)} ${dimension.kind === "income_date" ? "date" : "amount"}` : id;
  };

  return <section className="panel verification-panel" aria-labelledby="verify-heading" data-testid="verification-panel">
    <div className="section-title"><h2 id="verify-heading"><ShieldCheck size={18} /> Verify plan</h2><Badge tone="blue">Fixed schedule</Badge></div>
    <p className="helper">Does this saved plan remain safe for every combination of the bounds you declare? Its actions and execution dates stay fixed.</p>
    <form onSubmit={event => { event.preventDefault(); void verify(); }}>
      <fieldset disabled={busy} className="verification-fields">
        <UncertaintyControls workspace={workspace} dimensions={dimensions} onChange={changeDimensions} disabled={busy} />
        {workspace.mode === "synthetic" && incomes.some(income => income.date === "2026-09-21") &&
          <div className="verification-presets"><span>Synthetic example bounds:</span>
            <Button type="button" variant="ghost" onClick={() => preset("2026-09-28")}>Payday through Sep 28</Button>
            <Button type="button" variant="ghost" onClick={() => preset("2026-09-26")}>Payday through Sep 26</Button></div>}
        {incomes.length === 0 && <p className="helper">No projected income event is available to vary. Recorded income stays fixed.</p>}
      </fieldset>
      <div className="verification-submit"><Button type="submit" variant="primary" busy={busy} disabled={blocked}><ShieldCheck size={15} /> Verify fixed plan</Button><span>Up to {MAX_CASES.toLocaleString("en-US")} cases · 5-second budget</span></div>
    </form>
    <details className="verification-schedule"><summary>Saved actions and dates held fixed ({plan.actions.length})</summary>{plan.actions.length ? plan.actions.map(action => <div className="verification-action" key={action.action_id}><div><strong>{actionTitle(action.action_id)}</strong><span><CalendarDays size={12} /> {action.execution_date}</span></div><button className="text-button" disabled={!action.source_rule_ids.length} onClick={() => onEvidence(action.source_rule_ids)}><FileText size={12} /> Action evidence</button></div>) : <p>The saved plan selects no actions.</p>}</details>
    {error && <div className="inline-error" role="alert">{error}</div>}
    {result && <div className={`verification-result verification-${result.status.toLowerCase()}`} data-testid="verification-result" role="status">
      <div className="section-title"><h3>Fixed-plan result</h3><Badge tone={result.status === "SAFE" ? "success" : result.status === "UNSAFE" ? "danger" : "warning"}>{result.status === "SAFE" ? "Verified Safe" : result.status === "UNSAFE" ? "Unsafe" : "Unknown"}</Badge></div>
      <p className="verification-statement">{result.statement}</p>
      <p className="helper">Applies only to the declared bounds, recorded evidence, and horizon below. Other dates, outcomes, and uncertainties are outside this result.</p>
      <p className="helper verification-properties">Checks: nonnegative daily cash, preserved essentials, action authorization and evidence, execution windows and dependencies, and obligation accounting.</p>
      <div className="verification-metrics"><div><span>Nominal minimum</span><strong>{money(plan.proposed.minimum_balance_cents)}</strong></div><div><span>Worst-case minimum</span><strong data-testid="verification-worst-balance">{result.worst_case_proven && result.coverage_complete && result.worst_case ? money(result.worst_case.minimum_balance_cents) : "Not proven"}</strong></div></div>
      <dl className="verification-facts"><div><dt>Cases checked</dt><dd>{result.checked_cases} / {result.total_cases} · {result.dimension_count} uncertainty {result.dimension_count === 1 ? "dimension" : "dimensions"}</dd></div><div><dt>Full coverage</dt><dd>{result.coverage_complete ? "Yes · every modeled combination" : "No · bounded check incomplete"}</dd></div><div><dt>Horizon</dt><dd>{result.horizon_start} inclusive → {result.horizon_end_exclusive} exclusive</dd></div><div><dt>Solver</dt><dd>Exhaustive finite model checker · {result.solver_status} · {result.runtime_seconds.toFixed(3)}s</dd></div><div><dt>Input revision</dt><dd>{result.revision}</dd></div></dl>
      <details className="verification-assumptions" open><summary>Exact declared assumptions</summary><ul>{result.assumptions.uncertainties?.map(dimension => <li key={dimension.id}><strong>{dimension.kind === "approval" ? `${actionTitle(dimension.target_id)}: ${dimension.outcomes.join(" / ")}` : dimension.kind === "income_date" ? `${eventTitle(dimension.event_id)}: every date ${dimension.earliest} through ${dimension.latest}, inclusive` : `${eventTitle(dimension.event_id)}: every cent ${money(dimension.minimum_cents, true)} through ${money(dimension.maximum_cents, true)}, inclusive`}</strong><span>User assumption · {dimension.rationale}</span></li>)}</ul>{!result.assumptions.uncertainties?.length && <p>No uncertain dimensions declared; this checks one concrete case.</p>}<p>Everything outside these dimensions uses the saved nominal scenario. Opening cash: {money(result.nominal_assumptions.opening_balance_cents ?? workspace.scenario.opening_balance_cents)}.</p>{result.nominal_assumptions.income_date && <p>Nominal income date: {result.nominal_assumptions.income_date}.</p>}{result.nominal_assumptions.income_cents != null && <p>Nominal income amount: {money(result.nominal_assumptions.income_cents)}.</p>}{Object.entries(result.nominal_assumptions.approval_overrides ?? {}).map(([id, value]) => <p key={id}>Nominal approval assumption: {workspace.rules.find(rule => rule.id === id)?.title ?? actionTitle(id)} · {value}.</p>)}{result.nominal_assumptions.include_conditional && <p>Nominal scenario permits conditional approval assumptions; verification checks authorization separately in every case.</p>}</details>
      {/* RELEASED TO C12 — c-uncertainty-failure-view.
          B owns this seam and the props passed through it. C12 may replace the
          placeholder below with its failure view and may not change surrounding
          form, request or state handling. Typed props: { verification: VerificationResult;
          onEvidence: (ruleIds: string[]) => void }. Stable selector: data-testid="failure-view-slot". */}
      <div data-testid="failure-view-slot" className="failure-view-slot">
        <FailureViewSlot verification={result} onEvidence={onEvidence} />
      </div>
      {result.status !== "SAFE" && <CashGapPanel workspace={workspace} plan={plan} verification={result} onEvidence={onEvidence} />}
      {counterexample && <section className="counterexample" aria-labelledby="counterexample-heading">
        <h3 id="counterexample-heading">Counterexample timeline</h3>
        <ul className="counterexample-assignment">{counterexample.assignment.map(item => <li key={item.dimension_id}><strong>{dimensionTitle(item.dimension_id)}:</strong> {String(item.value)}</li>)}</ul>
        <p className="counterexample-failure"><strong>{result.coverage_complete ? "Earliest failing date" : "Failing date in this case"}: {counterexample.earliest_failing_date ?? "Schedule authorization failed"}</strong>{counterexample.balance_cents != null && <span>Balance: {money(counterexample.balance_cents)}</span>}</p>
        {counterexample.failures.map((failure, index) => <div className="counterexample-reason" key={index}><Badge tone="danger">{humanize(failure.property)}</Badge><p>{failure.message}</p>{(failure.source_rule_ids?.length ?? 0) > 0 && <button className="text-button" onClick={() => onEvidence(failure.source_rule_ids ?? [])}><FileText size={12} /> Failure evidence</button>}</div>)}
        {counterexample.simulation ? <p className="helper">This concrete case appears in red on the cash chart above.</p> : <p className="helper">An invalid schedule has no permitted cash projection; no counterexample line is drawn.</p>}
        <ol className="counterexample-events">{counterexample.events?.map(({ event, action_ids }) => <li key={event.id}><div className="counterexample-event-main"><time>{event.date}</time><strong>{event.title}</strong><span>{event.direction === "income" ? "+" : "−"}{money(event.amount_cents)}</span></div><div className="counterexample-event-detail">{event.essential && <Badge>Essential retained</Badge>}{event.source_rule_ids?.length ? <button className="text-button" onClick={() => onEvidence(event.source_rule_ids ?? [])}><FileText size={12} /> Event evidence</button> : <span>Recorded financial picture</span>}{action_ids?.map(id => { const action = plan.actions.find(item => item.action_id === id); return <button className="text-button" key={id} disabled={!action?.source_rule_ids.length} onClick={() => onEvidence(action?.source_rule_ids ?? [])}>{actionTitle(id)} · action evidence</button>; })}</div></li>)}</ol>
      </section>}
      {!!result.warnings?.length && <ul className="verification-warnings">{result.warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul>}
    </div>}
  </section>;
}
