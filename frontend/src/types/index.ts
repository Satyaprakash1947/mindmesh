export type MasteryStatus = "unknown" | "needs_review" | "demonstrated";

export interface Concept {
  id: string;
  name: string;
  status: MasteryStatus;
  explanation: string;
  diagnostic_question?: string;
}

export interface GraphNode {
  id: string;
  name: string;
  status: MasteryStatus;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: "REQUIRES";
}

export interface ConceptGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  target: string;
  next_concept: string | null;
}

export interface LearningStart {
  needs_topic_selection: boolean;
  target_concept_id?: string;
  confidence?: number;
  concepts?: Array<{ id: string; name: string }>;
  graph?: ConceptGraph;
  diagnostic?: { concept_id: string; question: string; explanation: string; worked_example: string; provider: string };
}

export interface Evaluation {
  score: number;
  feedback: string;
  status: MasteryStatus;
  next_concept: string;
  graph: ConceptGraph;
}

export interface TutorMaterial {
  next_concept: string;
  status: MasteryStatus;
  question: string;
  explanation: string;
  worked_example: string;
  provider: string;
  graph: ConceptGraph;
}
