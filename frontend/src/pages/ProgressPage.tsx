import type { CSSProperties } from "react";
import type { Concept } from "../types";
import StatusBadge from "../components/StatusBadge";

export default function ProgressPage({ concepts }: { concepts: Concept[] }) {
  const demonstrated = concepts.filter((item) => item.status === "demonstrated").length;
  const percent = concepts.length ? Math.round((demonstrated / concepts.length) * 100) : 0;
  return <section className="page-panel progress-panel"><div className="section-heading"><div><div className="eyebrow">YOUR PROGRESS</div><h1>Knowledge that sticks</h1><p>Mastery is based on your recent answers, and it updates what MindMesh recommends next.</p></div><div className="progress-ring" style={{ "--progress": `${percent * 3.6}deg` } as CSSProperties & { "--progress": string }}><div><strong>{percent}%</strong><span>demonstrated</span></div></div></div>
    <div className="progress-summary"><div><strong>{demonstrated}</strong><span>Demonstrated</span></div><div><strong>{concepts.filter((item) => item.status === "needs_review").length}</strong><span>Needs review</span></div><div><strong>{concepts.filter((item) => item.status === "unknown").length}</strong><span>Not checked yet</span></div></div>
    <div className="progress-list">{concepts.map((concept, index) => <div className="progress-row" key={concept.id}><span className="progress-index">{String(index + 1).padStart(2, "0")}</span><strong>{concept.name}</strong><div className="progress-track"><i className={`progress-fill ${concept.status}`} /></div><StatusBadge status={concept.status} /></div>)}</div>
  </section>;
}
