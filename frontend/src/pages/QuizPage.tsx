import { useState, type FormEvent } from "react";
import type { Concept } from "../types";
import StatusBadge from "../components/StatusBadge";

export default function QuizPage({ concepts, currentId, busy, onAnswer }: { concepts: Concept[]; currentId: string; busy: boolean; onAnswer: (conceptId: string, answer: string) => Promise<void> }) {
  const [selected, setSelected] = useState(currentId);
  const [answer, setAnswer] = useState("");
  const concept = concepts.find((item) => item.id === selected);
  const submit = async (event: FormEvent) => { event.preventDefault(); if (answer.trim()) { await onAnswer(selected, answer); setAnswer(""); } };
  return <div className="page-grid quiz-grid"><section className="page-panel quiz-main"><div className="eyebrow">RETRIEVAL PRACTICE</div><h1>Check what you know</h1><p className="lede">Short diagnostics help the recommendation respond to your understanding, not a fixed script.</p>
    <label className="select-label" htmlFor="quiz-concept">Concept</label><select id="quiz-concept" value={selected} onChange={(event) => setSelected(event.target.value)}>{concepts.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select>
    <div className="question-card"><div className="question-kicker">DIAGNOSTIC QUESTION</div><h2>{concept?.name || "Choose a concept"}</h2><p>{concept?.explanation || "Choose a concept to begin."}</p><div className="question-prompt">{concept?.diagnostic_question || "Select a concept above."}</div></div>
    <form onSubmit={submit} className="answer-card"><label htmlFor="quiz-answer">Your answer</label><textarea id="quiz-answer" value={answer} onChange={(event) => setAnswer(event.target.value)} rows={5} placeholder="Write a few words or sentences…" /><div className="form-row"><StatusBadge status={concept?.status || "unknown"} /><button className="primary-button" disabled={busy || !answer.trim()}>{busy ? "Grading…" : "Submit answer →"}</button></div></form>
  </section><aside className="page-panel quiz-aside"><div className="eyebrow">HOW IT WORKS</div><h2>Your answer changes the path</h2><ol className="steps-list"><li><span>1</span><div><strong>Diagnose</strong><p>Answer in your own words.</p></div></li><li><span>2</span><div><strong>Find the gap</strong><p>Rubric feedback marks the prerequisite status.</p></div></li><li><span>3</span><div><strong>Retest</strong><p>A demonstrated concept changes the next recommendation.</p></div></li></ol></aside></div>;
}
