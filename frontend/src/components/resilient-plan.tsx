"use client";

import { useEffect, useRef, useState } from "react";
import { Badge, Button } from "@/components/ui";
import { ApiError, humanize, money, request } from "@/lib/api";
import type { PlanResult, SynthesisAdoptionResult, SynthesisAdoptRequest, SynthesisRequest, SynthesisResult, Uncertainty, VerificationResult, Workspace } from "@/lib/types";

type Props = {
  workspace: Workspace;
  plan: PlanResult;
  dimensions: Uncertainty[];
  verification: VerificationResult | null;
  disabled: boolean;
  onEvidence: (ids: string[]) => void;
  onAdopt: (value: SynthesisAdoptionResult) => void;
  onAdopting: (value: boolean) => void;
  onSessionLost: (sessionId: string) => void;
};

/** Parent keys this panel by source identity and the entire uncertainty draft. */
export default function ResilientPlan({ workspace, plan, dimensions, verification, disabled, onEvidence, onAdopt, onAdopting, onSessionLost }: Props) {
  const [result, setResult] = useState<SynthesisResult | null>(null);
  const [busy, setBusy] = useState<"search" | "adopt" | null>(null);
  const [error, setError] = useState("");
  const controller = useRef<AbortController | null>(null);
  useEffect(() => () => { controller.current?.abort(); onAdopting(false); }, [onAdopting]);
  const unsupported = plan.assumptions?.include_conditional || Object.keys(plan.assumptions?.approval_overrides ?? {}).length > 0;

  function failure(caught: unknown, current: AbortController) {
    if (current.signal.aborted) return;
    setResult(null);
    if (caught instanceof ApiError && caught.status === 401) { onSessionLost(workspace.session_id); return; }
    setError(caught instanceof Error ? caught.message : "The request could not complete. Reload the saved plan before retrying.");
  }

  async function search() {
    if (disabled || unsupported || busy === "adopt") return;
    controller.current?.abort();
    const current = new AbortController();
    controller.current = current;
    setResult(null); setError(""); setBusy("search");
    const body: SynthesisRequest = { plan_id: plan.id, revision: workspace.revision, uncertainties: dimensions,
      max_candidates: 1000, max_case_checks: 10000, time_limit_seconds: 5 };
    try {
      const response = await request<SynthesisResult>("/synthesis", workspace.session_id, { method: "POST", body: JSON.stringify(body),
        signal: AbortSignal.any([current.signal, AbortSignal.timeout(30_000)]) });
      if (!current.signal.aborted) setResult(response);
    } catch (caught) { failure(caught, current); }
    finally { if (controller.current === current) { controller.current = null; setBusy(null); } }
  }

  async function adopt() {
    if (!result?.candidate || !result.candidate_fingerprint || busy || disabled) return;
    const current = new AbortController();
    controller.current = current;
    setError(""); setBusy("adopt"); onAdopting(true);
    const body: SynthesisAdoptRequest = { synthesis_request: result.assumptions, candidate_fingerprint: result.candidate_fingerprint,
      selected_actions: result.candidate.actions.map(({ action_id, execution_date }) => ({ action_id, execution_date })) };
    try {
      const saved = await request<SynthesisAdoptionResult>("/synthesis/adopt", workspace.session_id, { method: "POST", body: JSON.stringify(body),
        signal: AbortSignal.any([current.signal, AbortSignal.timeout(30_000)]) });
      if (!current.signal.aborted) onAdopt(saved);
    } catch (caught) { failure(caught, current); }
    finally { if (controller.current === current) { controller.current = null; setBusy(null); onAdopting(false); } }
  }

  function actions(value: PlanResult) {
    return value.actions.length ? <ul className="synthesis-actions">{value.actions.map(action => <li key={action.action_id}>
      <strong>{workspace.scenario.actions.find(item => item.id === action.action_id)?.title ?? action.action_id}</strong>
      <span>Execute {action.execution_date}</span>
      <button className="text-button" disabled={!action.source_rule_ids.length} onClick={() => onEvidence(action.source_rule_ids)}>Evidence for {action.action_id}</button>
    </li>)}</ul> : <p>No actions selected.</p>;
  }

  const proof = result?.verification;
  const found = result?.status === "FOUND" && result.candidate && proof?.status === "SAFE" && proof.coverage_complete;
  const currentWorst = verification?.coverage_complete && verification.worst_case_proven ? verification.worst_case : null;

  return <section className="resilient" aria-labelledby="resilient-heading" data-testid="resilient-panel">
    <div className="section-title"><h3 id="resilient-heading">Find a resilient schedule</h3><Badge tone="blue">Bounded search</Badge></div>
    <p>Find one permitted fixed schedule that survives the saved nominal case and every combination of the bounds above. Dates, amounts, approvals and cash assumptions stay unchanged.</p>
    <p className="helper">First verified feasible schedule; no optimum or minimum-fee claim. Search uses recorded approvals and retains future debt. Save any edits to nominal scenario controls before searching. No action is executed.</p>
    {unsupported && <p className="inline-error" role="status">Save a plan using recorded approvals before synthesis. Conditional approval assumptions and approval overrides are unsupported.</p>}
    <Button onClick={() => void search()} busy={busy === "search"} disabled={disabled || !!unsupported || busy === "adopt"}>Find verified alternative</Button>
    <p className="helper">Up to 1,000 candidate tuples · 10,000 shared nominal/uncertainty checks · 5 seconds. A cutoff cannot prove that no solution exists.</p>
    {error && <div className="inline-error" role="alert"><p>{error}</p><p>No candidate is available. Reload to see the current saved plan before retrying adoption.</p><Button onClick={() => window.location.reload()}>Reload saved plan</Button></div>}
    {result && <div data-testid="synthesis-result">
      <div className="section-title"><h4>{found ? "Verified alternative found" : result.status === "NO_SOLUTION" ? "No solution in this declared domain" : "Search inconclusive"}</h4>
        <Badge tone={found ? "success" : "warning"}>{humanize(result.termination)}</Badge></div>
      <p role="status">{result.statement}</p>
      <dl className="counts">
        <div><dt>Candidate tuples visited</dt><dd>{result.visited_candidate_tuples} / {result.total_candidate_tuples ?? "Domain count unavailable"}</dd></div>
        <div><dt>Refuted / unresolved tuples</dt><dd>{result.refuted_candidate_tuples} / {result.unresolved_candidate_tuples}</dd></div>
        <div><dt>Actual case checks</dt><dd>{result.nominal_checks} nominal + {result.uncertainty_checks} uncertainty</dd></div>
        <div><dt>Declared cases per schedule</dt><dd>{result.uncertainty_cases_per_candidate}</dd></div>
      </dl>
      {found && result.candidate && proof && <>
        <p className="helper">Preview only. The current saved plan stays active until adoption. The backend rechecks this exact schedule before saving its plan and proof together.</p>
        <div className="cards">
          <article aria-label="Current saved schedule"><h4>Current saved schedule</h4>{actions(plan)}<dl>
            <div><dt>Nominal minimum</dt><dd>{money(plan.proposed.minimum_balance_cents, true)}</dd></div>
            <div><dt>Proven worst minimum for these bounds</dt><dd>{currentWorst ? money(currentWorst.minimum_balance_cents, true) : "Not established"}</dd></div>
            <div><dt>Total action fees</dt><dd>{result.nominal_costs ? money(result.nominal_costs.total_action_fees_cents, true) : "Unavailable"}</dd></div>
            <div><dt>Action burden</dt><dd>{result.nominal_costs?.total_action_burden ?? "Unavailable"}</dd></div>
          </dl></article>
          <article aria-label="Verified candidate schedule"><h4>Verified candidate schedule</h4>{actions(result.candidate)}<dl>
            <div><dt>Nominal minimum</dt><dd>{money(result.candidate.proposed.minimum_balance_cents, true)}</dd></div>
            <div><dt>Proven worst minimum for these bounds</dt><dd>{proof.worst_case_proven && proof.worst_case ? money(proof.worst_case.minimum_balance_cents, true) : "Not established"}</dd></div>
            <div><dt>Total action fees</dt><dd>{result.candidate_costs ? money(result.candidate_costs.total_action_fees_cents, true) : "Unavailable"}</dd></div>
            <div><dt>Action burden</dt><dd>{result.candidate_costs?.total_action_burden ?? "Unavailable"}</dd></div>
          </dl></article>
        </div>
        <p data-testid="candidate-proof"><strong>Independent fixed-plan verification: SAFE</strong> · {proof.checked_cases} / {result.uncertainty_cases_per_candidate} cases, complete coverage. Horizon: {proof.horizon_start} inclusive → {proof.horizon_end_exclusive} exclusive.</p>
        <details><summary>Candidate future obligations and warnings</summary>
          {result.candidate.proposed.beyond_horizon?.length ? <ul>{result.candidate.proposed.beyond_horizon.map(event => <li key={event.id}>{event.title} · {event.date} · {money(event.amount_cents, true)}</li>)}</ul> : <p>No obligations recorded beyond this horizon.</p>}
          <ul>{result.candidate.warnings?.map((warning, index) => <li key={index}>{warning}</li>)}</ul>
        </details>
        <Button variant="primary" onClick={() => void adopt()} busy={busy === "adopt"} disabled={disabled || !!busy}>Adopt verified schedule</Button>
        <p className="helper">Saves a plan and its proof. No payment, cancellation, application or message is executed.</p>
      </>}
      {!found && result.example_refutation && <details><summary>Example refutation of one candidate</summary>
        <p>This example explains one rejected schedule; the search counters determine whether all schedules were refuted.</p>
        <p>{result.example_refutation.selected_actions.map(action => `${action.action_id} on ${action.execution_date}`).join("; ") || "Empty schedule"}</p>
        <ul>{result.example_refutation.failures.map((failure, index) => <li key={index}>{failure.message}{failure.date && ` (${failure.date})`}</li>)}</ul>
      </details>}
      {!!Object.keys(result.excluded_actions ?? {}).length && <details><summary>Actions excluded by recorded constraints</summary><ul>{Object.entries(result.excluded_actions ?? {}).map(([id, reason]) => <li key={id}><strong>{id}:</strong> {reason}</li>)}</ul></details>}
      {!!result.warnings?.length && <ul>{result.warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul>}
    </div>}
    <style jsx>{`
      .resilient { margin-top: 24px; border-top: 1px solid #dce3ef; padding-top: 22px; overflow-wrap: anywhere; }
      .resilient p { margin: 12px 0; line-height: 1.6; }
      .cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin: 16px 0; }
      article { padding: 16px; border: 1px solid #dce3ef; border-radius: 12px; background: #f8faff; min-width: 0; }
      h4 { font-size: 15px; font-weight: 650; margin: 12px 0; }
      ul { padding-left: 20px; margin: 10px 0; } li { margin-bottom: 10px; line-height: 1.5; }
      li strong, li span { display: block; } li span { color: #596980; font-size: 12px; margin: 5px 0; }
      .resilient :global(.synthesis-actions) { padding-left: 18px; margin: 12px 0; }
      .resilient :global(.synthesis-actions li) { margin-bottom: 12px; line-height: 1.6; }
      .resilient :global(.synthesis-actions strong), .resilient :global(.synthesis-actions span) { display: block; }
      .resilient :global(.synthesis-actions span) { color: #596980; font-size: 12px; margin: 5px 0; }
      dl div { padding: 8px 0; border-bottom: 1px solid #e5eaf2; } dt { color: #596980; font-size: 12px; } dd { font-weight: 600; margin-top: 4px; }
      .counts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 16px; margin: 12px 0; }
      details { margin: 14px 0; } summary { cursor: pointer; font-weight: 600; line-height: 1.6; }
      @media (max-width: 640px) { .cards, .counts { grid-template-columns: 1fr; } }
    `}</style>
  </section>;
}
