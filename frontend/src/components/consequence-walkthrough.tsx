"use client";

import { FileText, GitBranch, ShieldAlert } from "lucide-react";
import ConsequenceSteps, { type ConsequenceStep } from "@/components/consequence-steps";
import { Badge, Button } from "@/components/ui";
import { humanize, money, shortDate } from "@/lib/api";
import type { ConsequenceWalkthroughProps, FinancialEvent } from "@/lib/types";

type Trace = NonNullable<ConsequenceWalkthroughProps["candidate"]["decision_traces"]>[number];
type Change = NonNullable<Trace["changes"]>[number];

function eventLine(event: FinancialEvent) {
  return `${money(event.amount_cents)} ${event.title} on ${shortDate(event.date)}`;
}

function changeLine(change: Change) {
  if (change.operation === "remove" && change.before) return `${eventLine(change.before)} is removed from this preview ledger.`;
  if ((change.operation === "shift" || change.operation === "accelerate") && change.before && change.after) {
    const verb = change.operation === "accelerate" ? "moves earlier" : "moves";
    return `${money(change.before.amount_cents)} ${change.before.title} ${verb} from ${shortDate(change.before.date)} to ${shortDate(change.after.date)}. It remains the same obligation.`;
  }
  if (change.after) return `${eventLine(change.after)} is ${change.operation === "fee" ? "added as a fee" : "added to this preview ledger"}.`;
  return "The deterministic engine returned an unrenderable ledger change.";
}

export default function ConsequenceWalkthrough({ workspace, recorded, candidate, actionId, onEvidence, onGraph }: ConsequenceWalkthroughProps) {
  const action = workspace.scenario.actions.find(item => item.id === actionId);
  const trace = candidate.decision_traces?.find(item => item.action_id === actionId);
  const blocker = candidate.excluded_actions?.[actionId] || (!trace ? "No permitted action trace was returned for this preview." : "");
  const ruleIds = trace?.source_rule_ids?.length ? trace.source_rule_ids : action?.source_rule_ids ?? [];
  const rules = ruleIds.map(id => workspace.rules.find(rule => rule.id === id)).filter((rule): rule is NonNullable<typeof rule> => !!rule);
  const documentIds = trace?.source_document_ids?.length ? trace.source_document_ids : [...new Set(rules.flatMap(rule => rule.evidence.map(item => item.document_id)))];
  const documents = documentIds.map(id => workspace.documents.find(document => document.id === id)).filter((document): document is NonNullable<typeof document> => !!document);
  const dependencies = [...new Set([...rules.flatMap(rule => rule.dependencies ?? []), ...(action?.requires ?? [])])];
  const dependencyLabels = dependencies.map(id => workspace.rules.find(rule => rule.id === id)?.title || workspace.scenario.actions.find(item => item.id === id)?.title || id);
  const changes = trace?.changes ?? [];
  const futureBefore = recorded.proposed.beyond_horizon ?? [];
  const futureAfter = candidate.proposed.beyond_horizon ?? [];

  const evidenceControls = <div className="button-row"><Button onClick={() => onEvidence(ruleIds)} disabled={!ruleIds.length}><FileText size={13} /> Open exact evidence</Button><Button onClick={() => onGraph(ruleIds)} disabled={!ruleIds.length}><GitBranch size={13} /> View linked graph path</Button></div>;
  const steps: ConsequenceStep[] = [
    { id: "source", label: "Source", title: documents.map(item => item.name).join(", ") || "Source unavailable", summary: `${documents.length} exact document${documents.length === 1 ? "" : "s"}`, detail: <><p>{documents.length ? `This preview cites ${documents.map(item => `${item.name} v${item.version}`).join(", ")}.` : "No source document ID was returned."}</p>{evidenceControls}</> },
    { id: "rule", label: "Reviewed rule", title: rules.map(rule => rule.title).join(", ") || "Rule unavailable", summary: `${rules.length} linked rule${rules.length === 1 ? "" : "s"}`, detail: <div className="consequence-events">{rules.map(rule => <div className="consequence-event" key={rule.id}><strong>{rule.title}</strong><span>Evidence {humanize(rule.evidence_status)} · Human review {humanize(rule.review_status)} · Approval {humanize(rule.approval_status)}</span></div>)}</div> },
    { id: "dependency", label: "Dependency", title: dependencyLabels.join(", ") || "No additional dependency", summary: dependencies.length ? `${dependencies.length} recorded prerequisite${dependencies.length === 1 ? "" : "s"}` : "No extra prerequisite returned", detail: <><p>{dependencies.length ? "These relationships come from the reviewed rule/action graph; they are not inferred from the cash result." : "This action has no additional recorded prerequisite beyond its linked rules."}</p>{dependencyLabels.length > 0 && <ul>{dependencyLabels.map(label => <li key={label}>{label}</li>)}</ul>}<Button onClick={() => onGraph(ruleIds)} disabled={!ruleIds.length}><GitBranch size={13} /> Highlight dependency path</Button></> },
    { id: "effect", label: "Proposed effect", title: action?.title || actionId, summary: blocker ? "Blocked — no permitted transformation" : `${changes.length} deterministic ledger change${changes.length === 1 ? "" : "s"}`, detail: blocker ? <p>{blocker} No action-specific cash result is shown.</p> : <div className="consequence-events">{changes.map((change, index) => <div className="consequence-event" data-testid={`effect-${change.operation}`} key={`${change.operation}-${index}`}><strong>{humanize(change.operation)}</strong><span>{changeLine(change)}</span></div>)}</div> },
    { id: "cash", label: "Cash consequence", title: blocker ? "Cash projection withheld" : `${money(candidate.proposed.minimum_balance_cents)} lowest balance`, summary: blocker ? "Resolve the blocker first" : "Server-computed preview, not saved", detail: blocker ? <p>A blocked action has no authorized effect trace, so this walkthrough does not attach an unrelated fallback ledger to it.</p> : <div data-testid="cash-consequence"><div className="consequence-events"><div className="consequence-event"><strong>Recorded plan</strong><span>Minimum {money(recorded.proposed.minimum_balance_cents)} · Ending {money(recorded.proposed.ending_balance_cents)}</span></div><div className="consequence-event"><strong>This preview</strong><span>Minimum {money(candidate.proposed.minimum_balance_cents)} · Ending {money(candidate.proposed.ending_balance_cents)}{candidate.proposed.first_shortfall_date ? ` · First shortfall ${shortDate(candidate.proposed.first_shortfall_date)}` : " · No shortfall"}</span></div></div><p>{futureBefore.length ? `Before this preview: ${futureBefore.map(eventLine).join("; ")}.` : "The recorded plan has no returned beyond-horizon obligation."}</p><p>{futureAfter.length ? `After this preview: ${futureAfter.map(eventLine).join("; ")}. A later date is timing, not savings.` : "No obligation remains beyond this preview horizon; an accelerated obligation may now be inside the returned daily ledger."}</p></div> },
  ];

  return <section className="panel consequence-walkthrough" data-testid="consequence-walkthrough">
    <div className="consequence-heading"><div><span className="eyebrow">EVIDENCE-LINKED CONSEQUENCE</span><h2>Follow this option from clause to cash</h2><p>Read-only preview. Nothing is cancelled, paid, submitted or saved by this walkthrough.</p></div><Badge tone={blocker ? "danger" : "blue"}>{blocker ? "Blocked" : "Preview · not saved"}</Badge></div>
    {blocker && <div className="consequence-blocked" role="alert"><ShieldAlert size={15} /> <strong>Transformation blocked.</strong> {blocker} Cash cannot replace permission, evidence or a required dependency.</div>}
    <ConsequenceSteps steps={steps} identity={`${candidate.id}:${actionId}`} />
  </section>;
}
