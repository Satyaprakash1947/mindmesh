import type { FormEvent } from "react";
import type { Concept } from "../types";
import StatusBadge from "../components/StatusBadge";

export default function WorkspacePage({ concepts, target, question, setQuestion, onStart, busy, onSelect }: {
  concepts: Concept[]; target: string; question: string; setQuestion: (value: string) => void;
  onStart: (event: FormEvent<HTMLFormElement>) => void; busy: boolean; onSelect: (id: string) => void;
}) {
  const selected = concepts.find((concept) => concept.id === target);
  return <div className="page-grid workspace-grid">
    <section className="hero-card">
      <div className="eyebrow">YOUR LEARNING WORKSPACE</div>
      <h1>Find the missing link.<br /><span>Keep moving forward.</span></h1>
      <p>Ask a question or choose a concept. MindMesh checks the prerequisites, finds a gap, then guides you back to your goal.</p>
      <form onSubmit={onStart} className="question-form">
        <label htmlFor="learning-question">What are you trying to understand?</label>
        <textarea id="learning-question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="For example: How do I use gradient descent to minimize a function?" rows={3} />
        <div className="form-row"><span>Start with a question or a concept below</span><button className="primary-button" disabled={busy}>{busy ? "Starting…" : "Start learning →"}</button></div>
      </form>
    </section>
    <aside className="goal-card">
      <div className="card-topline"><span className="eyebrow">CURRENT TARGET</span><span className="target-spark">✦</span></div>
      <h2>{selected?.name || "Gradient Descent"}</h2>
      <p>{selected?.explanation || "Build the prerequisite knowledge behind optimization."}</p>
      {selected && <StatusBadge status={selected.status} />}
      <div className="goal-divider" />
      <div className="goal-stat"><span>Concepts in this graph</span><strong>{concepts.length}</strong></div>
      <div className="goal-stat"><span>Mastered so far</span><strong>{concepts.filter((item) => item.status === "demonstrated").length}</strong></div>
    </aside>
    <section className="concept-section">
      <div className="section-heading"><div><div className="eyebrow">PICK UP WHERE YOU NEED</div><h2>Explore concepts</h2></div><span>{concepts.length} concepts</span></div>
      <div className="concept-grid">{concepts.map((concept, index) => <button className="concept-card" key={concept.id} onClick={() => onSelect(concept.id)}>
        <span className="concept-index">{String(index + 1).padStart(2, "0")}</span><strong>{concept.name}</strong><StatusBadge status={concept.status} />
      </button>)}</div>
    </section>
  </div>;
}
