"use client";

import { ArrowUpRight, CalendarDays, ChevronRight, CircleAlert, FileText, GitBranch } from "lucide-react";
import { Badge, Button } from "./ui";
import { humanize, shortDate } from "@/lib/api";
import type { Action, PlanResult } from "@/lib/types";

type Props = { action: Action; plan: PlanResult; comparing: boolean; drafting: boolean; onEvidence: (ids: string[]) => void; onCompare: () => void; onDraft: () => void };

export default function ActionCard({ action, plan, comparing, drafting, onEvidence, onCompare, onDraft }: Props) {
  const chosen = plan.actions.find(item => item.action_id === action.id);
  const excluded = plan.excluded_actions?.[action.id];
  const risky = action.effects?.some(effect => effect.operation === "accelerate");
  return <article className={`action-card ${chosen ? "action-selected" : risky ? "action-risk" : ""}`} key={action.id} data-testid={`action-${action.id}`}>
    <div className={`action-symbol ${chosen ? "green" : risky ? "rose" : "amber"}`}>{chosen ? <CalendarDays size={20} /> : risky ? <GitBranch size={20} /> : <CircleAlert size={20} />}</div>
    <div className="action-content"><div className="action-card-top"><span className="eyebrow">{chosen ? `Step ${chosen.order}` : risky ? "Hidden consequence" : "Needs confirmation"}</span><Badge tone={chosen ? chosen.conditional ? "warning" : "success" : risky ? "danger" : "warning"}>{chosen ? chosen.conditional ? "Conditional" : plan.assumptions?.force_action_ids?.includes(action.id) ? "Requested option" : "In your plan" : risky ? "Avoid for now" : "Not in plan"}</Badge></div><h3>{action.title}</h3><p>{chosen?.explanation || action.description}</p>{excluded && <p className="action-exclusion">{excluded}</p>}<div className="action-card-bottom"><button className="text-button" onClick={() => onEvidence(action.source_rule_ids)}><FileText size={13} /> View evidence <ChevronRight size={13} /></button>{chosen ? <span className="action-date"><CalendarDays size={13} /> {shortDate(chosen.execution_date)}</span> : <span className="action-date">{action.approval_status === "pending" ? "Approval pending" : humanize(action.approval_status || "not_required")}</span>}<Button variant="ghost" busy={comparing} onClick={onCompare}>Compare option alone</Button><Button variant="ghost" busy={drafting} onClick={onDraft}>Draft request <ArrowUpRight size={13} /></Button></div></div>
  </article>;
}
