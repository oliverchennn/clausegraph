import { ArrowRight, CalendarDays, FileCheck2, GitBranch, Wallet } from "lucide-react";
import { money, shortDate } from "@/lib/api";
import type { FinancialEvent, PlanResult, Workspace } from "@/lib/types";

type Trace = NonNullable<PlanResult["decision_traces"]>[number];
type Change = NonNullable<Trace["changes"]>[number];

function eventLabel(event: FinancialEvent) {
  return `${money(event.amount_cents)} ${event.title}`;
}

function changeLabel(change: Change) {
  if (change.operation === "remove" && change.before) {
    return `${eventLabel(change.before)} removed from the projected ledger.`;
  }
  if ((change.operation === "shift" || change.operation === "accelerate") && change.before && change.after) {
    const verb = change.operation === "accelerate" ? "moves earlier" : "moves";
    return `${eventLabel(change.before)} ${verb} from ${shortDate(change.before.date)} to ${shortDate(change.after.date)}.`;
  }
  if (change.after) {
    return `${eventLabel(change.after)} added on ${shortDate(change.after.date)}${change.operation === "fee" ? " as a fee" : ""}.`;
  }
  return "Ledger change recorded by the planner.";
}

export default function DecisionTracePanel({ plan, workspace, onEvidence }: {
  plan: PlanResult;
  workspace: Workspace;
  onEvidence: (ruleIds: string[]) => void;
}) {
  const traces = plan.decision_traces ?? [];
  if (!traces.length) return null;

  return <section className="panel decision-trace" data-testid="decision-trace">
    <div className="trace-heading">
      <div>
        <span className="eyebrow">AUDITABLE DECISION PATH</span>
        <h2>Why this plan?</h2>
        <p>Follow each recommendation from the original document to its exact cash impact.</p>
      </div>
      <div className="trace-outcome">
        <span>Lowest balance</span>
        <strong>{money(plan.baseline.minimum_balance_cents)} <ArrowRight size={14} /> {money(plan.proposed.minimum_balance_cents)}</strong>
      </div>
    </div>
    <div className="trace-list">
      {traces.map(trace => {
        const action = workspace.scenario.actions.find(item => item.id === trace.action_id);
        const rules = trace.source_rule_ids.map(id => workspace.rules.find(rule => rule.id === id)).filter(Boolean);
        const documents = trace.source_document_ids.map(id => workspace.documents.find(document => document.id === id)).filter(Boolean);
        return <article className="trace-chain" key={`${trace.action_id}-${trace.execution_date}`}>
          <div className="trace-step">
            <span className="trace-icon"><FileCheck2 size={17} /></span>
            <small>1 · Source</small>
            <strong>{documents.map(document => document?.name).join(", ") || "Reviewed source"}</strong>
            <button className="text-button" onClick={() => onEvidence(trace.source_rule_ids)}>Open exact evidence <ArrowRight size={12} /></button>
          </div>
          <ArrowRight className="trace-arrow" size={17} />
          <div className="trace-step">
            <span className="trace-icon"><GitBranch size={17} /></span>
            <small>2 · Clause</small>
            <strong>{rules.map(rule => rule?.title).join(", ") || "Reviewed rule"}</strong>
            <span>{rules.every(rule => rule?.evidence_status === "supported") ? "Evidence supported" : "Review required"}</span>
          </div>
          <ArrowRight className="trace-arrow" size={17} />
          <div className="trace-step">
            <span className="trace-icon"><CalendarDays size={17} /></span>
            <small>3 · Action</small>
            <strong>{action?.title || trace.action_id}</strong>
            <span>Execute {shortDate(trace.execution_date)}</span>
          </div>
          <ArrowRight className="trace-arrow" size={17} />
          <div className="trace-step trace-ledger">
            <span className="trace-icon"><Wallet size={17} /></span>
            <small>4 · Ledger effect</small>
            <strong>{(trace.changes ?? []).length} verified change{(trace.changes ?? []).length === 1 ? "" : "s"}</strong>
            {(trace.changes ?? []).map((change, index) => <span key={index} data-testid="trace-change">{changeLabel(change)}</span>)}
          </div>
        </article>;
      })}
    </div>
    <div className="trace-footer"><strong>5 · Outcome</strong><span>The cash projection is recomputed from these ledger changes—no model-generated arithmetic.</span></div>
  </section>;
}
