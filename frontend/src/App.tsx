import { useCallback, useEffect, useState, type FormEvent } from "react";
import { loadConcepts, loadGraph, loadNext, startLearning, submitAnswer } from "./api/client";
import type { Concept, ConceptGraph, TutorMaterial } from "./types";
import WorkspacePage from "./pages/WorkspacePage";
import GraphPage from "./pages/GraphPage";
import TutorPage from "./pages/TutorPage";
import QuizPage from "./pages/QuizPage";
import ProgressPage from "./pages/ProgressPage";

type Page = "Workspace" | "Graph" | "Tutor" | "Quiz" | "Progress";
const pages: Page[] = ["Workspace", "Graph", "Tutor", "Quiz", "Progress"];

export default function App() {
  const [page, setPage] = useState<Page>("Workspace");
  const [studentId] = useState("demo");
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [targetId, setTargetId] = useState("gradient_descent");
  const [currentId, setCurrentId] = useState("functions");
  const [question, setQuestion] = useState("");
  const [graph, setGraph] = useState<ConceptGraph>({ nodes: [], edges: [], target: "gradient_descent", next_concept: "functions" });
  const [material, setMaterial] = useState<TutorMaterial | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [usingMock, setUsingMock] = useState(false);

  const refresh = useCallback(async (target = targetId) => {
    const [nextConcepts, nextGraph] = await Promise.all([loadConcepts(studentId), loadGraph(studentId, target)]);
    setConcepts(nextConcepts);
    setGraph(nextGraph);
  }, [studentId, targetId]);

  useEffect(() => { void refresh(); }, [refresh]);

  const chooseTarget = async (id: string) => {
    setBusy(true);
    setNotice("");
    setTargetId(id);
    const started = await startLearning(studentId, "", id);
    if (started.needs_topic_selection || !started.graph || !started.diagnostic) {
      setBusy(false);
      return;
    }
    setGraph(started.graph);
    setCurrentId(started.diagnostic.concept_id);
    setMaterial({
      next_concept: started.diagnostic.concept_id,
      status: "unknown",
      question: started.diagnostic.question,
      explanation: started.diagnostic.explanation,
      worked_example: started.diagnostic.worked_example,
      provider: started.diagnostic.provider,
      graph: started.graph,
    });
    setConcepts(await loadConcepts(studentId));
    setUsingMock(started.diagnostic.provider === "mock");
    setPage("Tutor");
    setBusy(false);
  };

  const begin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBusy(true);
    setNotice("");
    const started = await startLearning(studentId, question);
    if (started.needs_topic_selection || !started.graph || !started.diagnostic || !started.target_concept_id) {
      setNotice("I couldn’t identify the topic with confidence. Choose a concept below to continue.");
      setBusy(false);
      return;
    }
    setTargetId(started.target_concept_id);
    setGraph(started.graph);
    setCurrentId(started.diagnostic.concept_id);
    setMaterial({
      next_concept: started.diagnostic.concept_id,
      status: "unknown",
      question: started.diagnostic.question,
      explanation: started.diagnostic.explanation,
      worked_example: started.diagnostic.worked_example,
      provider: started.diagnostic.provider,
      graph: started.graph,
    });
    setConcepts(await loadConcepts(studentId));
    setUsingMock(started.diagnostic.provider === "mock");
    setPage("Tutor");
    setBusy(false);
  };

  const answer = async (answerText: string, conceptId = currentId) => {
    setBusy(true);
    setNotice("");
    const result = await submitAnswer(studentId, conceptId, targetId, answerText);
    setGraph(result.graph);
    setCurrentId(result.next_concept);
    setNotice(`${Math.round(result.score * 100)}% · ${result.feedback}`);
    setConcepts(await loadConcepts(studentId));
    const next = await loadNext(studentId, targetId);
    setMaterial(next);
    setUsingMock(next.provider === "mock");
    setBusy(false);
  };

  const nextStep = async () => {
    setBusy(true);
    const next = await loadNext(studentId, targetId);
    setGraph(next.graph);
    setCurrentId(next.next_concept);
    setMaterial(next);
    setUsingMock(next.provider === "mock");
    setConcepts(await loadConcepts(studentId));
    setBusy(false);
  };

  const selectNode = (id: string) => {
    setTargetId(id);
    setCurrentId(id);
    void startLearning(studentId, "", id).then(async (started) => {
      if (!started.graph || !started.diagnostic) return;
      setGraph(started.graph);
      setCurrentId(started.diagnostic.concept_id);
      setMaterial({
        next_concept: started.diagnostic.concept_id,
        status: "unknown",
        question: started.diagnostic.question,
        explanation: started.diagnostic.explanation,
        worked_example: started.diagnostic.worked_example,
        provider: started.diagnostic.provider,
        graph: started.graph,
      });
      setConcepts(await loadConcepts(studentId));
      setUsingMock(started.diagnostic.provider === "mock");
    });
  };

  return <div className="app-shell">
    <aside className="sidebar">
      <a className="brand" href="#workspace" onClick={(event) => { event.preventDefault(); setPage("Workspace"); }}><span className="brand-mark">m</span><span>mindmesh<small>ADAPTIVE LEARNING</small></span></a>
      <div className="side-label">LEARNING SPACE</div>
      <nav>{pages.map((item, index) => <button key={item} className={`nav-item ${page === item ? "active" : ""}`} onClick={() => setPage(item)}><span className="nav-number">0{index + 1}</span>{item}{page === item && <i />}</button>)}</nav>
      <div className="sidebar-bottom"><div className="avatar">S</div><div><strong>Student workspace</strong><small>Learning profile · {studentId}</small></div><span className="online-dot" /></div>
    </aside>
    <main className="main-area">
      <header className="topbar"><div><span>MindMesh</span><b>/</b><strong>{page}</strong></div><div className="topbar-right"><span className={`connection-dot ${usingMock ? "mock" : ""}`} />{usingMock ? "Built-in tutor active" : "Learning engine ready"}<button className="target-chip" onClick={() => setPage("Graph")}>Goal · {concepts.find((item) => item.id === targetId)?.name || "Gradient Descent"} <span>⌄</span></button></div></header>
      {notice && <div className="notice" role="status"><span>{notice}</span><button onClick={() => setNotice("")} aria-label="Dismiss">×</button></div>}
      <div className="content-area">
        {page === "Workspace" && <WorkspacePage concepts={concepts} target={targetId} question={question} setQuestion={setQuestion} onStart={begin} busy={busy} onSelect={chooseTarget} />}
        {page === "Graph" && <GraphPage graph={graph} onSelect={selectNode} />}
        {page === "Tutor" && <TutorPage concepts={concepts} currentId={currentId} targetId={targetId} material={material} busy={busy} onAnswer={answer} onNext={nextStep} />}
        {page === "Quiz" && <QuizPage concepts={concepts} currentId={currentId} busy={busy} onAnswer={(id, value) => answer(value, id)} />}
        {page === "Progress" && <ProgressPage concepts={concepts} />}
      </div>
      <footer className="app-footer"><span>Built to find the missing link in how you learn.</span><span>NEO4J GRAPH <i /> ADAPTIVE PATH</span></footer>
    </main>
  </div>;
}
