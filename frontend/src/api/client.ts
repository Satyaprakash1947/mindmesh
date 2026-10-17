import { gradeMockAnswer, getMockConcept, mockConcepts, mockGraph } from "./mockData";
import type { Concept, ConceptGraph, Evaluation, LearningStart, TutorMaterial } from "../types";

const API = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}/api${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    signal: AbortSignal.timeout(2500),
  });
  if (!response.ok) throw new Error(`API request failed (${response.status})`);
  return response.json() as Promise<T>;
}

export async function loadConcepts(studentId: string): Promise<Concept[]> {
  try { return (await request<{ concepts: Concept[] }>(`/concepts?student_id=${encodeURIComponent(studentId)}`)).concepts; }
  catch { return mockConcepts(studentId); }
}

export async function loadGraph(studentId: string, target: string): Promise<ConceptGraph> {
  try { return await request<ConceptGraph>(`/graph/${encodeURIComponent(target)}?student_id=${encodeURIComponent(studentId)}`); }
  catch { return mockGraph(studentId, target); }
}

export async function startLearning(studentId: string, question: string, target?: string): Promise<LearningStart> {
  try { return await request<LearningStart>("/learning/start", { method: "POST", body: JSON.stringify({ student_id: studentId, question, target_concept_id: target || null }) }); }
  catch {
    const normalized = question.toLowerCase();
    const selected = target || ["gradient_descent", "derivatives", "gradient", "slope", "functions"].find((id) => normalized.includes(id.replaceAll("_", " ")));
    if (!selected) return { needs_topic_selection: true, confidence: 0, concepts: mockConcepts(studentId).map(({ id, name }) => ({ id, name })) };
    const graph = mockGraph(studentId, selected);
    const concept = getMockConcept(graph.next_concept || selected)!;
    return { needs_topic_selection: false, target_concept_id: selected, confidence: 0.8, graph, diagnostic: { concept_id: concept.id, question: concept.diagnostic, explanation: concept.explanation, worked_example: concept.example, provider: "mock" } };
  }
}

export async function submitAnswer(studentId: string, conceptId: string, target: string, answer: string): Promise<Evaluation> {
  try { return await request<Evaluation>("/answer", { method: "POST", body: JSON.stringify({ student_id: studentId, concept_id: conceptId, target_concept_id: target, answer }) }); }
  catch {
    const evaluation = gradeMockAnswer(answer, conceptId);
    const graph = mockGraph(studentId, target);
    return { ...evaluation, next_concept: graph.next_concept || target, graph };
  }
}

export async function loadNext(studentId: string, target: string): Promise<TutorMaterial> {
  try { return await request<TutorMaterial>("/learning/next", { method: "POST", body: JSON.stringify({ student_id: studentId, target_concept_id: target }) }); }
  catch {
    const graph = mockGraph(studentId, target);
    const next = graph.next_concept || target;
    const concept = getMockConcept(next)!;
    return { next_concept: next, status: concept.status, question: concept.diagnostic, explanation: concept.explanation, worked_example: concept.example, provider: "mock", graph };
  }
}
