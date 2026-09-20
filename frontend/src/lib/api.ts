const API = process.env.NEXT_PUBLIC_API_URL || "";
export const SESSION_KEY = "clausegraph.session";

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = "ApiError";
  }
}

export async function request<T>(path: string, token?: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const response = await fetchWithTimeout(`${API}/api${path}`, { ...options, headers, cache: "no-store" });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    const message = typeof error.detail === "string" ? error.detail : JSON.stringify(error.detail);
    throw new ApiError(message || `Request failed (${response.status})`, response.status);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function requestBlob(path: string, token: string, options: RequestInit = {}): Promise<Blob> {
  const headers = new Headers(options.headers);
  headers.set("Authorization", `Bearer ${token}`);
  if (options.body) headers.set("Content-Type", "application/json");
  const response = await fetchWithTimeout(`${API}/api${path}`, { ...options, headers });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(typeof error.detail === "string" ? error.detail : "The file could not be created.");
  }
  return response.blob();
}

async function fetchWithTimeout(url: string, options: RequestInit): Promise<Response> {
  try { return await fetch(url, { ...options, signal: options.signal ?? AbortSignal.timeout(180_000) }); }
  catch (caught) {
    if (caught instanceof Error && caught.name === "TimeoutError") throw new Error("This request took too long. Please try again; your saved data is still available.");
    throw caught;
  }
}

export async function streamJob(token: string, id: string, signal: AbortSignal, onUpdate: (job: import("./types").JobStatus) => void) {
  const response = await fetch(`${API}/api/jobs/${encodeURIComponent(id)}/events`, { headers: { Authorization: `Bearer ${token}` }, signal, cache: "no-store" });
  if (!response.ok || !response.body) throw new Error("Live progress connection unavailable.");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    while (!signal.aborted) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true }).replaceAll("\r\n", "\n");
      let boundary = buffer.indexOf("\n\n");
      while (boundary >= 0) {
        const event = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        const data = event.split("\n").filter(line => line.startsWith("data:")).map(line => line.slice(5).trimStart()).join("\n");
        if (data) onUpdate(JSON.parse(data));
        boundary = buffer.indexOf("\n\n");
      }
    }
  } finally { reader.releaseLock(); }
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
