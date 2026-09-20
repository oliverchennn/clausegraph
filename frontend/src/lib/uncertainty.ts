/**
 * Shared consumption helpers for declared uncertainty dimensions.
 *
 * Domain cardinality only. No cash arithmetic happens here: the backend
 * remains the sole authority for money and for every proof claim. Counts are
 * computed with arbitrary-precision integers because a Cartesian product can
 * far exceed JavaScript's exact integer range, and a rounded total must never
 * be presented as exact.
 */
import type { Uncertainty, Workspace } from "./types";

export const MAX_DIMENSIONS = 8;
export const MAX_CASES = 10000;
export const DEFAULT_TIME_LIMIT_SECONDS = 5;

/** Full ISO calendar date, including years below 100 and real month/day values. */
export function parseIsoDate(value: string): { year: number; month: number; day: number } | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) return null;
  const [year, month, day] = [Number(match[1]), Number(match[2]), Number(match[3])];
  if (year < 1 || month < 1 || month > 12 || day < 1) return null;
  // Date.UTC maps years 0-99 onto 1900-1999, so build the check explicitly.
  const leap = (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
  const lengths = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (day > lengths[month - 1]) return null;
  return { year, month, day };
}

/**
 * Proleptic Gregorian day ordinal, computed arithmetically rather than through
 * Date, so local time, DST and the year 0-99 remapping cannot shift a count.
 */
export function dayOrdinal(value: string): bigint | null {
  const parsed = parseIsoDate(value);
  if (!parsed) return null;
  const { year, month, day } = parsed;
  const shiftedMonth = month <= 2 ? month + 12 : month;
  const shiftedYear = BigInt(month <= 2 ? year - 1 : year);
  const era = (shiftedYear >= BigInt(0) ? shiftedYear : shiftedYear - BigInt(399)) / BigInt(400);
  const yearOfEra = shiftedYear - era * BigInt(400);
  const dayOfYear = BigInt(Math.floor((153 * (shiftedMonth - 3) + 2) / 5) + day - 1);
  const dayOfEra = yearOfEra * BigInt(365) + yearOfEra / BigInt(4) - yearOfEra / BigInt(100) + dayOfYear;
  return era * BigInt(146097) + dayOfEra;
}

/** Inclusive cardinality of one dimension; zero marks an invalid draft. */
export function dimensionSize(dimension: Uncertainty): bigint {
  if (dimension.kind === "approval") {
    const outcomes = new Set(dimension.outcomes);
    return outcomes.size === dimension.outcomes.length && [...outcomes].every(value => ["approved", "denied", "pending"].includes(value))
      ? BigInt(outcomes.size) : BigInt(0);
  }
  if (dimension.kind === "income_amount") {
    if (![dimension.minimum_cents, dimension.maximum_cents].every(value => Number.isSafeInteger(value) && value >= 0 && value <= 10000000000)) return BigInt(0);
    const span = BigInt(dimension.maximum_cents) - BigInt(dimension.minimum_cents) + BigInt(1);
    return span > BigInt(0) ? span : BigInt(0);
  }
  const earliest = dayOrdinal(dimension.earliest);
  const latest = dayOrdinal(dimension.latest);
  if (earliest === null || latest === null || latest < earliest) return BigInt(0);
  return latest - earliest + BigInt(1);
}

/** Exact product of the declared domains. Zero dimensions means one case. */
export function exactCaseCount(dimensions: Uncertainty[]): bigint {
  return dimensions.reduce((total, dimension) => total * dimensionSize(dimension), BigInt(1));
}

export function dimensionTarget(dimension: Uncertainty): string {
  return dimension.kind === "approval" ? dimension.target_id : dimension.event_id;
}

/** IDs of dimensions that redeclare a property already declared for a target. */
export function duplicateTargets(dimensions: Uncertainty[]): Set<string> {
  const seen = new Map<string, number>();
  const duplicates = new Set<string>();
  for (const dimension of dimensions) {
    const key = `${dimension.kind}:${dimensionTarget(dimension)}`;
    const count = (seen.get(key) ?? 0) + 1;
    seen.set(key, count);
    if (count > 1) duplicates.add(dimension.id);
  }
  return duplicates;
}

export function duplicateIds(dimensions: Uncertainty[]): Set<string> {
  const seen = new Set<string>();
  const duplicates = new Set<string>();
  for (const dimension of dimensions) {
    if (seen.has(dimension.id)) duplicates.add(dimension.id);
    seen.add(dimension.id);
  }
  return duplicates;
}

/** An invalid draft has no valid count and must not be submitted. */
export function draftBlockers(dimensions: Uncertainty[], workspace?: Workspace): string[] {
  const blockers: string[] = [];
  if (dimensions.length > MAX_DIMENSIONS) blockers.push(`At most ${MAX_DIMENSIONS} dimensions may be declared.`);
  if (duplicateTargets(dimensions).size) blockers.push("Each property of a target may be declared only once.");
  if (duplicateIds(dimensions).size) blockers.push("Dimension identifiers must be unique.");
  for (const dimension of dimensions) {
    if (!dimension.id.trim()) blockers.push("A dimension identifier is required.");
    if (!dimension.rationale.trim()) blockers.push(`${dimension.id}: a rationale is required.`);
    if (dimensionSize(dimension) === BigInt(0)) blockers.push(`${dimension.id}: the declared bounds are empty or invalid.`);
    if (workspace && dimension.kind === "approval") {
      const matches = workspace.scenario.actions.filter(action => action.id === dimension.target_id).length
        + workspace.rules.filter(rule => rule.id === dimension.target_id).length;
      if (matches !== 1) blockers.push(`${dimension.id}: choose an unambiguous known approval target.`);
    } else if (workspace && dimension.kind !== "approval") {
      const income = workspace.scenario.events.find(event => event.id === dimension.event_id);
      if (!income || income.direction !== "income" || income.kind !== "projected" || income.date < workspace.scenario.start_date) {
        blockers.push(`${dimension.id}: choose projected income on or after the horizon start.`);
      }
      if (dimension.kind === "income_date" && dimension.earliest < workspace.scenario.start_date) {
        blockers.push(`${dimension.id}: an income date cannot precede the horizon start.`);
      }
    }
  }
  return blockers;
}

/** Exact decimal string; the caller decides how to qualify a very large value. */
export function formatCaseCount(count: bigint): string {
  return count.toString();
}

export function exceedsSafeInteger(count: bigint): boolean {
  return count > BigInt(Number.MAX_SAFE_INTEGER);
}

export function overBudget(count: bigint, maxCases: number = MAX_CASES): boolean {
  return count > BigInt(maxCases);
}
