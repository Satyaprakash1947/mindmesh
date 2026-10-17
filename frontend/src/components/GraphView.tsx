import { useMemo } from "react";
import { Background, Controls, MiniMap, ReactFlow, type Edge, type Node } from "@xyflow/react";
import type { ConceptGraph } from "../types";

export default function GraphView({ graph, onSelect }: { graph: ConceptGraph; onSelect?: (id: string) => void }) {
  const nodes = useMemo<Node[]>(() => graph.nodes.map((node, index) => ({
    id: node.id,
    position: { x: (index % 4) * 250, y: Math.floor(index / 4) * 150 },
    data: { label: <div className="graph-node-content"><strong>{node.name}</strong><span className={`node-dot ${node.status}`} />{node.id === graph.target && <small>Target</small>}</div> },
    className: `graph-node node-${node.status}${node.id === graph.target ? " node-target" : ""}`,
  })), [graph]);
  const edges = useMemo<Edge[]>(() => graph.edges.map((edge) => ({ id: `${edge.source}-${edge.target}`, source: edge.source, target: edge.target, label: "requires", animated: edge.target === graph.next_concept, type: "smoothstep" })), [graph]);

  return <div className="flow-frame"><ReactFlow nodes={nodes} edges={edges} fitView fitViewOptions={{ padding: 0.2 }} onNodeClick={(_, node) => onSelect?.(node.id)} nodesConnectable={false} elementsSelectable><Background color="#27364d" gap={24} /><MiniMap nodeColor={(node) => node.className?.includes("demonstrated") ? "#38b58f" : node.className?.includes("needs_review") ? "#e4746a" : "#8292aa"} /><Controls /></ReactFlow></div>;
}
