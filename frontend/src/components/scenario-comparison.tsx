import { CalendarDays, Check, CircleAlert, X } from "lucide-react";
import { humanize, money, shortDate } from "@/lib/api";
import type { PlanResult, Simulation, Workspace } from "@/lib/types";
import { Badge, Button } from "@/components/ui";

function ComparisonCard({ title, label, simulation, actionNames, featured = false, testPrefix }: {
  title: string;
  label: string;
  simulation: Simulation;
  actionNames: string[];
  featured?: boolean;
  testPrefix: string;
}) {
  return <article className={`comparison-card ${featured ? "comparison-featured" : ""}`}>
    <div className="comparison-card-heading"><div><small>{label}</small><h3>{title}</h3></div>{featured && <Badge tone="blue">Preview · not saved</Badge>}</div>
    <dl>
      <div><dt>Lowest balance</dt><dd className={simulation.minimum_balance_cents < 0 ? "text-red" : "text-green"} data-testid={`${testPrefix}-minimum`}>{money(simulation.minimum_balance_cents)}</dd></div>
      <div><dt>Ending balance</dt><dd data-testid={`${testPrefix}-ending`}>{money(simulation.ending_balance_cents)}</dd></div>
      <div><dt>First shortfall</dt><dd>{simulation.first_shortfall_date ? shortDate(simulation.first_shortfall_date) : "None"}</dd></div>
      <div><dt>Cash gap</dt><dd>{money(simulation.additional_cash_required_cents)}</dd></div>
    </dl>
    <div className="comparison-actions"><span>Options applied</span><strong>{actionNames.length ? actionNames.join(", ") : "None"}</strong></div>
    <div className="comparison-future"><CalendarDays size={13} /> {(simulation.beyond_horizon ?? []).length} obligation{(simulation.beyond_horizon ?? []).length === 1 ? "" : "s"} remains beyond the horizon</div>
  </article>;
}

export default function ScenarioComparison({ active, candidate, label, summary, workspace, busy, onApply, onClose }: {
  active: PlanResult;
  candidate: PlanResult;
  label: string;
  summary: string;
  workspace: Workspace;
  busy: boolean;
  onApply: () => void;
  onClose: () => void;
}) {
  const name = (id: string) => workspace.scenario.actions.find(action => action.id === id)?.title || id;
  return <section className="panel comparison-panel" data-testid="scenario-comparison">
    <div className="comparison-heading">
      <div><span className="eyebrow">SAFE WHAT-IF PREVIEW</span><h2>See the tradeoff before changing your plan</h2><p>The recorded plan stays untouched until you explicitly apply this preview.</p></div>
      <button className="icon-button" aria-label="Close comparison" onClick={onClose}><X size={17} /></button>
    </div>
    <div className="comparison-assumption"><CircleAlert size={15} /><span>Changed assumption</span><strong>{summary}</strong></div>
    <div className="comparison-grid">
      <ComparisonCard title="Current path" label="No options" simulation={active.baseline} actionNames={[]} testPrefix="baseline" />
      <ComparisonCard title="Recorded plan" label={humanize(active.state)} simulation={active.proposed} actionNames={active.actions.map(item => name(item.action_id))} testPrefix="active" />
      <ComparisonCard title={label} label={humanize(candidate.state)} simulation={candidate.proposed} actionNames={candidate.actions.map(item => name(item.action_id))} featured testPrefix="candidate" />
    </div>
    <div className="comparison-footer">
      <span><Check size={14} /> Previewing never changes history or recorded approvals.</span>
      <div><Button onClick={onClose}>Keep recorded plan</Button><Button variant="primary" busy={busy} onClick={onApply}>Use this preview as plan</Button></div>
    </div>
  </section>;
}
