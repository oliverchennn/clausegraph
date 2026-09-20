"use client";

import { useEffect, useRef, useState } from "react";
import { CalendarDays, CircleDollarSign, FileText, LockKeyhole } from "lucide-react";
import { Badge, Button } from "@/components/ui";
import { humanize, money, request, shortDate } from "@/lib/api";
import type { CashGapDiagnostic, CashGapRequest, PlanResult, VerificationResult, Workspace } from "@/lib/types";

type Props = {
  workspace: Workspace;
  plan: PlanResult;
  verification: VerificationResult;
  onEvidence: (ruleIds: string[]) => void;
};

const blockerCopy: Record<string, string> = {
  authorization: "Recorded approval does not permit this fixed schedule. Cash cannot grant permission.",
  evidence: "Required evidence is unresolved or unsupported. Cash cannot replace evidence.",
  accounting: "The obligation accounting is invalid. Adding cash cannot make an invalid ledger complete.",
  essential_services: "The schedule does not preserve an essential service. Cash alone cannot authorize that schedule.",
  dependencies: "A required action dependency is not satisfied. Cash cannot supply that dependency.",
};

function verificationTone(status: VerificationResult["status"]): "success" | "danger" | "warning" {
  return status === "SAFE" ? "success" : status === "UNSAFE" ? "danger" : "warning";
}

function verificationLabel(status: VerificationResult["status"]) {
  return status === "SAFE" ? "Verified Safe" : status === "UNSAFE" ? "Unsafe" : "Unknown";
}

function diagnosticLabel(status: CashGapDiagnostic["status"]) {
  if (status === "PROVEN_MINIMUM") return "Proven minimum";
  if (status === "SUFFICIENT_NOT_PROVEN_MINIMAL") return "Verified sufficient";
  if (status === "NOT_REQUIRED") return "No buffer required";
  if (status === "NOT_REPAIRABLE_WITH_CASH") return "Cash cannot repair";
  return "Inconclusive";
}

function diagnosticTone(status: CashGapDiagnostic["status"]): "success" | "danger" | "warning" {
  if (status === "PROVEN_MINIMUM" || status === "NOT_REQUIRED") return "success";
  return status === "NOT_REPAIRABLE_WITH_CASH" ? "danger" : "warning";
}

function balanceSummary(result: VerificationResult) {
  if (result.coverage_complete && result.worst_case_proven && result.worst_case) {
    return `Proven worst-case minimum ${money(result.worst_case.minimum_balance_cents, true)}`;
  }
  if (result.counterexample?.balance_cents != null) {
    return `Observed failing balance ${money(result.counterexample.balance_cents, true)}; worst case not proven`;
  }
  if (result.worst_case) {
    return `Observed minimum ${money(result.worst_case.minimum_balance_cents, true)}; worst case not proven`;
  }
  return result.counterexample && result.counterexample.simulation == null
    ? "No permitted cash trace for this invalid schedule"
    : "No worst-case cash minimum is proven";
}

export default function CashGapDiagnosticPanel({ workspace, plan, verification, onEvidence }: Props) {
  const [diagnostic, setDiagnostic] = useState<CashGapDiagnostic | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const controller = useRef<AbortController | null>(null);

  useEffect(() => () => controller.current?.abort(), []);

  async function diagnose() {
    controller.current?.abort();
    const current = new AbortController();
    controller.current = current;
    setDiagnostic(null);
    setError("");
    setBusy(true);
    const body: CashGapRequest = {
      ...verification.assumptions,
      plan_id: plan.id,
      revision: workspace.revision,
    };
    try {
      const result = await request<CashGapDiagnostic>("/cash-gap", workspace.session_id, {
        method: "POST",
        body: JSON.stringify(body),
        signal: current.signal,
      });
      if (!current.signal.aborted && result.plan_id === plan.id && result.revision === workspace.revision) {
        setDiagnostic(result);
      }
    } catch (caught) {
      if (!current.signal.aborted) {
        setError(caught instanceof Error ? caught.message : "The cash diagnostic could not complete. No amount is established.");
      }
    } finally {
      if (controller.current === current) {
        controller.current = null;
        setBusy(false);
      }
    }
  }

  const limitingEvents = (diagnostic?.limiting_event_ids ?? []).map(id => workspace.scenario.events.find(event => event.id === id)).filter(event => event != null);
  const limitingRuleIds = diagnostic ? Array.from(new Set([
    ...(diagnostic.limiting_rule_ids ?? []),
    ...limitingEvents.flatMap(event => event.source_rule_ids ?? []),
  ])) : [];
  const blockingProperties = diagnostic?.blocking_properties ?? [];
  const warnings = diagnostic?.warnings ?? [];
  const testedCash = diagnostic?.additional_opening_cash_cents ?? diagnostic?.lower_bound_cents;
  const future = plan.proposed.beyond_horizon ?? [];

  return <div className="cash-gap-area">
    <div className="cash-gap-trigger">
      <div><h4>Could cash alone repair this failure?</h4><p>Test the same saved actions, dates, evidence and declared bounds. This does not edit or adopt a plan.</p></div>
      <Button type="button" busy={busy} onClick={() => void diagnose()}><CircleDollarSign size={15} /> Explain cash gap</Button>
    </div>
    {error && <div className="inline-error" role="alert">{error} No stale or partial amount is shown.</div>}
    {diagnostic && <section className="cash-gap-result" data-testid="cash-gap-diagnostic" aria-labelledby="cash-gap-heading" role="status">
      <div className="section-title"><h4 id="cash-gap-heading"><CircleDollarSign size={17} /> Hypothetical cash diagnostic</h4><Badge tone={diagnosticTone(diagnostic.status)}>{diagnosticLabel(diagnostic.status)}</Badge></div>
      <p className="cash-gap-statement">{diagnostic.statement}</p>
      <div className={`cash-gap-amount cash-gap-${diagnosticTone(diagnostic.status)}`}>
        <span>{diagnostic.additional_opening_cash_cents != null
          ? diagnostic.minimality_proven ? "Proven fixed-schedule buffer" : "Verified-sufficient fixed-schedule buffer"
          : diagnostic.lower_bound_cents != null ? "Observed lower bound—not verified sufficient" : "No cash amount established"}</span>
        {diagnostic.additional_opening_cash_cents != null
          ? <strong>{money(diagnostic.additional_opening_cash_cents, true)}</strong>
          : diagnostic.lower_bound_cents != null ? <strong>{money(diagnostic.lower_bound_cents, true)}+</strong> : <strong>Not established</strong>}
        <p><LockKeyhole size={12} /> Hypothetical only—not funding, income, approval or permission. Recorded opening cash and the saved plan stay unchanged.</p>
      </div>

      <div className="cash-gap-comparison" aria-label="Fixed schedule cash comparison">
        <article>
          <div><span>Original fixed schedule</span><Badge tone={verificationTone(diagnostic.baseline.status)}>{verificationLabel(diagnostic.baseline.status)}</Badge></div>
          <strong>No added cash</strong>
          <p>{balanceSummary(diagnostic.baseline)}</p>
          <small>{diagnostic.baseline.checked_cases} / {diagnostic.baseline.total_cases} cases checked · {diagnostic.baseline.coverage_complete ? "complete coverage" : "incomplete coverage"}</small>
        </article>
        <article>
          <div><span>Same actions and dates</span>{diagnostic.funded && <Badge tone={verificationTone(diagnostic.funded.status)}>{verificationLabel(diagnostic.funded.status)}</Badge>}</div>
          <strong>{testedCash != null ? `With ${money(testedCash, true)} hypothetical opening cash` : "No verified cash comparison"}</strong>
          {diagnostic.funded ? <><p>{balanceSummary(diagnostic.funded)}</p><small>{diagnostic.funded.checked_cases} / {diagnostic.funded.total_cases} cases checked · {diagnostic.funded.coverage_complete ? "complete coverage" : "incomplete coverage"}</small></> : <p>Cash was not tested as a repair because no permissible amount is established.</p>}
        </article>
      </div>

      {diagnostic.minimality_witness && <p className="cash-gap-witness"><strong>One-cent check:</strong> {money(diagnostic.minimality_witness.tested_additional_cents, true)} was {diagnostic.minimality_witness.status.toLowerCase()} across {diagnostic.minimality_witness.coverage_complete ? "complete" : "incomplete"} coverage{diagnostic.minimality_witness.earliest_failing_date ? `, failing from ${shortDate(diagnostic.minimality_witness.earliest_failing_date)}` : ""}.</p>}

      {(diagnostic.limiting_date || limitingEvents.length > 0 || limitingRuleIds.length > 0) && <div className="cash-gap-limits">
        <div><CalendarDays size={15} /><span><strong>Limiting point</strong>{diagnostic.limiting_date ? shortDate(diagnostic.limiting_date) : "Date unavailable"}{limitingEvents.length > 0 && <small>{limitingEvents.map(event => event.title).join(" · ")}</small>}</span></div>
        {limitingRuleIds.length > 0 ? <button className="text-button" type="button" onClick={() => onEvidence(limitingRuleIds)}><FileText size={13} /> Open limiting evidence</button> : <span className="helper">No source-linked evidence was identified for this point.</span>}
      </div>}

      {blockingProperties.length > 0 && <div className="cash-gap-blockers"><h5>Non-cash blockers</h5><ul>{blockingProperties.filter(property => property !== "nonnegative_balance").map(property => <li key={property}><Badge tone="danger">{humanize(property)}</Badge><span>{blockerCopy[property] ?? `Resolve ${humanize(property)} before relying on a cash result.`}</span></li>)}</ul>{blockingProperties.every(property => property === "nonnegative_balance") && <p>The modeled failure is a cash shortfall; no authorization or evidence blocker was returned.</p>}</div>}

      <details className="cash-gap-future" open><summary>Future obligations remain visible ({future.length})</summary>{future.length > 0 ? <ul>{future.map(event => <li key={event.id}><span>{shortDate(event.date)} · {event.title}</span><strong>{event.direction === "income" ? "+" : "−"}{money(event.amount_cents, true)}</strong></li>)}</ul> : <p>No beyond-horizon obligations were returned for this saved plan.</p>}</details>
      {warnings.length > 0 && <ul className="cash-gap-warnings">{warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul>}
    </section>}
  </div>;
}
