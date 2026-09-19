"use client";

import { ChevronRight } from "lucide-react";
import { Badge } from "./ui";
import { humanize, money, shortDate } from "@/lib/api";
import type { Workspace } from "@/lib/types";

export default function FactsReview({ workspace, onEvidence }: { workspace: Workspace; onEvidence: (ids: string[]) => void }) {
  const pendingReviews = workspace.rules.filter(rule => rule.review_status !== "reviewed").length;
  return <section className="panel facts-panel"><div className="panel-heading"><div><h2>Extracted facts & review</h2><p>Open a fact to inspect its exact source and confirm what it means.</p></div><Badge tone="warning">{pendingReviews} need review</Badge></div><div className="facts-table-wrapper"><table className="facts-table"><thead><tr><th>Fact</th><th>Evidence</th><th>Human review</th><th>Approval</th><th /></tr></thead><tbody>{workspace.rules.map(rule => <tr key={rule.id}><td><button onClick={() => onEvidence([rule.id])}>{rule.title}</button><small>{rule.amount_cents != null ? money(rule.amount_cents) : humanize(rule.kind)}{rule.due_date && ` · ${shortDate(rule.due_date)}`}</small></td><td><Badge tone={rule.evidence_status === "supported" ? "success" : "warning"}>{rule.evidence_status}</Badge></td><td>{humanize(rule.review_status || "pending")}</td><td><Badge tone={rule.approval_status === "approved" ? "success" : rule.approval_status === "denied" ? "danger" : "neutral"}>{humanize(rule.approval_status || "not_required")}</Badge></td><td><button className="icon-button" aria-label={`Review ${rule.title}`} onClick={() => onEvidence([rule.id])}><ChevronRight size={17} /></button></td></tr>)}</tbody></table>{!workspace.rules.length && <div className="empty-small">No extracted facts yet. Upload a document to get started.</div>}</div></section>;
}
