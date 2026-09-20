"use client";

import { useEffect, useRef, useState } from "react";
import { LockKeyhole, Upload } from "lucide-react";
import { ApiError, request } from "@/lib/api";
import type { UploadResponse } from "@/lib/types";
import { Button, Modal } from "./ui";
import ProcessingConsent, { useProcessingConsent } from "./processing-consent";

export default function UploadDialog({ token, retryName, onClose, onUploaded, onBusyChange }: {
  token: string; retryName?: string; onClose: () => void; onUploaded: (response: UploadResponse) => Promise<void>; onBusyChange: (busy: boolean) => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const input = useRef<HTMLInputElement>(null);
  const active = useRef(true);
  const processing = useProcessingConsent(token, "upload");
  useEffect(() => { active.current = true; return () => { active.current = false; }; }, []);

  function selectFile(next: File | null) { setFile(next); processing.setConsent(false); setError(""); }

  async function upload() {
    if (!file || busy) return;
    setBusy(true); setError(""); onBusyChange(true);
    try {
      const consent = processing.consent;
      const route = consent ? await processing.confirmedRoute() : null;
      if (!active.current) return;
      const form = new FormData();
      form.append("file", file); form.append("consent", String(consent));
      if (route) {
        form.append("consent_text_provider", route.textId);
        form.append("consent_provider", route.evidenceId);
      }
      const response = await request<UploadResponse>("/documents", token, { method: "POST", body: form });
      processing.setConsent(false);
      if (active.current) await onUploaded(response);
    } catch (caught) {
      if (!active.current) return;
      if (caught instanceof ApiError && caught.status === 409) {
        processing.setConsent(false);
        await processing.refresh().catch(() => {});
      }
      if (active.current) setError(caught instanceof Error ? caught.message : "Upload failed. Your selected file is ready to retry.");
    } finally { onBusyChange(false); if (active.current) setBusy(false); }
  }

  return <Modal open onClose={() => { if (!busy) onClose(); }} title="Add your documents" description="A bill, a contract, or a benefits letter can change the picture.">
    <div className="dialog-body">
      {retryName && <p className="retry-instructions">To retry <strong>{retryName}</strong>, choose the original file again and give fresh processing consent. Identical contents reuse the document; a failed job is not a completed extraction.</p>}
      <button className="upload-dropzone" disabled={busy} onClick={() => input.current?.click()} onDragOver={event => event.preventDefault()} onDrop={event => { event.preventDefault(); if (!busy) selectFile(event.dataTransfer.files[0] || null); }}><span><Upload size={27} /></span><strong>{file ? file.name : "Choose a document or drop it here"}</strong><p>{file ? `${Math.ceil(file.size / 1024)} KB · Ready to upload` : "PDF, TXT, or CSV · Up to 10 MB"}</p></button>
      <input ref={input} className="sr-only" type="file" aria-label="Document file" disabled={busy} accept=".pdf,.txt,.csv,application/pdf,text/plain,text/csv" onChange={event => selectFile(event.target.files?.[0] || null)} />
      <ProcessingConsent state={processing} purpose="upload" busy={busy} />
      <div className="privacy-note"><LockKeyhole size={15} /><p>Documents stay in your private session. You can delete them and their derived data at any time. A local upload without processing consent retains readable native text for review; scanned pages need consented OCR.</p></div>
      {error && <div className="inline-error" role="alert">{error}</div>}
    </div>
    <div className="dialog-footer"><Button disabled={busy} onClick={onClose}>Cancel</Button><Button variant="primary" disabled={!file || file.size > 10 * 1024 * 1024 || processing.loading || !!processing.route.storage?.configured && !processing.consent} busy={busy} onClick={() => void upload()}><Upload size={15} /> Upload document</Button></div>
  </Modal>;
}
