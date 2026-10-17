import { useState, type FormEvent } from "react";
import type { Concept, TutorMaterial } from "../types";
import StatusBadge from "../components/StatusBadge";

export default function TutorPage({ concepts, currentId, targetId, material, busy, onAnswer, onNext }: {
  concepts: Concept[]; currentId: string; targetId: string; material: TutorMaterial | null; busy: boolean;
  onAnswer: (answer: string) => Promise<void>; onNext: () => void;
}) {
  const [answer, setAnswer] = useState("");
  const concept = concepts.find((item) => item.id === currentId);
  const submit = async (event: FormEvent) => { event.preventDefault(); if (answer.trim()) { await onAnswer(answer); setAnswer(""); } };
  return <div className="page-grid tutor-grid">
    <section className="page-panel tutor-main">
      <div className="eyebrow">YOUR TUTOR</div><h1>{concept?.name || "Choose a concept"}</h1>
      <div className="tutor-meta"><StatusBadge status={concept?.status || "unknown"} /><span>Goal: {concepts.find((item) => item.id === targetId)?.name || "Gradient Descent"}</span><span className="provider-pill">{material?.provider || "mock"} tutor</span></div>
      <div className="lesson-card"><div className="lesson-number">01</div><div><div className="eyebrow">A QUICK EXPLANATION</div><p>{material?.explanation || concept?.explanation || "Start a learning session to get a tailored explanation."}</p></div></div>
      <div className="lesson-card example-card"><div className="lesson-number">02</div><div><div className="eyebrow">WORKED EXAMPLE</div><p>{material?.worked_example || "A worked example will appear when you select a concept."}</p></div></div>
      <div className="diagnostic-prompt"><div className="eyebrow">DIAGNOSTIC QUESTION</div><p>{material?.question || concept?.diagnostic_question || "Start a learning session to get a diagnostic question."}</p></div>
      <form onSubmit={submit} className="answer-card"><label htmlFor="tutor-answer">Now try explaining it in your own words</label><textarea id="tutor-answer" value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder="Your answer drives the next recommendation…" rows={4} /><div className="form-row"><span>Feedback is matched to this concept’s rubric</span><button className="primary-button" disabled={busy || !answer.trim()}>{busy ? "Checking…" : "Check my answer →"}</button></div></form>
    </section>
    <aside className="page-panel next-card"><div className="eyebrow">LEARNING PATH</div><h2>One step at a time</h2><p>MindMesh will find the earliest prerequisite that needs attention, then guide you back to your original target.</p><div className="path-target"><span className="path-dot" /><div><small>GOAL</small><strong>{concepts.find((item) => item.id === targetId)?.name || "Gradient Descent"}</strong></div></div><div className="path-line" /><div className="path-target active-path"><span className="path-dot" /><div><small>UP NEXT</small><strong>{material?.next_concept ? concepts.find((item) => item.id === material.next_concept)?.name || material.next_concept : concept?.name || "Select a goal"}</strong></div></div><button className="secondary-button" onClick={onNext} disabled={busy}>Refresh next step ↗</button></aside>
  </div>;
}
