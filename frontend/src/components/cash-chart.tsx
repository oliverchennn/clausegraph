"use client";

import { Area, CartesianGrid, ComposedChart, Line, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { money, shortDate } from "@/lib/api";
import type { PlanResult, VerificationResult } from "@/lib/types";

export default function CashChart({ plan, verification }: { plan: PlanResult; verification?: VerificationResult | null }) {
  const baseline = new Map(plan.baseline.daily.map(day => [day.date, day.balance_cents]));
  const counterexample = verification?.counterexample;
  const failing = new Map(counterexample?.simulation?.daily.map(day => [day.date, day.balance_cents]) ?? []);
  const data = plan.proposed.daily.map(day => ({ date: day.date, proposed: day.balance_cents, baseline: baseline.get(day.date) ?? 0, counterexample: failing.get(day.date) }));
  return <div className="cash-chart" role="img" aria-label={`Cash projection. Baseline minimum ${money(plan.baseline.minimum_balance_cents)}; proposed minimum ${money(plan.proposed.minimum_balance_cents)}.${counterexample?.simulation ? ` Counterexample minimum ${money(counterexample.simulation.minimum_balance_cents)}, first failing date ${counterexample.earliest_failing_date ?? "unavailable"}.` : ""}`}>
    <ResponsiveContainer width="100%" height="100%"><ComposedChart data={data} margin={{ top: 12, right: 18, left: 1, bottom: 2 }}>
      <defs><linearGradient id="cashFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#4169ed" stopOpacity={0.16} /><stop offset="100%" stopColor="#4169ed" stopOpacity={0.015} /></linearGradient></defs>
      <CartesianGrid strokeDasharray="3 5" vertical={false} stroke="#e7eaf1" />
      <XAxis dataKey="date" tickFormatter={shortDate} tick={{ fill: "#8790a3", fontSize: 11 }} minTickGap={45} axisLine={false} tickLine={false} tickMargin={12} />
      <YAxis tickFormatter={value => money(Number(value))} tick={{ fill: "#8790a3", fontSize: 11 }} axisLine={false} tickLine={false} width={64} tickMargin={10} />
      <Tooltip labelFormatter={value => shortDate(String(value))} formatter={(value, name) => [money(Number(value), true), name === "counterexample" ? "Counterexample" : name === "proposed" ? "Nominal plan" : "Current path"]} contentStyle={{ border: "1px solid #e7eaf1", borderRadius: 12, boxShadow: "0 8px 30px #14204610", fontSize: 12 }} />
      <ReferenceLine y={0} stroke="#d08a88" strokeDasharray="4 4" />
      <Area type="stepAfter" dataKey="proposed" fill="url(#cashFill)" stroke="none" tooltipType="none" isAnimationActive={false} />
      <Line type="stepAfter" dataKey="baseline" name="baseline" stroke="#b2a7b5" strokeDasharray="5 5" strokeWidth={2} dot={false} isAnimationActive={false} />
      <Line type="stepAfter" dataKey="proposed" name="proposed" stroke="#4368e8" strokeWidth={2.8} dot={false} activeDot={{ r: 5, strokeWidth: 3, stroke: "#fff" }} isAnimationActive={false} />
      {counterexample?.simulation && <Line type="stepAfter" dataKey="counterexample" name="counterexample" stroke="#be4d49" strokeWidth={2.6} strokeDasharray="7 3" dot={false} activeDot={{ r: 5, strokeWidth: 3, stroke: "#fff" }} isAnimationActive={false} />}
      {counterexample?.simulation && counterexample.earliest_failing_date && <ReferenceLine x={counterexample.earliest_failing_date} stroke="#be4d49" strokeDasharray="3 4" />}
    </ComposedChart></ResponsiveContainer>
  </div>;
}
