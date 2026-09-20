"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import * as Tabs from "@radix-ui/react-tabs";
import { ArrowRight, ArrowUpRight, AudioLines, CalendarDays, CheckCheck, ChevronDown, ChevronRight, CircleAlert, CircleCheck, ClipboardList, Download, FileText, GitBranch, Headphones, LayoutDashboard, LoaderCircle, LockKeyhole, Mic, Plus, RefreshCw, Settings2, ShieldCheck, SlidersHorizontal, Sparkles, Trash2, Upload, Wallet, X } from "lucide-react";
import { Badge, Button, Field, Modal } from "@/components/ui";
import UploadDialog from "@/components/upload-dialog";
import DraftDialog from "@/components/draft-dialog";
import IntakeDialog from "@/components/intake-dialog";
import EvidenceDrawer from "@/components/evidence-drawer";
import VerifyPlan from "@/components/verify-plan";
import SavedHistory from "@/components/saved-history";
import DecisionTracePanel from "@/components/decision-trace";
import ScenarioComparison from "@/components/scenario-comparison";
import OverviewMetrics from "@/components/overview-metrics";
import FactsReview from "@/components/facts-review";
import ReviewQueue from "@/components/review-queue";
import ActionCard from "@/components/action-card";
import { download, dollars, humanize, money, parseCents, request, requestBlob, SESSION_KEY, shortDate, streamJob } from "@/lib/api";
import type { Action, ConsequenceWalkthroughProps, DraftResponse, IntakeRequest, PlanRequest, PlanResult, ProviderStatus, RuleReview, SynthesisAdoptionResult, UploadResponse, VerificationResult, Workspace } from "@/lib/types";

const CashChart = dynamic(() => import("@/components/cash-chart"), { ssr: false, loading: () => <div className="cash-chart chart-loading"><LoaderCircle className="spin" /> Drawing your cash forecast…</div> });
const DependencyGraph = dynamic(() => import("@/components/dependency-graph"), { ssr: false, loading: () => <div className="graph-canvas chart-loading"><LoaderCircle className="spin" /> Connecting the evidence…</div> });

type Tab = "overview" | "documents" | "graph" | "history";
type Dialog = "intake" | "upload" | "settings" | "voice" | null;
type Comparison = { label: string; summary: string; result: PlanResult; actionId?: string };

/** Placeholder seam released to C14; C owns only this body and its import. */
function ConsequenceWalkthroughSlot(props: ConsequenceWalkthroughProps) {
  void props;
  return null;
}

export default function Home() {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleted, setDeleted] = useState(false);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [tab, setTab] = useState<Tab>("overview");
  const [dialog, setDialog] = useState<Dialog>(null);
  const [evidence, setEvidence] = useState<string[] | null>(null);
  const [draft, setDraft] = useState<DraftResponse | null>(null);
  const [verification, setVerification] = useState<VerificationResult | null>(null);
  const [cash, setCash] = useState("");
  const [approval, setApproval] = useState("recorded");
  const [incomeDate, setIncomeDate] = useState("");
  const [actionDate, setActionDate] = useState("");
  const [retryName, setRetryName] = useState<string | undefined>();
  const [audioConsent, setAudioConsent] = useState(false);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [transcript, setTranscript] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [graphFocus, setGraphFocus] = useState<string[]>([]);
  const booted = useRef(false);

  const onHistorySessionLost = useCallback((sessionId: string) => {
    if (localStorage.getItem(SESSION_KEY) !== sessionId) return;
    localStorage.removeItem(SESSION_KEY);
    setWorkspace(null); setVerification(null); setComparison(null); setEvidence(null); setDialog(null);
    setError("This private session is no longer available. Open a new session to continue.");
  }, []);

  const withPlan = useCallback(async (data: Workspace) => {
    if (!data.plan) data = { ...data, plan: await request<PlanResult>("/plan", data.session_id, { method: "POST", body: "{}" }) };
    setWorkspace(data);
    return data;
  }, []);

  const openSession = useCallback(async (demo: boolean, demo_variant: "baseline" | "resilient" = "baseline") => {
    const data = await request<Workspace>("/sessions", undefined, { method: "POST", body: JSON.stringify({ demo, demo_variant }) });
    localStorage.setItem(SESSION_KEY, data.session_id);
    setDeleted(false); setApproval("recorded"); setCash(""); setIncomeDate(""); setActionDate(""); setComparison(null);
    await withPlan(data);
  }, [withPlan]);

  useEffect(() => {
    if (booted.current) return;
    booted.current = true;
    async function initialize() {
      try {
        const token = localStorage.getItem(SESSION_KEY);
        if (token) await withPlan(await request<Workspace>("/workspace", token));
        else await openSession(true);
      } catch (caught) { setError(caught instanceof Error ? caught.message : "Could not reach the workspace."); }
      finally { setLoading(false); }
    }
    void initialize();
  }, [openSession, withPlan]);

  useEffect(() => {
    if (!workspace?.jobs?.some(job => job.status === "queued" || job.status === "running")) return;
    let active = true;
    const timer = window.setInterval(async () => {
      try {
        const data = await request<Workspace>("/workspace", workspace.session_id);
        if (!active) return;
        if (data.jobs?.every(job => job.status !== "queued" && job.status !== "running")) await withPlan(data);
        else setWorkspace(data);
      } catch (caught) { if (active) setError(caught instanceof Error ? caught.message : "Processing status could not be refreshed."); }
    }, 1800);
    return () => { active = false; window.clearInterval(timer); };
  }, [workspace?.session_id, workspace?.jobs, withPlan]);

  useEffect(() => () => { if (audioUrl) URL.revokeObjectURL(audioUrl); }, [audioUrl]);

  useEffect(() => { setVerification(current => current?.plan_id === workspace?.plan?.id && current?.revision === workspace?.revision ? current : null); }, [workspace?.session_id, workspace?.revision, workspace?.plan?.id]);
  useEffect(() => { setDraft(null); }, [workspace?.session_id, workspace?.revision]);
  useEffect(() => {
    if (comparison && workspace && comparison.result.revision !== workspace.revision) setComparison(null);
  }, [comparison, workspace]);
  useEffect(() => { if (!comparison) setGraphFocus([]); }, [comparison]);

  const pendingJobIds = (workspace?.jobs ?? []).filter(job => job.status === "queued" || job.status === "running").map(job => job.id).sort().join(",");
  useEffect(() => {
    if (!workspace?.session_id || !pendingJobIds) return;
    const controller = new AbortController();
    for (const id of pendingJobIds.split(",")) {
      void streamJob(workspace.session_id, id, controller.signal, job => {
        setWorkspace(current => current ? { ...current, jobs: (current.jobs ?? []).map(item => item.id === job.id ? job : item) } : null);
        if (job.status === "completed" || job.status === "failed") {
          void request<Workspace>("/workspace", workspace.session_id).then(withPlan).catch(caught => setError(caught instanceof Error ? caught.message : "Could not refresh processed document."));
        }
      }).catch(() => { /* Polling remains active when a stream closes or reconnects. */ });
    }
    return () => controller.abort();
  }, [workspace?.session_id, pendingJobIds, withPlan]);

  const savedAssumptions = workspace?.plan?.assumptions;
  const shiftId = workspace?.scenario.actions.find(action => action.kind === "shift")?.id;
  useEffect(() => {
    setCash(savedAssumptions?.opening_balance_cents != null ? dollars(savedAssumptions.opening_balance_cents) : "");
    setIncomeDate(savedAssumptions?.income_date ?? "");
    setActionDate(shiftId ? savedAssumptions?.action_dates?.[shiftId] ?? "" : "");
    setApproval(shiftId ? savedAssumptions?.approval_overrides?.[shiftId] ?? "recorded" : "recorded");
  }, [savedAssumptions, shiftId]);

  async function run(label: string, operation: () => Promise<void>) {
    setBusy(label); setError(""); setNotice("");
    try { await operation(); } catch (caught) { setError(caught instanceof Error ? caught.message : "Something went wrong. Please try again."); }
    finally { setBusy(""); }
  }

  async function saveIntake(value: IntakeRequest) {
    if (!workspace) return;
    const data = await request<Workspace>("/intake", workspace.session_id, { method: "POST", body: JSON.stringify(value) });
    await withPlan(data); setComparison(null); setCash(""); setNotice("Financial picture updated. Your plan has been recalculated.");
  }

  async function saveReview(id: string, review: RuleReview) {
    if (!workspace) return;
    const data = await request<Workspace>(`/rules/${encodeURIComponent(id)}`, workspace.session_id, { method: "PATCH", body: JSON.stringify(review) });
    await withPlan(data); setComparison(null); setApproval("recorded"); setNotice("Review recorded. Your plan now reflects the updated evidence and approval.");
  }

  function scenarioRequest(): PlanRequest {
    if (!workspace) return { include_conditional: false };
    const shift = workspace.scenario.actions.find(action => action.kind === "shift");
    return { include_conditional: false, ...(cash ? { opening_balance_cents: parseCents(cash) } : {}), ...(incomeDate ? { income_date: incomeDate } : {}), ...(shift && actionDate ? { action_dates: { [shift.id]: actionDate } } : {}), ...(shift && approval !== "recorded" ? { approval_overrides: Object.fromEntries([shift.id, ...workspace.rules.filter(rule => shift.source_rule_ids.includes(rule.id) && rule.approval_status !== "not_required").map(rule => rule.id)].map(id => [id, approval as "approved" | "denied" | "pending"])), include_conditional: approval === "approved" } : {}) };
  }

  async function calculate() {
    if (!workspace) return;
    const body = scenarioRequest();
    const result = await request<PlanResult>("/plan", workspace.session_id, { method: "POST", body: JSON.stringify(body) });
    setWorkspace({ ...workspace, plan: result });
    setComparison(null);
    setNotice("Scenario recalculated using your selected assumptions.");
  }

  async function previewScenario() {
    if (!workspace) return;
    const body = scenarioRequest();
    const changed = [cash ? `Available cash ${money(body.opening_balance_cents ?? 0)}` : "", approval !== "recorded" ? `Payment extension ${approval}` : "", actionDate ? `Action date ${shortDate(actionDate)}` : "", incomeDate ? `Income date ${shortDate(incomeDate)}` : ""].filter(Boolean);
    const result = await request<PlanResult>("/plan/preview", workspace.session_id, { method: "POST", body: JSON.stringify(body) });
    setGraphFocus([]);
    setComparison({ label: "Scenario preview", summary: changed.join(" · ") || "Current scenario controls", result });
    setNotice("Scenario previewed safely. Your recorded plan has not changed.");
  }

  async function previewAction(action: Action) {
    if (!workspace?.plan) return;
    const assumptions = workspace.plan.assumptions;
    const body: PlanRequest = {
      ...assumptions,
      include_conditional: assumptions?.include_conditional ?? false,
      force_action_ids: [action.id],
      exclude_action_ids: workspace.scenario.actions.filter(item => item.id !== action.id).map(item => item.id),
    };
    const result = await request<PlanResult>("/plan/preview", workspace.session_id, { method: "POST", body: JSON.stringify(body) });
    setGraphFocus([]);
    setComparison({ label: action.title, summary: `${action.title} is the only option applied`, result, actionId: action.id });
    setNotice(`${action.title} previewed safely. Your recorded plan has not changed.`);
  }

  async function applyComparison() {
    if (!workspace || !comparison) return;
    const result = await request<PlanResult>("/plan", workspace.session_id, { method: "POST", body: JSON.stringify(comparison.result.assumptions) });
    setWorkspace({ ...workspace, plan: result });
    setComparison(null);
    setNotice("The preview is now your recorded plan. No request, payment, or cancellation was executed.");
  }

  function adoptSchedule(value: SynthesisAdoptionResult) {
    if (!workspace?.plan) return;
    const source = workspace;
    setWorkspace(current => current?.session_id === source.session_id && current.revision === source.revision && current.plan?.id === source.plan?.id
      ? { ...current, plan: value.plan } : current);
    setVerification(value.verification);
    setComparison(null);
    setNotice("Verified fixed schedule adopted with its saved proof. No external action was executed.");
  }

  function openUpload(name?: string) { setRetryName(name); setDialog("upload"); }

  async function uploaded(response: UploadResponse) {
    if (!workspace) return;
    await withPlan(await request<Workspace>("/workspace", workspace.session_id));
    setDialog(null); setTab("documents"); setRetryName(undefined);
    setNotice(response.job?.status === "queued" || response.job?.status === "running"
      ? "Document processing is queued or running. Review the extracted facts when it finishes."
      : response.duplicate ? "This document is already in your workspace. No duplicate was created."
      : "Document stored without external processing. Readable native text is available for review.");
  }

  const plan = workspace?.plan;
  const currentVerification = verification && verification.plan_id === plan?.id && verification.revision === workspace?.revision ? verification : null;
  const shift = workspace?.scenario.actions.find(action => action.kind === "shift");
  const pendingReviews = workspace?.rules.filter(rule => rule.review_status !== "reviewed").length || 0;
  const isProtected = plan && plan.proposed.minimum_balance_cents >= 0 && plan.state === "confirmed";


  return <div className="app-shell">
    <aside className="sidebar"><Link className="brand" href="/" aria-label="ClauseGraph home"><span className="brand-mark"><GitBranch size={24} strokeWidth={2.1} /></span><span>Clause<span className="brand-light">Graph</span><small>BOUNDED PLAN VERIFICATION</small></span></Link><div className="workspace-switch"><span className="workspace-avatar">P</span><div>Personal workspace<small>Financial recovery</small></div><ChevronDown size={14} /></div><div className="nav-label">WORKSPACE</div><nav><button className={tab === "overview" ? "nav-item active" : "nav-item"} onClick={() => setTab("overview")}><LayoutDashboard size={18} /> Overview<span className="nav-active-dot" /></button><button className={tab === "documents" ? "nav-item active" : "nav-item"} onClick={() => setTab("documents")}><FileText size={18} /> Your documents{workspace && <span className="nav-count">{workspace.documents.length}</span>}</button><button className={tab === "graph" ? "nav-item active" : "nav-item"} onClick={() => setTab("graph")}><GitBranch size={18} /> Dependency graph</button><button className={tab === "history" ? "nav-item active" : "nav-item"} onClick={() => setTab("history")}><ClipboardList size={18} /> History</button><button className="nav-item" disabled={!workspace} onClick={() => setDialog("intake")}><Wallet size={18} /> Financial picture</button></nav><div className="sidebar-note"><div className="sidebar-note-icon"><ShieldCheck size={21} /></div><h3>Your essentials come first.</h3><p>Every option is checked against the expenses you need to protect.</p><button onClick={() => setDialog("intake")} disabled={!workspace}>Review essentials <ArrowRight size={14} /></button></div><div className="sidebar-bottom"><button className="nav-item" disabled={!workspace} onClick={() => setDialog("settings")}><Settings2 size={18} /> Settings & privacy</button><div className="profile"><div className="profile-avatar">Y</div><div>Your workspace<small><span className="status-dot" /> Private session</small></div><LockKeyhole size={15} /></div></div></aside>
    <main className="main"><header className="topbar"><div className="breadcrumb">Workspace <ChevronRight size={13} /> <span>{tab === "overview" ? "Overview" : tab === "documents" ? "Your documents" : tab === "history" ? "History" : "Dependency graph"}</span></div><div className="topbar-right"><span className="private-label"><LockKeyhole size={13} /> Private by design</span>{workspace?.mode === "synthetic" && <Badge tone="warning"><span className="mini-dot" /> Synthetic demo</Badge>}<button className="top-avatar" aria-label="Open settings" onClick={() => setDialog("settings")} disabled={!workspace}>Y</button></div></header>
      <div className="page-content">
        <div className="page-heading"><div><div className="eyebrow page-eyebrow">A LITTLE CLARITY. A WAY FORWARD.</div><h1>{tab === "overview" ? "Your recovery plan" : tab === "documents" ? "The evidence behind your plan" : tab === "history" ? "Your saved calculations" : "See how it all connects"}</h1><p>{tab === "overview" ? "Understand your options. Protect what matters. Take the next step." : tab === "documents" ? "Your documents, extracted facts, and the fine print that changes the picture." : tab === "history" ? "Inspect past plans and fixed-plan checks, with their original assumptions." : "Follow the relationships between documents, clauses, actions, and your cash."}</p></div><Button variant="primary" disabled={!workspace || !!busy} onClick={() => openUpload()}><Plus size={17} /> Add documents</Button></div>
        {workspace?.mode === "synthetic" && <div className="demo-strip"><Sparkles size={15} /><span>You’re exploring {workspace.demo_variant === "resilient" ? "the resilient-plan" : "the original"} synthetic example. Its {workspace.demo_variant === "resilient" ? "three" : "six"} fixture documents and starting financial details are fictional.</span><button onClick={() => void run("new", () => openSession(false))} disabled={!!busy}>Start my own plan <ArrowRight size={13} /></button><button disabled={!!busy} onClick={() => void run("demo", () => openSession(true, workspace.demo_variant === "resilient" ? "baseline" : "resilient"))}>{workspace.demo_variant === "resilient" ? "Open original example" : "Open resilient example"}</button></div>}
        {error && <div className="alert error-alert" role="alert"><CircleAlert size={18} /><div><strong>Something needs attention</strong><p>{error}</p></div><button aria-label="Dismiss error" className="icon-button" onClick={() => setError("")}><X size={16} /></button></div>}
        {notice && <div className="notice" role="status"><CircleCheck size={15} /><span>{notice}</span><button aria-label="Dismiss notification" className="icon-button" onClick={() => setNotice("")}><X size={14} /></button></div>}
        {loading ? <div className="loading-workspace"><span className="loading-logo"><GitBranch size={32} /></span><h2>Connecting the dots…</h2><p>Opening your clearly labeled synthetic demo.</p><LoaderCircle className="spin" size={20} /></div> : !workspace ? <div className="welcome-card"><div className="large-icon"><ShieldCheck size={28} /></div><h2>{deleted ? "Your session has been deleted" : "Let’s find your next step"}</h2><p>{deleted ? "Your documents, extracted rules, and financial data were removed from this session." : "Open the synthetic example or start a private plan with your own financial picture."}</p><div className="button-row"><Button variant="primary" busy={busy === "new"} onClick={() => void run("new", () => openSession(false))}>Start a new plan</Button><Button busy={busy === "demo"} onClick={() => void run("demo", () => openSession(true))}>Explore synthetic demo</Button></div></div> : <>
          <Tabs.Root value={tab} onValueChange={value => setTab(value as Tab)}><Tabs.List className="workspace-tabs" aria-label="Workspace views"><Tabs.Trigger value="overview"><LayoutDashboard size={15} /> Overview</Tabs.Trigger><Tabs.Trigger value="documents"><FileText size={15} /> Documents & facts <span>{workspace.documents.length}</span></Tabs.Trigger><Tabs.Trigger value="graph"><GitBranch size={15} /> Dependency graph</Tabs.Trigger><Tabs.Trigger value="history"><ClipboardList size={15} /> History</Tabs.Trigger><div className="tab-meta"><span className="status-dot" /> {workspace.mode === "synthetic" ? "Demo ready" : "Session active"}<span className="dot-separator">·</span> USD</div></Tabs.List>
          <Tabs.Content value="overview" className="tab-content">
          {!workspace.scenario.events.length && <div className="onboarding-card"><div className="large-icon"><Wallet size={24} /></div><div><h2>Start with what you have today.</h2><p>Add cash, expected income, and your essential bills to calculate a useful plan.</p></div><Button variant="primary" onClick={() => setDialog("intake")}>Set up my financial picture <ArrowRight size={15} /></Button></div>}
          <ReviewQueue key={`${workspace.session_id}:${workspace.revision}`} workspace={workspace} onEvidence={setEvidence} onIntake={() => setDialog("intake")} onUpload={() => openUpload()} onRefresh={async () => { await withPlan(await request<Workspace>("/workspace", workspace.session_id)); }} />
          {plan ? <>{!!plan.assumptions?.force_action_ids?.length && <div className="notice"><SlidersHorizontal size={15} /><span>Recorded plan uses: {plan.assumptions.force_action_ids.map(id => workspace.scenario.actions.find(action => action.id === id)?.title || id).join(", ")}.</span><Button variant="ghost" onClick={() => void run("calculate", calculate)}>Return to recommended plan</Button></div>}<OverviewMetrics workspace={workspace} plan={plan} onIntake={() => setDialog("intake")} />
          <DecisionTracePanel plan={plan} workspace={workspace} onEvidence={setEvidence} />
          {comparison && <ScenarioComparison active={plan} candidate={comparison.result} label={comparison.label} summary={comparison.summary} workspace={workspace} busy={busy === "apply-comparison"} onClose={() => setComparison(null)} onApply={() => void run("apply-comparison", applyComparison)} />}
          {/* RELEASED TO C14 — c-consequence-walkthrough. C may replace only the
              placeholder body/import and this mounted call while preserving props/state. */}
          {comparison?.actionId && <div data-testid="consequence-walkthrough-slot" className="consequence-walkthrough-slot"><ConsequenceWalkthroughSlot workspace={workspace} recorded={plan} candidate={comparison.result} actionId={comparison.actionId} onEvidence={setEvidence} onGraph={ruleIds => { setGraphFocus([...new Set(ruleIds)]); setTab("graph"); }} /></div>}
          <div className="dashboard-grid"><div className="dashboard-main"><section className="panel chart-panel"><div className="panel-heading"><div><h2>Your cash, with a plan</h2><p>A day-by-day view of the path ahead.</p></div><div className="period-pill"><CalendarDays size={13} />{shortDate(workspace.scenario.start_date)} – {plan.proposed.daily.length ? shortDate(plan.proposed.daily[plan.proposed.daily.length - 1].date) : "—"}</div></div><div className="chart-legend"><span><i className="legend-line proposed" /> Saved plan (nominal case)</span><span><i className="legend-line baseline" /> Current path</span>{currentVerification?.counterexample?.simulation && <span><i className="legend-line counterexample" /> Counterexample</span>}<span className="projection-label">All future balances are projections</span></div><CashChart plan={plan} verification={currentVerification} /><div className={`chart-insight ${plan.proposed.minimum_balance_cents < 0 ? "insight-warning" : ""}`}><span className="insight-icon">{isProtected ? <ShieldCheck size={18} /> : <CircleAlert size={18} />}</span><p>{isProtected ? <>The saved schedule keeps daily cash nonnegative in the nominal case.<span> Essential expenses remain included throughout the horizon.</span></> : plan.state === "conditional" ? <>This scenario relies on approval assumptions.<span> Confirm them before using it as your plan.</span></> : plan.state === "unresolved" && plan.proposed.minimum_balance_cents >= 0 ? <>Cash stays nonnegative, but evidence is unresolved.<span> Review flagged facts before relying on this plan.</span></> : <>A cash gap remains{plan.proposed.first_shortfall_date ? ` from ${shortDate(plan.proposed.first_shortfall_date)}` : ""}.<span> {money(plan.proposed.additional_cash_required_cents)} additional cash is required; this is a diagnostic, not available funding.</span></>}</p></div></section>
          <VerifyPlan key={`${workspace.session_id}:${workspace.revision}:${plan.id}`} workspace={workspace} plan={plan} result={currentVerification} onResult={setVerification} onEvidence={setEvidence} onAdopt={adoptSchedule} onSessionLost={onHistorySessionLost} scenarioDraftKey={JSON.stringify([cash, approval, incomeDate, actionDate])} />
          <section className="actions-section"><div className="section-heading"><div><h2>Your next moves <span className="count-pill">{plan.actions.length}</span></h2><p>In the right order, with the reasoning behind each one.</p></div><button className="text-button" onClick={() => setTab("graph")}>Explore connections <ArrowUpRight size={14} /></button></div><div className="action-list">{[...workspace.scenario.actions].sort((a, b) => (plan.actions.find(item => item.action_id === a.id)?.order ?? 999) - (plan.actions.find(item => item.action_id === b.id)?.order ?? 999)).map((action, index) => <ActionCard key={action.id} action={action} plan={plan} comparing={busy === `compare-${index}`} drafting={busy === `draft-${index}`} onEvidence={setEvidence} onCompare={() => void run(`compare-${index}`, () => previewAction(action))} onDraft={() => void run(`draft-${index}`, async () => setDraft(await request<DraftResponse>(`/actions/${encodeURIComponent(action.id)}/draft`, workspace.session_id, { method: "POST" })))} />)}</div>{!workspace.scenario.actions.length && <div className="empty-small">Add your documents to find evidence-backed options. Your existing income and expenses already appear in the cash forecast.</div>}</section>
          {!!plan.proposed.beyond_horizon?.length && <section className="panel future-panel"><div className="panel-heading"><div><h2>Still on the horizon</h2><p>These obligations remain yours after the plan ends.</p></div><CalendarDays size={18} /></div>{plan.proposed.beyond_horizon.map(event => <div className="future-row" key={event.id}><div><strong>{event.title}</strong><small>{shortDate(event.date)} · {humanize(event.kind || "projected")}</small></div><span>{money(event.amount_cents)}</span></div>)}</section>}
          </div><aside className="dashboard-aside"><section className="panel plan-summary"><div className="section-title"><h3>Plan snapshot</h3><span className={`status-orb ${isProtected ? "green-orb" : "amber-orb"}`} /></div><div className="summary-status"><ShieldCheck size={18} /><span>{isProtected ? "A steadier path forward" : plan.state === "conditional" ? "Conditional scenario" : "Your plan needs attention"}</span></div><div className="summary-line"><span>Plan status</span><Badge tone={isProtected ? "success" : "warning"}>{humanize(plan.state)}</Badge></div><div className="summary-line"><span>Recommended actions</span><strong>{plan.actions.length}</strong></div><div className="summary-line"><span>Facts to review</span><button onClick={() => setTab("documents")}>{pendingReviews} <ChevronRight size={12} /></button></div><div className="summary-line"><span>Protected services</span><strong>{workspace.scenario.essential_service_ids?.length || 0}</strong></div><div className="solver-note"><CheckCheck size={13} /><span>{plan.solver_status === "FIXED_VERIFIED" ? "Verified fixed schedule · no optimum claimed" : plan.solver_status === "OPTIMAL" && plan.objective_proven ? "Nominal optimum proven" : `${plan.solver_status} · ${plan.objective_proven ? "Objective proven" : "Optimality not proven"}`}<small>{plan.solver_status !== "FIXED_VERIFIED" && `${plan.solver_wall_time_seconds.toFixed(3)}s · `}Revision {plan.revision}</small></span></div><Button className="full-width" busy={busy === "export"} onClick={() => void run("export", async () => download(await requestBlob("/evidence/export", workspace.session_id), "clausegraph-evidence.md"))}><Download size={15} /> Download evidence summary</Button></section>
          <section className="panel scenario-panel"><div className="section-title"><h3><SlidersHorizontal size={16} /> What if things change?</h3><Badge tone="blue">Scenario</Badge></div><p className="helper">Explore changes and recalculate the consequences.</p><form onSubmit={event => { event.preventDefault(); void run("calculate", calculate); }}><Field label="Available cash (USD)"><div className="input-prefix"><span>$</span><input aria-label="Scenario available cash" inputMode="decimal" value={cash} placeholder={dollars(workspace.scenario.opening_balance_cents)} onChange={event => setCash(event.target.value)} /></div></Field>{shift && <><Field label="Payment extension approval"><select aria-label="Payment extension approval assumption" value={approval} onChange={event => setApproval(event.target.value)}><option value="recorded">Use recorded approval</option><option value="approved">Assume approved · conditional</option><option value="pending">Assume still pending</option><option value="denied">Assume denied</option></select></Field><Field label="Action execution date" hint="Must fall within the allowed action window."><input type="date" aria-label="Action execution date" min={shift.earliest_date} max={shift.latest_date} value={actionDate} onChange={event => setActionDate(event.target.value)} /></Field></>}{workspace.scenario.events.some(event => event.direction === "income") && <Field label="Expected income date"><input type="date" aria-label="Expected income date" value={incomeDate} onChange={event => setIncomeDate(event.target.value)} /></Field>}<Button className="full-width" type="button" busy={busy === "preview-scenario"} onClick={() => void run("preview-scenario", previewScenario)}><SlidersHorizontal size={14} /> Preview side by side</Button><Button className="full-width" variant="primary" type="submit" busy={busy === "calculate"}><RefreshCw size={14} /> Save as recorded plan</Button></form><p className="scenario-foot"><LockKeyhole size={12} /> Nothing is submitted or executed.</p></section>
          <section className="listen-card"><span><Headphones size={20} /></span><div><h3>A little easier to take in.</h3><p>Listen to your action checklist or record your financial picture.</p><button onClick={() => setDialog("voice")}>Open audio tools <ArrowRight size={13} /></button></div></section></aside></div>
          {(plan.warnings?.length ?? 0) > 0 && <div className="plan-warnings"><h3><CircleAlert size={15} /> Things to keep in mind</h3>{plan.warnings?.map((warning, index) => <p key={index}>{warning}</p>)}</div>}</> : <div className="panel loading-plan"><LoaderCircle size={19} className="spin" /><p>Your plan is being updated as evidence is processed.</p><Button onClick={() => void run("calculate", calculate)}>Recalculate now</Button></div>}
          </Tabs.Content>
          <Tabs.Content value="documents" className="tab-content"><div className="documents-heading"><div><h2>Your document library <span className="count-pill">{workspace.documents.length}</span></h2><p>Source text stays separate from reviewed facts and third-party approvals.</p></div><Button onClick={() => openUpload()}><Upload size={15} /> Upload document</Button></div><div className="document-grid">{workspace.documents.map(document => { const rules = workspace.rules.filter(rule => rule.evidence.some(source => source.document_id === document.id)); const job = workspace.jobs?.find(item => item.document_id === document.id); return <article className="document-card" key={document.id}><div className="document-card-top"><span className="document-icon"><FileText size={24} /></span><Badge tone={document.status === "ready" ? "success" : document.status === "failed" ? "danger" : "warning"}>{humanize(document.status)}</Badge></div><h3>{document.name}</h3><p>{document.pages?.length || 0} pages · Version {document.version}{document.synthetic && " · Synthetic"}</p>{job && job.status !== "completed" && <div className={`job-status ${job.status === "failed" ? "job-failed" : ""}`}><span>{job.status === "failed" ? <CircleAlert size={13} /> : <LoaderCircle size={13} className="spin" />}{humanize(job.stage)} · {job.progress}%</span><progress value={job.progress} max={100} />{job.error && <p role="alert">{job.error}</p>}</div>}{document.error && <p className="text-red">{document.error}</p>}{(document.status === "failed" || job?.status === "failed") && <Button disabled={!!busy} onClick={() => openUpload(document.name)}><RefreshCw size={14} /> Retry processing</Button>}<div className="document-card-footer"><button className="text-button" onClick={() => setEvidence(rules.map(rule => rule.id))}>{rules.length} extracted facts <ArrowRight size={13} /></button><button className="icon-button" aria-label={`Delete ${document.name}`} onClick={() => { if (window.confirm(`Delete ${document.name}? This also clears all saved plan and verification history in this session; essential obligations remain.`)) void run("delete-document", async () => { await request(`/documents/${encodeURIComponent(document.id)}`, workspace.session_id, { method: "DELETE" }); await withPlan(await request<Workspace>("/workspace", workspace.session_id)); }); }}><Trash2 size={14} /></button></div></article>; })}<button className="document-upload-card" onClick={() => openUpload()}><span><Plus size={24} /></span><strong>Add another piece of the picture</strong><p>Bills, contracts, or benefit documents</p><small>PDF, TXT, or CSV</small></button></div><FactsReview workspace={workspace} onEvidence={setEvidence} /></Tabs.Content>
          <Tabs.Content value="graph" className="tab-content"><section className="panel graph-panel"><div className="panel-heading"><div><h2>The bigger picture</h2><p>Click any clause or connection to inspect its evidence. Drag to explore; scroll to zoom.</p></div><Badge tone="blue">{workspace.graph.nodes?.length ?? 0} connections of context</Badge></div>{!!graphFocus.length && <div className="graph-focus-note" role="status">Highlighting the {graphFocus.length} rule{graphFocus.length === 1 ? "" : "s"} behind the selected consequence.<button className="text-button" onClick={() => setGraphFocus([])}>Clear highlight</button></div>}<div className="graph-legend"><span><i style={{ background: "#b9cafa" }} /> Documents</span><span><i style={{ background: "#a9d9c6" }} /> Rules</span><span><i style={{ background: "#eed09b" }} /> Actions</span><span><i style={{ background: "#bfc9df" }} /> Cash events</span></div><DependencyGraph graph={workspace.graph} onEvidence={setEvidence} highlightRuleIds={graphFocus} /></section>{workspace.graph.issues?.map((issue, index) => <div className="alert graph-issue" key={index}><CircleAlert size={18} /><div><strong>{humanize(issue.code)}</strong><p>{issue.message}</p></div><button className="text-button" onClick={() => setEvidence(issue.rule_ids ?? [])}>Review evidence <ArrowRight size={14} /></button></div>)}</Tabs.Content><Tabs.Content value="history" className="tab-content">{busy ? <p role="status">Workspace operation in progress. Saved history is cleared until it finishes.</p> : <SavedHistory key={`${workspace.session_id}:${workspace.revision}:${workspace.plan?.id ?? "none"}`} workspace={workspace} onSessionLost={onHistorySessionLost} />}</Tabs.Content></Tabs.Root>
          <footer className="page-footer"><span><GitBranch size={14} /> Evidence in. Clarity out.</span><span>Planning support · You remain in control of every action.</span></footer>
        </>}
      </div>
    </main>
    {workspace && dialog === "intake" && <IntakeDialog scenario={workspace.scenario} onClose={() => setDialog(null)} onSave={saveIntake} />}
    {workspace && evidence && <EvidenceDrawer ruleIds={evidence} workspace={workspace} onClose={() => setEvidence(null)} onSave={saveReview} />}
    {workspace && dialog === "upload" && <UploadDialog key={workspace.session_id} token={workspace.session_id} retryName={retryName} onClose={() => setDialog(null)} onUploaded={uploaded} onBusyChange={value => { setBusy(value ? "upload" : ""); if (value) { setError(""); setNotice(""); } }} />}
    {workspace && draft && <DraftDialog key={`${workspace.session_id}:${workspace.revision}:${draft.action_id}`} token={workspace.session_id} initial={draft} onClose={() => setDraft(null)} onCopied={() => { setNotice("Draft copied. Nothing has been sent."); setDraft(null); }} />}
    {workspace && dialog === "voice" && <Modal open onClose={() => setDialog(null)} title="Your plan, in your own time" description="Optional audio tools powered by ElevenLabs. Financial facts always need your confirmation."><div className="dialog-body"><label className="consent-box"><input type="checkbox" checked={audioConsent} onChange={event => setAudioConsent(event.target.checked)} /><span>I consent to external audio processing.<small>Your audio or action checklist will be sent to ElevenLabs for this request.</small></span></label><h3 className="audio-section-title"><Headphones size={18} /> Listen to the checklist</h3><p className="helper">Hear the actions and conditions in your current plan.</p><Button disabled={!audioConsent} busy={busy === "audio"} onClick={() => void run("audio", async () => { const blob = await requestBlob("/audio/checklist", workspace.session_id, { method: "POST", body: JSON.stringify({ consent: true }) }); setAudioUrl(URL.createObjectURL(blob)); })}><AudioLines size={16} /> Generate spoken checklist</Button>{audioUrl && <audio className="audio-player" controls src={audioUrl} />}<hr /><h3 className="audio-section-title"><Mic size={18} /> Spoken intake</h3><p className="helper">Upload a voice recording. Review the transcript, then enter verified amounts in your financial picture.</p><input type="file" accept="audio/*" aria-label="Voice recording" onChange={event => setAudioFile(event.target.files?.[0] || null)} /><Button disabled={!audioConsent || !audioFile} busy={busy === "transcribe"} onClick={() => void run("transcribe", async () => { const form = new FormData(); form.append("file", audioFile!); form.append("consent", "true"); const result = await request<{ text: string; facts_confirmed: false }>("/audio/transcribe", workspace.session_id, { method: "POST", body: form }); setTranscript(result.text); })}><Mic size={15} /> Transcribe recording</Button>{transcript && <div className="transcript"><Badge tone="warning">Unconfirmed financial facts</Badge><p>{transcript}</p><Button onClick={() => setDialog("intake")}>Review & enter confirmed facts <ArrowRight size={14} /></Button></div>}{error && <div className="inline-error" role="alert">{error}</div>}</div></Modal>}
    {workspace && dialog === "settings" && <Modal open onClose={() => { setDialog(null); setConfirmDelete(false); }} title="Settings & privacy" description="Your session, your data, your choice."><div className="dialog-body"><div className="privacy-note"><ShieldCheck size={20} /><p>Documents and financial details are isolated to this browser’s private session token. Keep access to this browser private.</p></div><div className="section-title"><h3>Connected services</h3><Button variant="ghost" busy={busy === "providers"} onClick={() => void run("providers", async () => { const providers = await request<ProviderStatus[]>("/providers", workspace.session_id); setWorkspace({ ...workspace, providers }); })}><RefreshCw size={14} /> Refresh</Button></div>{workspace.providers?.map(provider => <div className="provider-row" key={provider.name}><div><strong>{provider.name}</strong><p>{provider.detail}</p>{provider.model && <small>{provider.model}</small>}</div><Badge tone={provider.mode === "live" ? "success" : "neutral"}>{provider.mode}</Badge></div>)}<p className="helper">Configuration does not prove a successful live call. Synthetic documents are never presented as live provider results.</p><hr />{workspace.mode === "synthetic" && <div className="setting-action"><div><h3>Reset synthetic demo</h3><p>Clear saved history and restore this {workspace.demo_variant === "resilient" ? "three-document resilient" : "original six-document"} synthetic example.</p></div><Button busy={busy === "reset"} onClick={() => void run("reset", async () => { if (!window.confirm("Reset this session to its starting synthetic example? Current documents, changes, and all saved history will be replaced.")) return; await withPlan(await request<Workspace>("/demo/reset", workspace.session_id, { method: "POST" })); setApproval("recorded"); setCash(""); setIncomeDate(""); setActionDate(""); setDialog(null); })}><RefreshCw size={15} /> Reset</Button></div>}<div className="setting-action"><div><h3>Delete this session</h3><p>Remove its documents, rules, jobs, financial data, and all saved history.</p></div><Button variant="danger" onClick={() => setConfirmDelete(true)}><Trash2 size={15} /> Delete</Button></div>{confirmDelete && <div className="delete-confirm"><strong>Permanently delete all data in this session?</strong><p>This cannot be undone.</p><Button variant="danger" busy={busy === "delete"} onClick={() => void run("delete", async () => { await request("/session", workspace.session_id, { method: "DELETE" }); localStorage.removeItem(SESSION_KEY); setWorkspace(null); setDialog(null); setConfirmDelete(false); setDeleted(true); })}>Delete session permanently</Button></div>}{error && <div className="inline-error" role="alert">{error}</div>}</div></Modal>}
  </div>;
}
