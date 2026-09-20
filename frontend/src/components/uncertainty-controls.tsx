"use client";

import { Plus, Trash2, TriangleAlert } from "lucide-react";
import { Button, Field } from "./ui";
import { money } from "@/lib/api";
import type { Action, Rule, Uncertainty, Workspace } from "@/lib/types";

export const MAX_DIMENSIONS = 8;
export const MAX_CASES = 10000;

type Props = {
  workspace: Workspace;
  dimensions: Uncertainty[];
  onChange: (dimensions: Uncertainty[]) => void;
  disabled?: boolean;
};

/** Values a single dimension contributes, as an exact integer. */
export function dimensionSize(dimension: Uncertainty): bigint {
  if (dimension.kind === "approval") return BigInt(dimension.outcomes.length);
  if (dimension.kind === "income_amount") {
    const span = BigInt(dimension.maximum_cents) - BigInt(dimension.minimum_cents) + BigInt(1);
    return span > BigInt(0) ? span : BigInt(0);
  }
  const start = Date.parse(`${dimension.earliest}T00:00:00Z`);
  const end = Date.parse(`${dimension.latest}T00:00:00Z`);
  if (Number.isNaN(start) || Number.isNaN(end) || end < start) return BigInt(0);
  return BigInt(Math.round((end - start) / 86_400_000)) + BigInt(1);
}

/**
 * Exact product of the declared domains. BigInt throughout: a product can far
 * exceed JavaScript's safe integer range, and a rounded count must never be
 * shown as exact. This mirrors the backend's arbitrary-precision count.
 */
export function exactCaseCount(dimensions: Uncertainty[]): bigint {
  return dimensions.reduce((total, dimension) => total * dimensionSize(dimension), BigInt(1));
}

/** Two dimensions may not declare the same property of the same target. */
export function duplicateTargets(dimensions: Uncertainty[]): Set<string> {
  const seen = new Map<string, number>();
  const duplicates = new Set<string>();
  for (const dimension of dimensions) {
    const target = dimension.kind === "approval" ? dimension.target_id : dimension.event_id;
    const key = `${dimension.kind}:${target}`;
    const count = (seen.get(key) ?? 0) + 1;
    seen.set(key, count);
    if (count > 1) duplicates.add(dimension.id);
  }
  return duplicates;
}

function uniqueId(dimensions: Uncertainty[], prefix: string) {
  let index = 1;
  const taken = new Set(dimensions.map(item => item.id));
  while (taken.has(`${prefix}-${index}`)) index += 1;
  return `${prefix}-${index}`;
}

const RATIONALE = "User-declared planning bound; an assumption, not a forecast.";

export default function UncertaintyControls({ workspace, dimensions, onChange, disabled }: Props) {
  const incomes = workspace.scenario.events.filter(event => event.direction === "income" && event.kind !== "actual");
  const approvalTargets: { id: string; title: string }[] = [
    ...workspace.scenario.actions.filter((action: Action) => action.approval_status !== "not_required")
      .map(action => ({ id: action.id, title: action.title })),
    ...workspace.rules.filter((rule: Rule) => rule.approval_status !== "not_required")
      .map(rule => ({ id: rule.id, title: `${rule.title} (rule)` })),
  ];
  const duplicates = duplicateTargets(dimensions);
  const full = dimensions.length >= MAX_DIMENSIONS;

  function replace(id: string, next: Uncertainty) {
    onChange(dimensions.map(item => (item.id === id ? next : item)));
  }

  function add(kind: Uncertainty["kind"]) {
    if (full) return;
    if (kind === "income_date" && incomes[0]) {
      onChange([...dimensions, { id: uniqueId(dimensions, "date"), kind: "income_date", basis: "user_assumption",
        event_id: incomes[0].id, earliest: incomes[0].date, latest: incomes[0].date, rationale: RATIONALE }]);
    } else if (kind === "income_amount" && incomes[0]) {
      onChange([...dimensions, { id: uniqueId(dimensions, "amount"), kind: "income_amount", basis: "user_assumption",
        event_id: incomes[0].id, minimum_cents: incomes[0].amount_cents, maximum_cents: incomes[0].amount_cents,
        rationale: RATIONALE }]);
    } else if (kind === "approval" && approvalTargets[0]) {
      onChange([...dimensions, { id: uniqueId(dimensions, "approval"), kind: "approval", basis: "user_assumption",
        target_id: approvalTargets[0].id, outcomes: ["approved", "denied", "pending"], rationale: RATIONALE }]);
    }
  }

  const count = exactCaseCount(dimensions);
  const overBudget = count > BigInt(MAX_CASES);

  return <div className="uncertainty-controls" data-testid="uncertainty-controls">
    <div className="uncertainty-add">
      <Button type="button" variant="ghost" disabled={disabled || full || !incomes.length}
        onClick={() => add("income_date")} data-testid="add-income-date"><Plus size={13} /> Income date</Button>
      <Button type="button" variant="ghost" disabled={disabled || full || !incomes.length}
        onClick={() => add("income_amount")} data-testid="add-income-amount"><Plus size={13} /> Income amount</Button>
      <Button type="button" variant="ghost" disabled={disabled || full || !approvalTargets.length}
        onClick={() => add("approval")} data-testid="add-approval"><Plus size={13} /> Approval outcome</Button>
      <span className="uncertainty-limit" data-testid="dimension-count">{dimensions.length} / {MAX_DIMENSIONS} dimensions</span>
    </div>
    {full && <p className="helper" role="status">Eight declared dimensions is the contract limit. Remove one to add another.</p>}

    {dimensions.length === 0 && <p className="helper">No declared uncertainty: verification checks the single nominal assignment.</p>}

    <ul className="uncertainty-list">
      {dimensions.map(dimension => {
        const duplicate = duplicates.has(dimension.id);
        return <li key={dimension.id} className={`uncertainty-item${duplicate ? " uncertainty-duplicate" : ""}`}
          data-testid={`dimension-${dimension.id}`}>
          <div className="uncertainty-item-head">
            <strong>{dimension.kind === "approval" ? "Approval outcomes"
              : dimension.kind === "income_amount" ? "Income amount" : "Income date"}</strong>
            <span className="uncertainty-size">{dimensionSize(dimension).toString()} values</span>
            <button type="button" className="icon-button" aria-label={`Remove ${dimension.id}`} disabled={disabled}
              onClick={() => onChange(dimensions.filter(item => item.id !== dimension.id))}><Trash2 size={14} /></button>
          </div>

          {dimension.kind !== "approval" && <Field label="Projected income">
            <select aria-label={`Income for ${dimension.id}`} value={dimension.event_id} disabled={disabled}
              onChange={event => replace(dimension.id, { ...dimension, event_id: event.target.value })}>
              {incomes.map(income => <option key={income.id} value={income.id}>{income.title}</option>)}
            </select></Field>}

          {dimension.kind === "income_date" && <div className="form-grid">
            <Field label="Earliest (inclusive)"><input type="date" required disabled={disabled}
              aria-label={`Earliest for ${dimension.id}`} value={dimension.earliest}
              onChange={event => replace(dimension.id, { ...dimension, earliest: event.target.value })} /></Field>
            <Field label="Latest (inclusive)"><input type="date" required disabled={disabled} min={dimension.earliest}
              aria-label={`Latest for ${dimension.id}`} value={dimension.latest}
              onChange={event => replace(dimension.id, { ...dimension, latest: event.target.value })} /></Field>
          </div>}

          {dimension.kind === "income_amount" && <div className="form-grid">
            <Field label="Minimum (cents, inclusive)"><input type="number" min={0} step={1} required disabled={disabled}
              aria-label={`Minimum cents for ${dimension.id}`} value={dimension.minimum_cents}
              onChange={event => replace(dimension.id, { ...dimension, minimum_cents: Number(event.target.value) })} /></Field>
            <Field label="Maximum (cents, inclusive)"><input type="number" min={0} step={1} required disabled={disabled}
              aria-label={`Maximum cents for ${dimension.id}`} value={dimension.maximum_cents}
              onChange={event => replace(dimension.id, { ...dimension, maximum_cents: Number(event.target.value) })} /></Field>
          </div>}

          {dimension.kind === "approval" && <>
            <Field label="Approval target"><select aria-label={`Approval target for ${dimension.id}`}
              value={dimension.target_id} disabled={disabled}
              onChange={event => replace(dimension.id, { ...dimension, target_id: event.target.value })}>
              {approvalTargets.map(target => <option key={target.id} value={target.id}>{target.title}</option>)}
            </select></Field>
            <Field label="Outcomes to check" hint="Hypothetical only; this records no third-party decision.">
              <select aria-label={`Outcomes for ${dimension.id}`} value={dimension.outcomes.join(",")} disabled={disabled}
                onChange={event => replace(dimension.id, { ...dimension, outcomes: event.target.value.split(",") as typeof dimension.outcomes })}>
                <option value="approved,denied,pending">approved / denied / pending</option>
                <option value="approved,denied">approved / denied</option>
                <option value="denied,pending">denied / pending</option>
                <option value="denied">denied only</option>
              </select></Field>
          </>}

          <Field label="Why this bound?" hint="User assumption. The verifier never infers a range from the sources.">
            <input aria-label={`Rationale for ${dimension.id}`} required maxLength={1000} disabled={disabled}
              value={dimension.rationale}
              onChange={event => replace(dimension.id, { ...dimension, rationale: event.target.value })} /></Field>

          {duplicate && <p role="alert" className="uncertainty-error" data-testid={`duplicate-${dimension.id}`}>
            This property of this target is already declared. Each may be declared only once.</p>}
        </li>;
      })}
    </ul>

    {/* Exact preflight count, never a rounded float. */}
    <div className={`uncertainty-count${overBudget ? " uncertainty-over-budget" : ""}`} data-testid="preflight-count">
      <strong>{count.toString()}</strong> case{count === BigInt(1) ? "" : "s"} in the declared model
      {overBudget && <span role="alert" data-testid="budget-warning"><TriangleAlert size={13} /> Above the {MAX_CASES}-case
        budget. The check will stop early and report incomplete coverage — it will not return Safe.</span>}
    </div>
  </div>;
}

export function summarize(dimension: Uncertainty): string {
  if (dimension.kind === "approval") return `${dimension.target_id}: ${dimension.outcomes.join(" / ")}`;
  if (dimension.kind === "income_amount") {
    return `${dimension.event_id}: every cent ${money(dimension.minimum_cents, true)} through ${money(dimension.maximum_cents, true)}, inclusive`;
  }
  return `${dimension.event_id}: every date ${dimension.earliest} through ${dimension.latest}, inclusive`;
}
