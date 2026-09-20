"use client";

import { useEffect, useRef, useState } from "react";
import { ClipboardList, Download, Sparkles } from "lucide-react";
import { ApiError, download, request } from "@/lib/api";
import type { components } from "@/lib/api-types";
import type { DraftResponse } from "@/lib/types";
import { Badge, Button, Field, Modal } from "./ui";
import ProcessingConsent, { useProcessingConsent } from "./processing-consent";

export default function DraftDialog({ token, initial, onClose, onCopied }: {
  token: string; initial: DraftResponse; onClose: () => void; onCopied: () => void;
}) {
  const [draft, setDraft] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [generated, setGenerated] = useState(false);
  const active = useRef(true);
  const processing = useProcessingConsent(token, "draft");
  useEffect(() => { active.current = true; return () => { active.current = false; }; }, []);

  async function generate() {
    if (busy || !processing.consent) return;
    setBusy(true); setError("");
    try {
      const route = await processing.confirmedRoute();
      if (!active.current) return;
      const body: components["schemas"]["DraftRequest"] = { use_provider: true, consent: true, consent_text_provider: route.textId };
      const result = await request<DraftResponse>(`/actions/${encodeURIComponent(initial.action_id)}/draft`, token, { method: "POST", body: JSON.stringify(body) });
      if (!active.current) return;
      setDraft(result); setGenerated(true); processing.setConsent(false);
    } catch (caught) {
      if (!active.current) return;
      if (caught instanceof ApiError && caught.status === 409) {
        processing.setConsent(false);
        await processing.refresh().catch(() => {});
      }
      if (active.current) setError(caught instanceof Error ? caught.message : "Draft generation failed. Your current draft is preserved.");
    } finally { if (active.current) setBusy(false); }
  }

  return <Modal open onClose={() => { if (!busy) onClose(); }} title="Your request, ready to review" description="A draft only. Nothing has been sent or submitted.">
    <div className="dialog-body"><Badge tone="blue">Not sent</Badge><p className="helper" role="status">{generated ? "Provider-generated draft. Check every detail against your source." : "Local template draft. No external model was called to create this message."}</p>
      <Field label="Subject"><input aria-label="Subject" disabled={busy} value={draft.subject} onChange={event => setDraft({ ...draft, subject: event.target.value })} /></Field>
      <Field label="Message"><textarea aria-label="Message" disabled={busy} rows={10} value={draft.body} onChange={event => setDraft({ ...draft, body: event.target.value })} /></Field>
      <p className="helper">Check the details and send it yourself when you’re ready. Approval is only recorded when you explicitly update the source review.</p>
      <details className="draft-provider"><summary>Optional: generate a replacement with a model</summary><ProcessingConsent state={processing} purpose="draft" busy={busy} /><Button disabled={!processing.consent || processing.loading} busy={busy} onClick={() => void generate()}><Sparkles size={15} /> Generate replacement draft</Button></details>
      {error && <div className="inline-error" role="alert">{error} Your current draft has been preserved.</div>}
    </div>
    <div className="dialog-footer"><Button disabled={busy} onClick={() => download(new Blob([`${draft.subject}\n\n${draft.body}`], { type: "text/plain" }), "clausegraph-request.txt")}>Download draft <Download size={14} /></Button><Button disabled={busy} variant="primary" onClick={() => void navigator.clipboard.writeText(`${draft.subject}\n\n${draft.body}`).then(onCopied).catch(() => setError("Could not copy to the clipboard. Download the draft instead."))}><ClipboardList size={15} /> Copy draft</Button></div>
  </Modal>;
}
