"use client";

import { useState } from "react";
import { FileText, Check, CircleHelp, ShieldCheck, ExternalLink } from "lucide-react";
import { Badge, Button, Field, Modal } from "./ui";
import { dollars, download, humanize, parseCents, requestBlob, shortDate } from "@/lib/api";
import type { ApprovalStatus, Rule, RuleReview, Workspace } from "@/lib/types";

function RuleEditor({ rule, workspace, onSave }: { rule: Rule; workspace: Workspace; onSave: (id: string, review: RuleReview) => Promise<void> }) {
  const [amount, setAmount] = useState(rule.amount_cents != null ? dollars(rule.amount_cents) : "");
  const [date, setDate] = useState(rule.due_date || "");
  const [approval, setApproval] = useState<ApprovalStatus>(rule.approval_status || "not_required");
  const [review, setReview] = useState<RuleReview["review_status"]>(rule.review_status || "pending");
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [conditions, setConditions] = useState(rule.conditions ?? []);
  const [evidenceConfirmed, setEvidenceConfirmed] = useState(false);
  async function save() {
    setBusy(true); setError(""); setSaved(false);
    try { await onSave(rule.id, { review_status: review, approval_status: approval, conditions, evidence_confirmed: evidenceConfirmed, ...(amount ? { amount_cents: parseCents(amount) } : {}), ...(date ? { due_date: date } : {}), note: note || null }); setSaved(true); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Review could not be saved."); }
    finally { setBusy(false); }
  }
  return <section className="rule-detail" data-testid={`rule-${rule.id}`}>
    <div className="rule-title"><span className="eyebrow">{rule.kind}</span><h3>{rule.title}</h3><div className="badge-row"><Badge tone={rule.evidence_status === "supported" ? "success" : "warning"}>Evidence {rule.evidence_status}</Badge><Badge>{Math.round((rule.extraction_confidence || 0) * 100)}% extraction confidence</Badge></div></div>
    {rule.evidence.map((evidence, index) => { const document = workspace.documents.find(doc => doc.id === evidence.document_id); const page = document?.pages?.find(item => item.page === evidence.page); return <div className="evidence-source" key={`${evidence.document_id}-${index}`}><div className="source-label"><FileText size={15} /><strong>{document?.name || evidence.document_id}</strong><span>v{evidence.version} · p. {evidence.page}</span></div><blockquote>{evidence.quote}</blockquote><div className="source-foot"><span>Characters {evidence.char_start}–{evidence.char_end}</span>{document?.synthetic && <Badge tone="warning">Synthetic</Badge>}</div>{page && <details><summary>Read source page <ExternalLink size={12} /></summary><pre>{page.text}</pre></details>}</div>; })}
    {rule.parties && rule.parties.length > 0 && <p className="helper">Parties: {rule.parties.join(", ")}</p>}
    <h4>Conditions & dependencies</h4>
    {conditions.length ? <ul className="condition-list">{conditions.map((condition, index) => <li key={index}>{condition.resolved && condition.satisfied ? <Check size={15} className="text-green" /> : <CircleHelp size={15} className="text-amber" />}<div className="condition-control"><span>{humanize(condition.fact)} {condition.operator} {String(condition.value ?? "")}<small>{condition.resolved ? condition.satisfied ? "Satisfied" : "Not satisfied" : "Unresolved — excluded from confirmed plans"}</small></span><select aria-label={`Condition ${humanize(condition.fact)}`} value={!condition.resolved ? "unresolved" : condition.satisfied ? "satisfied" : "unsatisfied"} onChange={event => setConditions(current => current.map((item, itemIndex) => itemIndex === index ? { ...item, resolved: event.target.value !== "unresolved", satisfied: event.target.value === "unresolved" ? null : event.target.value === "satisfied" } : item))}><option value="unresolved">Unresolved</option><option value="satisfied">I verified this condition is satisfied</option><option value="unsatisfied">I verified this condition is not satisfied</option></select></div></li>)}</ul> : <p className="helper">No additional conditions recorded.</p>}
    <label className="consent-box"><input type="checkbox" checked={evidenceConfirmed} onChange={event => setEvidenceConfirmed(event.target.checked)} /><span>I checked this rule against the original source.<small>Required with a review note when resolving disputed evidence. This does not confirm third-party approval.</small></span></label>
    {Array.from(new Set(rule.evidence.map(item => item.document_id))).map(id => <Button key={id} className="source-download" onClick={async () => { try { const source = await requestBlob(`/documents/${encodeURIComponent(id)}/original`, workspace.session_id); download(source, workspace.documents.find(item => item.id === id)?.name || "original-document"); } catch (caught) { setError(caught instanceof Error ? caught.message : "Original could not be downloaded."); } }}>Download original source</Button>)}
    {!!rule.dependencies?.length && <p className="helper">Requires: {rule.dependencies.join(", ")}</p>}
    {rule.verifier_notes && <div className="note-box">{rule.verifier_notes}</div>}
    <div className="review-form"><div className="section-title"><h4><ShieldCheck size={15} /> Human review</h4><span className="helper">Separate from lender approval</span></div><div className="form-grid"><Field label="Evidence review"><select value={review} onChange={e => setReview(e.target.value as RuleReview["review_status"])}><option value="pending">Pending review</option><option value="reviewed">Reviewed</option><option value="unresolved">Unresolved</option><option value="rejected">Rejected</option></select></Field><Field label="Third-party approval"><select aria-label={`Approval for ${rule.title}`} value={approval} onChange={e => setApproval(e.target.value as ApprovalStatus)}><option value="not_required">Not required</option><option value="pending">Pending</option><option value="approved">Approved</option><option value="denied">Denied</option></select></Field>{rule.amount_cents != null && <Field label="Amount (USD)"><input inputMode="decimal" value={amount} onChange={e => setAmount(e.target.value)} /></Field>}{rule.due_date && <Field label="Due date"><input type="date" value={date} onChange={e => setDate(e.target.value)} /></Field>}</div><Field label="Review note"><textarea rows={2} value={note} onChange={e => setNote(e.target.value)} placeholder="Record how you verified this fact or approval…" /></Field><p className="helper">Only mark approved after the relevant party confirms. Changing a value may require the source evidence to be verified again.</p>{error && <div className="inline-error" role="alert">{error}</div>}<Button variant="primary" busy={busy} onClick={() => void save()}>{saved ? <><Check size={15} /> Review saved</> : "Save review & recalculate"}</Button></div>
  </section>;
}

export default function EvidenceDrawer({ ruleIds, workspace, onClose, onSave }: { ruleIds: string[]; workspace: Workspace; onClose: () => void; onSave: (id: string, review: RuleReview) => Promise<void> }) {
  const rules = workspace.rules.filter(rule => ruleIds.includes(rule.id));
  return <Modal open onClose={onClose} title="Follow the evidence" description="Every recommendation starts with a specific clause. Review its source, conditions, and approval separately." drawer><div className="dialog-body">{rules.length ? rules.map(rule => <RuleEditor key={rule.id} rule={rule} workspace={workspace} onSave={onSave} />) : <div className="empty-small">This graph element has no linked source rule. Select a rule or another relationship to inspect its evidence.</div>}<p className="helper">Workspace revision {workspace.revision} · Plan starts {shortDate(workspace.scenario.start_date)}</p></div></Modal>;
}
