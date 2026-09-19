"use client";

import { useEffect, useState } from "react";
import { ArrowRight, CircleAlert, ClipboardList, FileText, LoaderCircle } from "lucide-react";
import { Badge, Button } from "./ui";
import { humanize, request } from "@/lib/api";
import type { ReviewQueue as Queue, ReviewQueueItem, Workspace } from "@/lib/types";

type Props = {
  workspace: Workspace;
  onEvidence: (ids: string[]) => void;
  onIntake: () => void;
  onUpload: () => void;
  onRefresh: () => Promise<void>;
};

function ReviewItem({ item, first, workspace, onEvidence, onIntake, onUpload }: Omit<Props, "onRefresh"> & { item: ReviewQueueItem; first: boolean }) {
  const availableRules = item.rule_ids.filter(id => workspace.rules.some(rule => rule.id === id));
  const actions = item.action_ids.map(id => workspace.scenario.actions.find(action => action.id === id)?.title ?? id);
  return <article className={`review-queue-item ${first ? "review-queue-next" : ""}`} data-testid={`review-item-${item.id}`}>
    <div className="review-queue-item-heading">
      <div>{first && <span className="eyebrow">Next to inspect</span>}<h3>{item.title}</h3></div>
      <Badge tone={item.disposition === "blocked" ? "danger" : "warning"}>{item.disposition === "blocked" ? "Blocked by recorded facts" : item.disposition === "waiting" ? "Waiting for approval" : "Needs review"}</Badge>
    </div>
    <ul className="review-blockers">{item.blockers.map((blocker, index) => <li key={`${blocker.code}-${index}`}>
      <Badge>{humanize(blocker.category)}</Badge>
      <div><p>{blocker.message}</p><p className="review-next-step"><strong>Next step:</strong> {blocker.next_step}</p></div>
    </li>)}</ul>
    {!!actions.length && <p className="helper">Related options: {actions.join(" · ")}</p>}
    {item.missing_source && <p className="review-missing-source"><CircleAlert size={15} /> Supporting source evidence is missing or unavailable. A review alone cannot replace it.</p>}
    <div className="review-queue-actions">
      {!!availableRules.length && <Button onClick={() => onEvidence(availableRules)} aria-label={`Review evidence for ${item.title}`}><FileText size={14} /> Review evidence <ArrowRight size={14} /></Button>}
      {item.subject_kind === "event" && !availableRules.length && <Button onClick={onIntake}>Review financial picture <ArrowRight size={14} /></Button>}
      {item.missing_source && <Button variant="ghost" onClick={onUpload}>Add supporting document</Button>}
    </div>
  </article>;
}

export default function ReviewQueue({ workspace, onEvidence, onIntake, onUpload, onRefresh }: Props) {
  const [queue, setQueue] = useState<Queue | null>(null);
  const [error, setError] = useState("");
  const [stale, setStale] = useState(false);
  const [retry, setRetry] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const { session_id: sessionId, revision } = workspace;

  useEffect(() => {
    const controller = new AbortController();
    setQueue(null); setError(""); setStale(false);
    void request<Queue>("/review-queue", sessionId, { signal: AbortSignal.any([controller.signal, AbortSignal.timeout(30_000)]) }).then(result => {
      if (controller.signal.aborted) return;
      if (result.revision !== revision) { setStale(true); return; }
      setQueue(result);
    }).catch(caught => {
      if (!controller.signal.aborted) setError(caught instanceof Error ? caught.message : "Review tasks could not be loaded.");
    });
    return () => controller.abort();
  }, [sessionId, revision, retry]);

  async function refresh() {
    setRefreshing(true);
    try { await onRefresh(); setRetry(value => value + 1); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "The workspace could not be refreshed."); }
    finally { setRefreshing(false); }
  }

  const items = queue?.revision === revision ? queue.items : null;
  return <section className="panel review-queue" aria-labelledby="review-queue-heading" data-testid="review-queue" data-revision={items ? queue?.revision : undefined}>
    <div className="panel-heading"><div><h2 id="review-queue-heading"><ClipboardList size={18} /> What needs review next?</h2><p>Essential obligations first, then blocked options and other reviews. This order does not estimate a cash benefit.</p></div>{items && <Badge tone={items.length ? "warning" : "neutral"}>{items.length} {items.length === 1 ? "item" : "items"}</Badge>}</div>
    <div className="review-queue-body">
      {error ? <div role="alert" className="review-queue-message"><p>Review tasks could not be loaded. {error}</p><Button onClick={() => setRetry(value => value + 1)}>Try again</Button></div>
        : stale ? <div role="status" className="review-queue-message"><p>The workspace changed while review tasks were loading. Refresh to inspect the latest facts.</p><Button busy={refreshing} onClick={() => void refresh()}>Refresh workspace</Button></div>
        : !items ? <p role="status" className="review-queue-loading"><LoaderCircle size={16} className="spin" /> Loading review tasks…</p>
        : !items.length ? <p role="status" className="review-queue-message">No listed review tasks remain. This does not mean the plan is financially safe; check its cash projection and declared verification bounds.</p>
        : <><ReviewItem item={items[0]} first workspace={workspace} onEvidence={onEvidence} onIntake={onIntake} onUpload={onUpload} />{items.length > 1 && <details className="review-queue-rest"><summary>Show {items.length - 1} more review {items.length === 2 ? "item" : "items"}</summary><div>{items.slice(1).map(item => <ReviewItem key={item.id} item={item} first={false} workspace={workspace} onEvidence={onEvidence} onIntake={onIntake} onUpload={onUpload} />)}</div></details>}</>}
    </div>
  </section>;
}
