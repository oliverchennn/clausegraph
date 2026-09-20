"use client";

import { ArrowUpRight, CalendarDays, ShieldCheck, Wallet } from "lucide-react";
import { Badge } from "./ui";
import { humanize, money } from "@/lib/api";
import type { PlanResult, Workspace } from "@/lib/types";

export default function OverviewMetrics({ workspace, plan, onIntake }: { workspace: Workspace; plan: PlanResult; onIntake: () => void }) {
  const isProtected = plan.proposed.minimum_balance_cents >= 0 && plan.state === "confirmed";
  const recordedOpening = workspace.scenario.opening_balance_cents;
  const assumedOpening = plan.assumptions?.opening_balance_cents;
  // A saved scenario override lives on the plan, never on the recorded financial picture.
  const openingIsAssumed = assumedOpening != null && assumedOpening !== recordedOpening;
  return <div className="metric-grid"><section className="metric-card"><div className="metric-title">Available cash <Wallet size={17} /></div><div className="metric-value">{money(assumedOpening ?? recordedOpening)}</div><div className="metric-foot">{openingIsAssumed ? `Assumed starting balance · recorded ${money(recordedOpening)}` : "Starting balance"} <button onClick={onIntake}>Edit financial picture <ArrowUpRight size={12} /></button></div></section><section className="metric-card protected-metric"><div className="metric-title">Lowest projected balance <ShieldCheck size={18} /></div><div className={`metric-value ${plan.proposed.minimum_balance_cents < 0 ? "text-red" : "text-green"}`} data-testid="minimum-balance">{money(plan.proposed.minimum_balance_cents)}<span className="metric-arrow"><ArrowUpRight size={18} /></span></div><div className="metric-foot">Current path: <span className={plan.baseline.minimum_balance_cents < 0 ? "text-red" : ""}>{money(plan.baseline.minimum_balance_cents)}</span><Badge tone={isProtected ? "success" : plan.state === "conditional" ? "warning" : "danger"}>{isProtected ? "Cash stays nonnegative" : humanize(plan.state)}</Badge></div></section><section className="metric-card"><div className="metric-title">At the end of your plan <CalendarDays size={17} /></div><div className="metric-value" data-testid="ending-balance">{money(plan.proposed.ending_balance_cents)}</div><div className="metric-foot">{workspace.scenario.horizon_days}-day projection <span className="neutral-foot">Timing changes aren’t savings</span></div></section></div>;
}
