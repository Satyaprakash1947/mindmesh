import GraphView from "../components/GraphView";
import type { ConceptGraph } from "../types";

export default function GraphPage({ graph, onSelect }: { graph: ConceptGraph; onSelect: (id: string) => void }) {
  return <section className="page-panel graph-panel">
    <div className="section-heading"><div><div className="eyebrow">PREREQUISITE MAP</div><h1>See how ideas connect</h1><p>Choose a node to make it your learning target. The highlighted connection marks the next recommendation.</p></div><span className="graph-count">{graph.nodes.length} nodes · {graph.edges.length} links</span></div>
    <div className="graph-legend"><span><i className="legend-dot unknown" />Unknown</span><span><i className="legend-dot needs_review" />Needs review</span><span><i className="legend-dot demonstrated" />Demonstrated</span><span><i className="legend-dot target" />Current target</span></div>
    <GraphView graph={graph} onSelect={onSelect} />
  </section>;
}
