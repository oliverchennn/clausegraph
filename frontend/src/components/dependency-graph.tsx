"use client";

import { Background, Controls, MarkerType, ReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type { Workspace } from "@/lib/types";

const colors: Record<string, string> = { document: "#e8efff", rule: "#e6f3ee", action: "#fff1dc", event: "#edf0f7", entity: "#f1eafb" };

export default function DependencyGraph({ graph, onEvidence }: { graph: Workspace["graph"]; onEvidence: (ids: string[]) => void }) {
  const rows: Record<string, number> = {};
  const columns: Record<string, number> = { document: 0, entity: 0, rule: 1, action: 2, event: 3 };
  const nodes = (graph.nodes ?? []).map(node => {
    const column = columns[node.kind];
    const row = rows[column] || 0;
    rows[column] = row + 1;
    return { id: node.id, data: { label: <div><small className="graph-kind">{node.kind}</small><strong>{node.label}</strong><span className="graph-status">{node.status.replaceAll("_", " ")}</span></div> }, position: { x: column * 290, y: row * 135 }, style: { width: 230, borderRadius: 12, background: "#fff", border: `1px solid ${colors[node.kind]}`, boxShadow: "0 4px 20px #17244c07", padding: 16, textAlign: "left" as const, fontSize: 12 }, sourcePosition: "right" as never, targetPosition: "left" as never };
  });
  const edges = (graph.edges ?? []).map(edge => ({ id: edge.id, source: edge.source, target: edge.target, label: edge.label || edge.relation, data: { ruleIds: edge.rule_ids }, markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: edge.relation === "excludes" ? "#d38a7d" : "#a7b7d4", strokeWidth: 1.5 }, labelStyle: { fontSize: 10, fill: "#69758c" }, labelBgStyle: { fill: "#f8fafe" } }));
  return <div className="graph-canvas"><ReactFlow nodes={nodes} edges={edges} fitView minZoom={0.2} maxZoom={1.5} nodesDraggable nodesConnectable={false} onNodeClick={(_, node) => { const source = graph.nodes?.find(item => item.id === node.id); if (source?.kind === "rule") onEvidence([source.reference_id]); else onEvidence((graph.edges ?? []).filter(edge => edge.source === node.id || edge.target === node.id).flatMap(edge => edge.rule_ids ?? [])); }} onEdgeClick={(_, edge) => onEvidence(edge.data?.ruleIds ?? [])}><Background color="#d6deed" gap={20} /><Controls showInteractive={false} /></ReactFlow></div>;
}
