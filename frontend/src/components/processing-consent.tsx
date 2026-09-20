"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { RefreshCw } from "lucide-react";
import { request } from "@/lib/api";
import type { ProviderStatus } from "@/lib/types";
import { Button } from "./ui";

type Purpose = "upload" | "draft";

function destinations(providers: ProviderStatus[], purpose: Purpose) {
  const texts = providers.filter(item => ["NVIDIA Nemotron", "Brev-hosted Nemotron"].includes(item.name));
  const evidence = providers.filter(item => ["NVIDIA Nemotron evidence", "Gemini"].includes(item.name));
  const storage = providers.filter(item => item.name === "DigitalOcean Spaces");
  const text = texts.length === 1 ? texts[0] : undefined;
  const check = evidence.length === 1 ? evidence[0] : undefined;
  const originals = storage.length === 1 ? storage[0] : undefined;
  const valid = !!text && (purpose === "draft" || !!check && !!originals);
  const relevant = purpose === "draft" ? [text] : [text, check, originals];
  return {
    text, evidence: check, storage: originals, valid,
    textId: text?.name === "Brev-hosted Nemotron" ? "brev" as const : "nvidia" as const,
    evidenceId: check?.name === "Gemini" ? "gemini" : "nvidia",
    key: valid ? JSON.stringify(relevant.map(item => [item!.name, item!.model, item!.configured])) : "",
  };
}

// Consent belongs to this dialog/session and the disclosed recipient/model snapshot.
// Unknown or ambiguous provider statuses never fall back to an assumed recipient.
export function useProcessingConsent(token: string, purpose: Purpose) {
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [acceptedKey, setAcceptedKey] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const lifetime = useRef<AbortController | null>(null);
  const route = destinations(providers, purpose);

  const refresh = useCallback(async () => {
    const controller = lifetime.current;
    if (!controller || controller.signal.aborted) throw new Error("This dialog is closed.");
    setLoading(true); setError("");
    try {
      const next = await request<ProviderStatus[]>("/providers", token, { signal: AbortSignal.any([controller.signal, AbortSignal.timeout(20_000)]) });
      if (controller.signal.aborted) throw new Error("This dialog is closed.");
      setProviders(next);
      return destinations(next, purpose);
    } catch (caught) {
      if (!controller.signal.aborted) {
        setProviders([]); setAcceptedKey("");
        setError("Processing destinations could not be loaded. Refresh before consenting to external processing.");
      }
      throw caught;
    } finally { if (!controller.signal.aborted) setLoading(false); }
  }, [token, purpose]);

  useEffect(() => {
    const controller = new AbortController();
    lifetime.current = controller;
    void refresh().catch(() => {});
    return () => controller.abort();
  }, [refresh]);

  async function confirmedRoute() {
    const accepted = acceptedKey;
    const latest = await refresh();
    if (!accepted || !latest.valid || latest.key !== accepted) {
      setAcceptedKey("");
      throw new Error("Processing destinations changed or consent is missing. Review the destinations and consent again; nothing was sent for processing.");
    }
    return latest;
  }

  return {
    route, loading, error, refresh, confirmedRoute,
    consent: !!acceptedKey && acceptedKey === route.key,
    changed: !!acceptedKey && !!route.key && acceptedKey !== route.key,
    setConsent: (value: boolean) => setAcceptedKey(value && route.valid ? route.key : ""),
  };
}

export default function ProcessingConsent({ state, purpose, busy }: {
  state: ReturnType<typeof useProcessingConsent>; purpose: Purpose; busy: boolean;
}) {
  const { route } = state;
  return <section className="processing-consent" aria-label="Processing destinations">
    <div className="section-title"><h3>Processing destinations</h3><Button variant="ghost" disabled={busy} busy={state.loading} onClick={() => void state.refresh().catch(() => {})}><RefreshCw size={14} /> Refresh destinations</Button></div>
    {state.loading && <p role="status" className="helper">Checking the selected providers…</p>}
    {state.error && <p className="inline-error" role="alert">{state.error}</p>}
    {!state.loading && !state.error && !route.valid && <p className="inline-error" role="alert">The selected processing destinations are incomplete or ambiguous. External processing is unavailable until they can be confirmed.</p>}
    {route.text && <div className="processing-destination"><strong>{purpose === "upload" ? "Text extraction" : "Optional draft generation"}</strong><p>{route.text.name === "Brev-hosted Nemotron" ? "Brev-hosted Nemotron · your configured private GPU endpoint" : "NVIDIA · hosted Nemotron"}</p><small>{route.text.model} · {route.text.configured ? "Configured; connectivity and accuracy not established" : "Not configured; processing may fail"}</small></div>}
    {purpose === "upload" && route.evidence && <div className="processing-destination"><strong>Evidence checks and scanned-page OCR</strong><p>{route.evidence.name === "Gemini" ? "Google · Gemini" : "NVIDIA · hosted Nemotron evidence"}</p><small>{route.evidence.model} · {route.evidence.configured ? "Configured; connectivity and accuracy not established" : "Not configured; processing may fail"}</small></div>}
    {purpose === "upload" && route.storage && <p className="helper">Original storage: {route.storage.configured ? "DigitalOcean Spaces (private cloud). External consent is required to upload." : "private local files."}</p>}
    {state.changed && <p role="alert" className="inline-error">The processing destinations changed. Review them and consent again.</p>}
    <label className="consent-box"><input type="checkbox" disabled={busy || state.loading || !route.valid} checked={state.consent} onChange={event => state.setConsent(event.target.checked)} /><span>{purpose === "upload" ? "I consent to external document processing." : "I consent to external draft generation."}<small>{purpose === "upload" ? "Document content and your scenario’s financial facts may be sent to the text and evidence/OCR destinations listed above. Model agreement is not proof; your review is still required. Without consent, external processing will not run." : "The action title, description, requested date and source quotes will be sent to the text destination above to create a replacement draft. Your edited message is not sent. Nothing is submitted to a creditor or other recipient."}</small></span></label>
  </section>;
}
