const API = process.env.NEXT_PUBLIC_API_URL || "";
export const SESSION_KEY = "clausegraph.session";

export async function request<T>(path: string, token?: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const response = await fetch(`${API}/api${path}`, { ...options, headers, cache: "no-store" });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    const message = typeof error.detail === "string" ? error.detail : JSON.stringify(error.detail);
    throw new Error(message || `Request failed (${response.status})`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function requestBlob(path: string, token: string, options: RequestInit = {}): Promise<Blob> {
  const headers = new Headers(options.headers);
  headers.set("Authorization", `Bearer ${token}`);
  if (options.body) headers.set("Content-Type", "application/json");
  const response = await fetch(`${API}/api${path}`, { ...options, headers });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(typeof error.detail === "string" ? error.detail : "The file could not be created.");
  }
  return response.blob();
}

export function download(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function money(cents: number, decimals = false) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", minimumFractionDigits: decimals ? 2 : 0, maximumFractionDigits: 2 }).format(cents / 100);
}

export function dollars(cents: number) { return (cents / 100).toFixed(2); }

export function parseCents(value: string): number {
  if (!/^\d+(\.\d{1,2})?$/.test(value.trim())) throw new Error("Enter a positive USD amount with at most two decimal places.");
  const [whole, fraction = ""] = value.trim().split(".");
  const cents = Number(whole) * 100 + Number(fraction.padEnd(2, "0"));
  if (!Number.isSafeInteger(cents)) throw new Error("This amount is too large.");
  return cents;
}

export function shortDate(date: string) {
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", timeZone: "UTC" }).format(new Date(`${date.slice(0, 10)}T12:00:00Z`));
}

export function humanize(value: string) { return value.replaceAll("_", " "); }
