"use client";

import { useState } from "react";
import { Plus, Trash2, ShieldCheck } from "lucide-react";
import { Button, Field, Modal } from "./ui";
import { dollars, parseCents } from "@/lib/api";
import type { FinancialEvent, IntakeRequest, Scenario } from "@/lib/types";

type EditableEvent = FinancialEvent & { dollars: string };

export default function IntakeDialog({ scenario, onClose, onSave }: { scenario: Scenario; onClose: () => void; onSave: (value: IntakeRequest) => Promise<void> }) {
  const [cash, setCash] = useState(dollars(scenario.opening_balance_cents));
  const [start, setStart] = useState(scenario.start_date);
  const [horizon, setHorizon] = useState(scenario.horizon_days ?? 60);
  const [events, setEvents] = useState<EditableEvent[]>(scenario.events.map(event => ({ ...event, dollars: dollars(event.amount_cents) })));
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  function update(id: string, changes: Partial<EditableEvent>) { setEvents(current => current.map(event => event.id === id ? { ...event, ...changes } : event)); }
  async function save() {
    setBusy(true); setError("");
    try {
      const converted = events.map(({ dollars: amount, ...event }) => ({ ...event, amount_cents: parseCents(amount) }));
      if (converted.some(event => !event.title.trim() || !event.date)) throw new Error("Each event needs a name and a date.");
      await onSave({ opening_balance_cents: parseCents(cash), start_date: start, horizon_days: horizon, events: converted, essential_service_ids: converted.filter(event => event.essential && event.service_id).map(event => event.service_id!) });
      onClose();
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to save intake."); } finally { setBusy(false); }
  }
  return <Modal open onClose={onClose} title="Your financial picture" description="Set your available cash, expected income, and the expenses you need to protect." wide>
    <form onSubmit={event => { event.preventDefault(); void save(); }}><div className="dialog-body">
      <div className="form-grid three"><Field label="Available cash (USD)"><input required inputMode="decimal" value={cash} onChange={event => setCash(event.target.value)} /></Field><Field label="Plan start date"><input required type="date" value={start} onChange={event => setStart(event.target.value)} /></Field><Field label="Planning horizon"><select value={horizon} onChange={event => setHorizon(Number(event.target.value))}><option value={30}>30 days</option><option value={60}>60 days</option><option value={90}>90 days</option><option value={180}>180 days</option><option value={366}>366 days</option></select></Field></div>
      <div className="section-title"><h3>Income & expenses</h3><Button type="button" variant="ghost" onClick={() => setEvents(current => [...current, { id: `event-${crypto.randomUUID()}`, title: "", date: start, amount_cents: 0, dollars: "0.00", direction: "expense", kind: "projected", essential: false, service_id: `service-${crypto.randomUUID()}`, source_rule_ids: [] }])}><Plus size={14} /> Add event</Button></div>
      <div className="intake-events">{events.map(event => <div className="intake-event" key={event.id}>
        <input aria-label="Event name" placeholder="Expense or income name" value={event.title} onChange={e => update(event.id, { title: e.target.value })} required />
        <select aria-label={`${event.title} direction`} value={event.direction} onChange={e => update(event.id, { direction: e.target.value as "income" | "expense" })}><option value="expense">Expense</option><option value="income">Income</option></select>
        <input aria-label={`${event.title} amount in dollars`} value={event.dollars} inputMode="decimal" onChange={e => update(event.id, { dollars: e.target.value })} required />
        <input aria-label={`${event.title} date`} type="date" value={event.date} onChange={e => update(event.id, { date: e.target.value })} required />
        <select aria-label={`${event.title} certainty`} value={event.kind} onChange={e => update(event.id, { kind: e.target.value as "actual" | "projected" })}><option value="projected">Projected</option><option value="actual">Actual</option></select>
        <label className="check-label"><input type="checkbox" checked={event.essential ?? false} onChange={e => update(event.id, { essential: e.target.checked, service_id: event.service_id || `service-${event.id}` })} /><ShieldCheck size={14} /> Essential</label>
        <button type="button" className="icon-button remove-event" aria-label={`Remove ${event.title || "event"}`} onClick={() => setEvents(current => current.filter(item => item.id !== event.id))}><Trash2 size={15} /></button>
      </div>)}</div>
      {events.length === 0 && <div className="empty-small">Add your next paycheck and upcoming bills to build your first cash forecast.</div>}
      <p className="helper">Protected essentials stay in the plan. Future obligations remain tracked even when their dates fall beyond your planning horizon.</p>
      {error && <div className="inline-error" role="alert">{error}</div>}
    </div><div className="dialog-footer"><Button type="button" onClick={onClose}>Cancel</Button><Button variant="primary" type="submit" busy={busy}>Save & recalculate</Button></div></form>
  </Modal>;
}
