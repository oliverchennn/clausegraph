"use client";

import { useEffect, useRef, useState } from "react";
import { CircleAlert, Coins, FileText, LoaderCircle } from "lucide-react";
import { Badge, Button } from "./ui";
import { money, request } from "@/lib/api";
import type { CashGapDiagnostic, CashGapRequest, PlanResult, VerificationResult, Workspace } from "@/lib/types";

type Props = {
  workspace: Workspace;
  plan: PlanResult;
  verification: VerificationResult;
  onEvidence: (ruleIds: string[]) => void;
};

/** Labels stay tied to the backend status; the UI never derives a proof claim of its own. */
const HEADLINE: Record<CashGapDiagnostic["status"], { tone: "success" | "warning" | "danger" | "neutral"; label: string }> = {
  NOT_REQUIRED: { tone: "success", label: "No additional cash required" },
  PROVEN_MINIMUM: { tone: "warning", label: "Proven minimum for this schedule" },
  SUFFICIENT_NOT_PROVEN_MINIMAL: { tone: "warning", label: "Sufficient · minimality not proven" },
  NOT_REPAIRABLE_WITH_CASH: { tone: "danger", label: "Cash cannot repair this" },
  INCONCLUSIVE: { tone: "neutral", label: "Inconclusive · coverage stopped early" },
};

export default function CashGapPanel({ workspace, plan, verification, onEvidence }: Props) {
  const [result, setResult] = useState<CashGapDiagnostic | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const controller = useRef<AbortController | null>(null);

  // A diagnostic belongs to one session, revision, plan and declared assumption set.
  // Any change to those makes a displayed result stale, so drop it rather than relabel it.
  useEffect(() => {
    controller.current?.abort();
    controller.current = null;
    setResult(null); setError(""); setBusy(false);
  }, [workspace.session_id, workspace.revision, plan.id, verification.id]);

  useEffect(() => () => controller.current?.abort(), []);

  async function diagnose() {
    controller.current?.abort();
    const current = new AbortController();
    controller.current = current;
    setBusy(true); setError(""); setResult(null);
    const body: CashGapRequest = {
      plan_id: plan.id, revision: workspace.revision,
      uncertainties: verification.assumptions.uncertainties ?? [],
      max_cases: verification.assumptions.max_cases,
      time_limit_seconds: verification.assumptions.time_limit_seconds,
    };
    try {
      const diagnostic = await request<CashGapDiagnostic>("/cash-gap", workspace.session_id,
        { method: "POST", body: JSON.stringify(body), signal: current.signal });
      if (!current.signal.aborted) setResult(diagnostic);
    } catch (caught) {
      if (!current.signal.aborted) {
        setError(caught instanceof Error ? caught.message : "The cash diagnostic could not be completed.");
      }
    } finally {
      if (controller.current === current) { controller.current = null; setBusy(false); }
    }
  }

  const headline = result ? HEADLINE[result.status] : null;
  const amount = result?.additional_opening_cash_cents;
  const blockers = result?.blocking_properties ?? [];
  const limitingRuleIds = result?.limiting_rule_ids ?? [];
  const warnings = result?.warnings ?? [];
  const baselineWorst = result?.baseline.worst_case;
  const fundedWorst = result?.funded?.worst_case;

  return <section className="cash-gap" aria-labelledby="cash-gap-heading" data-testid="cash-gap">
    <div className="section-title"><h4 id="cash-gap-heading"><Coins size={16} /> How large is the gap?</h4>
      <Badge tone="blue">Diagnostic</Badge></div>
    <p className="helper">Holding these exact actions and dates, how much explicitly hypothetical opening cash
      would the declared bounds need? This never obtains money, approves anything, or changes an obligation.</p>

    {!result && <Button type="button" busy={busy} onClick={() => void diagnose()} data-testid="cash-gap-run">
      <Coins size={14} /> Diagnose the cash gap</Button>}

    {busy && <p role="status" className="cash-gap-loading"><LoaderCircle size={15} className="spin" /> Checking every declared case…</p>}
    {error && <div role="alert" className="inline-error"><p>{error}</p>
      <Button type="button" onClick={() => void diagnose()}>Try again</Button></div>}

    {result && headline && <div className={`cash-gap-result cash-gap-${result.status.toLowerCase()}`} role="status" data-testid="cash-gap-result">
      <div className="section-title"><h5>Bounded cash diagnostic</h5>
        <span data-testid="cash-gap-status"><Badge tone={headline.tone}>{headline.label}</Badge></span></div>

      {amount != null
        ? <p className="cash-gap-amount" data-testid="cash-gap-amount">{money(amount)}
            <span>{result.minimality_proven ? "proven minimum for this fixed schedule" : "verified sufficient; not proven minimal"}</span></p>
        : <p className="cash-gap-amount cash-gap-none" data-testid="cash-gap-amount">No amount established
            <span>{result.lower_bound_cents != null
              ? `The declared model already proves ${money(result.lower_bound_cents)} is not enough on its own.`
              : "The declared model does not establish a cash requirement here."}</span></p>}

      <p className="cash-gap-statement">{result.statement}</p>
      <p className="helper cash-gap-not-funding" data-testid="cash-gap-not-funding">
        <CircleAlert size={13} /> This is a diagnostic, not funding. No money was obtained, no approval was
        granted, and every obligation is unchanged.</p>

      {blockers.length > 0 && <div className="cash-gap-blockers" data-testid="cash-gap-blockers">
        <strong>Blocked by more than cash:</strong>
        <ul>{blockers.map(property => <li key={property}>{property.replaceAll("_", " ")}</li>)}</ul>
        <p className="helper">Missing evidence and unauthorized schedules are never repaired by adding money.</p>
      </div>}

      {/* The same fixed schedule under an explicit cash assumption, beside the original. The saved plan is untouched. */}
      {result.funded && <dl className="cash-gap-compare" data-testid="cash-gap-compare">
        <div><dt>Saved schedule as recorded</dt>
          <dd>{result.baseline.status} · worst minimum {baselineWorst ? money(baselineWorst.minimum_balance_cents) : "not simulated"}</dd></div>
        <div><dt>Same schedule, with the assumed cash</dt>
          <dd>{result.funded.status} · worst minimum {fundedWorst ? money(fundedWorst.minimum_balance_cents) : "not simulated"}</dd></div>
      </dl>}

      <dl className="cash-gap-facts">
        <div><dt>Coverage</dt><dd>{result.baseline.coverage_complete
          ? `Complete · ${result.baseline.checked_cases} of ${result.baseline.total_cases} cases`
          : `Incomplete · ${result.baseline.checked_cases} of ${result.baseline.total_cases} cases checked`}</dd></div>
        <div><dt>Limiting date</dt><dd data-testid="cash-gap-limiting-date">{result.limiting_date ?? "None identified"}</dd></div>
      </dl>

      {limitingRuleIds.length > 0 && <button className="text-button" data-testid="cash-gap-evidence"
        onClick={() => onEvidence(limitingRuleIds)}>
        <FileText size={13} /> Evidence behind the limiting date</button>}

      {!!warnings.length && <ul className="cash-gap-warnings">
        {warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul>}

      <p className="helper">The saved plan is unchanged. Reloading keeps the recorded plan exactly as it is.</p>
    </div>}
  </section>;
}
