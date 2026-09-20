"use client";

import { Background, Controls, MarkerType, ReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type { Workspace } from "@/lib/types";

const colors: Record<string, string> = { document: "#e8efff", rule: "#e6f3ee", action: "#fff1dc", event: "#edf0f7", entity: "#f1eafb" };

export default function DependencyGraph({ graph, onEvidence, highlightRuleIds = [] }: { graph: Workspace["graph"]; onEvidence: (ids: string[]) => void; highlightRuleIds?: string[] }) {
  const highlightedRules = new Set(highlightRuleIds);
  const rows: Record<string, number> = {};
  const columns: Record<string, number> = { document: 0, entity: 0, rule: 1, action: 2, event: 3 };
  const nodes = (graph.nodes ?? []).map(node => {
    const column = columns[node.kind];
    const row = rows[column] || 0;
    rows[column] = row + 1;
    const connected = (graph.edges ?? []).some(edge => (edge.source === node.id || edge.target === node.id) && (edge.rule_ids ?? []).some(id => highlightedRules.has(id)));
    const highlighted = (node.kind === "rule" && highlightedRules.has(node.reference_id)) || connected;
    return { id: node.id, className: highlighted ? "graph-node-highlighted" : undefined, data: { label: <div><small className="graph-kind">{node.kind}</small><strong>{node.label}</strong><span className="graph-status">{node.status.replaceAll("_", " ")}</span></div> }, position: { x: column * 290, y: row * 135 }, style: { width: 230, borderRadius: 12, background: "#fff", border: `1px solid ${highlighted ? "#647fc3" : colors[node.kind]}`, boxShadow: highlighted ? "0 0 0 3px #dce6ff, 0 8px 25px #17244c16" : "0 4px 20px #17244c07", padding: 16, textAlign: "left" as const, fontSize: 12 }, sourcePosition: "right" as never, targetPosition: "left" as never };
  });
  const edges = (graph.edges ?? []).map(edge => {
    const highlighted = (edge.rule_ids ?? []).some(id => highlightedRules.has(id));
    return { id: edge.id, className: highlighted ? "graph-edge-highlighted" : undefined, source: edge.source, target: edge.target, label: edge.label || edge.relation, data: { ruleIds: edge.rule_ids }, markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: highlighted ? "#647fc3" : edge.relation === "excludes" ? "#d38a7d" : "#a7b7d4", strokeWidth: highlighted ? 3 : 1.5 }, labelStyle: { fontSize: 10, fill: highlighted ? "#405b9c" : "#69758c", fontWeight: highlighted ? 650 : 400 }, labelBgStyle: { fill: "#f8fafe" } };
  });
  return <div className="graph-canvas"><ReactFlow nodes={nodes} edges={edges} fitView minZoom={0.2} maxZoom={1.5} nodesDraggable nodesConnectable={false} onNodeClick={(_, node) => { const source = graph.nodes?.find(item => item.id === node.id); if (source?.kind === "rule") onEvidence([source.reference_id]); else onEvidence((graph.edges ?? []).filter(edge => edge.source === node.id || edge.target === node.id).flatMap(edge => edge.rule_ids ?? [])); }} onEdgeClick={(_, edge) => onEvidence(edge.data?.ruleIds ?? [])}><Background color="#d6deed" gap={20} /><Controls showInteractive={false} /></ReactFlow></div>;
}
