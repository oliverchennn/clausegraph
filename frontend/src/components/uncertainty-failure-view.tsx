"use client";

import { Badge, Button } from "@/components/ui";
import { humanize, money } from "@/lib/api";
import { exactCaseCount } from "@/lib/uncertainty";
import type { VerificationResult } from "@/lib/types";

type Props = { verification: VerificationResult; onEvidence: (ruleIds: string[]) => void };

export default function UncertaintyFailureView({ verification: result, onEvidence }: Props) {
  const total = exactCaseCount(result.assumptions.uncertainties ?? []);
  const unchecked = total > BigInt(result.checked_cases) ? total - BigInt(result.checked_cases) : BigInt(0);
  const witness = result.counterexample;
  const failures = witness?.failures ?? [];
  const assignmentLabel = (id: string) => {
    const dimension = result.assumptions.uncertainties?.find(item => item.id === id);
    if (!dimension) return id;
    return `${humanize(dimension.kind)} · ${dimension.kind === "approval" ? dimension.target_id : dimension.event_id}`;
  };
  const assignmentValue = (id: string, value: string | number) => result.assumptions.uncertainties?.find(item => item.id === id)?.kind === "income_amount"
    && typeof value === "number" ? money(value, true) : String(value);
  const evidence = (ids: string[], index: number) => ids.length
    ? <Button variant="ghost" onClick={() => onEvidence(ids)}>Evidence for failure {index + 1}</Button>
    : <span>No source reference returned</span>;

  return <section className="failure-view" aria-labelledby="failure-details-heading" data-testid="uncertainty-failure-view">
    <div className="section-title"><h3 id="failure-details-heading">Explore this verification</h3><Badge tone={result.status === "SAFE" ? "success" : result.status === "UNSAFE" ? "danger" : "warning"}>{humanize(result.status)}</Badge></div>
    <dl className="coverage" aria-label="Evaluated and unchecked cases">
      <div><dt>Evaluated cases</dt><dd>{result.checked_cases} of {total.toString()}</dd></div>
      <div><dt>Unchecked cases</dt><dd data-testid="unchecked-cases">{unchecked.toString()}</dd></div>
    </dl>
    <p className="helper">These are combinations, not probabilities. The checker does not return a list of every evaluated case.</p>
    {!result.coverage_complete && <p className="notice">Unvisited assignments remain unchecked. {witness ? "This witness proves a failure, but other failures may exist and may occur earlier." : "No conclusive failure was found in the evaluated prefix; safety remains unknown."}</p>}
    {result.status === "UNKNOWN" && result.coverage_complete && <p className="notice">Every assignment was visited, but required facts remain unresolved. Complete coverage does not establish safety.</p>}
    {result.status === "SAFE" && <p>All declared cases passed for this fixed schedule and displayed horizon. Outcomes outside these bounds are not covered.</p>}

    {witness && <details open data-testid="witness-details">
      <summary>One concrete failure witness</summary>
      <p>This is one returned assignment, not all failing combinations.</p>
      <dl className="assignments">{witness.assignment.map(item => <div key={item.dimension_id}><dt>{assignmentLabel(item.dimension_id)}</dt><dd>{assignmentValue(item.dimension_id, item.value)}</dd></div>)}</dl>
      <p>Failure date in this witness: <strong>{witness.earliest_failing_date ?? "No cash date available"}</strong>.</p>
      {witness.simulation ? <p>Balance at the witness failure: <strong>{witness.balance_cents == null ? "Not supplied" : money(witness.balance_cents, true)}</strong>. This is separate from the worst cash result below.</p>
        : <p className="notice" data-testid="witness-no-cash">No permitted cash simulation exists for this witness. Resolve its authorization, evidence or structural failures; a cash balance is not substituted.</p>}
      <div className="desktop-failures"><table aria-label="Properties violated by this witness"><thead><tr><th scope="col">Property</th><th scope="col">Reason and date</th><th scope="col">Source</th></tr></thead><tbody>{failures.map((failure, index) => <tr key={index}><th scope="row">{humanize(failure.property)}</th><td>{failure.message}{failure.date && <small>{failure.date}</small>}{failure.action_id && <small>Action: {failure.action_id}</small>}</td><td>{evidence(failure.source_rule_ids ?? [], index)}</td></tr>)}</tbody></table></div>
      <ol className="mobile-failures" aria-label="Properties violated by this witness">{failures.map((failure, index) => <li key={index}><strong>{humanize(failure.property)}</strong><p>{failure.message}</p>{failure.date && <p>{failure.date}</p>}{failure.action_id && <p>Action: {failure.action_id}</p>}{evidence(failure.source_rule_ids ?? [], index)}</li>)}</ol>
    </details>}

    <details data-testid="worst-permitted-cash">
      <summary>{result.worst_case_proven ? "Proven worst cash within these bounds" : "Observed permitted cash only · worst case not proven"}</summary>
      {result.worst_case ? <><p>Minimum: <strong>{money(result.worst_case.minimum_balance_cents, true)}</strong>. {result.worst_case_proven ? "Complete resolved coverage supports this cash bound." : "This value covers only evaluated assignments with a permitted simulation."}</p>
        <dl className="assignments">{result.worst_case_assignment?.map(item => <div key={item.dimension_id}><dt>{assignmentLabel(item.dimension_id)}</dt><dd>{assignmentValue(item.dimension_id, item.value)}</dd></div>)}</dl>
        {!!result.worst_case.beyond_horizon?.length && <p>Future obligations remain beyond the horizon. A later due date is a timing change, not savings.</p>}</>
        : <p>No permitted cash result was returned. Missing cash is not zero and does not establish safety.</p>}
      <p className="helper">The worst cash assignment can differ from the failure witness. Neither result is a comparison of every possible action schedule.</p>
    </details>
    <style jsx>{`
      .failure-view { margin: 20px 0; padding: 18px; border: 1px solid #d9e1ed; border-radius: 12px; background: #fafcff; font-size: 13px; line-height: 1.6; overflow-wrap: anywhere; }
      h3 { font-size: 15px; } p { margin: 8px 0; } .coverage { display: flex; gap: 26px; flex-wrap: wrap; margin: 12px 0; } dt { color: #596a83; } dd { margin: 0; font-weight: 600; }
      .notice { padding: 10px 12px; border-left: 3px solid #bf781d; background: #fff8e8; color: #654812; }
      details { margin-top: 14px; } summary { cursor: pointer; font-weight: 600; } summary:focus-visible { outline: 2px solid #4e68df; outline-offset: 4px; }
      .assignments { display: grid; gap: 8px; padding: 10px 0; } table { width: 100%; border-collapse: collapse; text-align: left; margin-top: 12px; } th, td { vertical-align: top; padding: 10px 8px; border-bottom: 1px solid #dae2ed; } th { font-weight: 600; } small { display: block; margin-top: 5px; } .mobile-failures { display: none; }
      @media (max-width: 600px) { .failure-view { padding: 12px; } .desktop-failures { display: none; } .mobile-failures { display: block; margin: 12px 0; padding-left: 20px; } .mobile-failures li { padding: 8px 0; } }
    `}</style>
  </section>;
}
