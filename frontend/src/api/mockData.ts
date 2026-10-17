import type { Concept, ConceptGraph, MasteryStatus } from "../types";

export const concepts: Array<Concept & { order: number; keywords: string[]; diagnostic: string; example: string; rubric: string[] }> = [
  { id: "functions", name: "Functions", order: 1, status: "unknown", explanation: "A function maps each allowed input to exactly one output.", keywords: ["function"], diagnostic: "What does it mean for a rule to be a function?", example: "For f(x)=2x+1, input 3 maps to 7.", rubric: ["input", "one output"] },
  { id: "linear_functions", name: "Linear Functions", order: 2, status: "unknown", explanation: "A linear function has a constant rate of change and graphs as a straight line.", keywords: ["linear", "line"], diagnostic: "What does the slope tell you in y=3x+2?", example: "Every increase of 1 in x changes y by 3.", rubric: ["constant rate", "slope"] },
  { id: "coordinate_change", name: "Coordinate Change", order: 3, status: "unknown", explanation: "A change is final value minus initial value: Δx=x₂−x₁.", keywords: ["coordinate", "delta"], diagnostic: "Between (2,4) and (5,10), what are Δx and Δy?", example: "Δx=3 and Δy=6.", rubric: ["delta x is 3", "delta y is 6"] },
  { id: "slope", name: "Slope", order: 4, status: "unknown", explanation: "Slope is change in output divided by change in input, or rise over run.", keywords: ["slope", "rate of change"], diagnostic: "Find the slope between (2,4) and (5,10).", example: "(10−4)/(5−2)=2.", rubric: ["change in y", "change in x", "slope is 2"] },
  { id: "limits", name: "Limits", order: 5, status: "unknown", explanation: "A limit describes the value a function approaches as input gets close to a point.", keywords: ["limit", "approach"], diagnostic: "What does a limit describe?", example: "As x approaches 2, x+3 approaches 5.", rubric: ["approaches", "input gets close"] },
  { id: "secant_slope", name: "Secant Slope", order: 6, status: "unknown", explanation: "A secant line passes through two points and measures average rate of change.", keywords: ["secant", "average slope"], diagnostic: "How is a secant slope different from a slope at one point?", example: "For x² from 1 to 3, the secant slope is 4.", rubric: ["two points", "average rate"] },
  { id: "derivatives", name: "Derivatives", order: 7, status: "unknown", explanation: "A derivative gives instantaneous rate of change and the slope of a tangent line.", keywords: ["derivative", "tangent", "instantaneous"], diagnostic: "What does f′(a) tell you about f near x=a?", example: "For f(x)=x², f′(3)=6.", rubric: ["instantaneous rate of change", "tangent slope"] },
  { id: "power_rule", name: "Power Rule", order: 8, status: "unknown", explanation: "For xⁿ, the derivative is n·xⁿ⁻¹: multiply by the exponent, then reduce it by one.", keywords: ["power rule", "exponent"], diagnostic: "Differentiate x³ using the power rule.", example: "d(x³)/dx=3x².", rubric: ["multiply by exponent", "reduce exponent", "3x squared"] },
  { id: "derivative_rules", name: "Derivative Rules", order: 9, status: "unknown", explanation: "Differentiate sums term by term and pull constants outside; use product and chain rules where needed.", keywords: ["sum rule", "chain rule", "product rule"], diagnostic: "Differentiate 4x²+3x term by term.", example: "The derivative is 8x+3.", rubric: ["differentiate each term", "8x plus 3"] },
  { id: "partial_derivatives", name: "Partial Derivatives", order: 10, status: "unknown", explanation: "A partial derivative measures change with one variable while holding the others constant.", keywords: ["partial derivative", "multivariable"], diagnostic: "For f(x,y)=x²+3y, find ∂f/∂x.", example: "Hold y constant: ∂f/∂x=2x.", rubric: ["hold y constant", "2x"] },
  { id: "gradient", name: "Gradient", order: 11, status: "unknown", explanation: "The gradient collects partial derivatives into a vector pointing toward steepest increase.", keywords: ["gradient", "vector"], diagnostic: "What information does the gradient vector contain?", example: "For x²+y², ∇f=(2x,2y).", rubric: ["vector of partial derivatives", "steepest increase"] },
  { id: "loss_functions", name: "Loss Functions", order: 12, status: "unknown", explanation: "A loss function measures prediction error; training seeks parameters that reduce it.", keywords: ["loss", "objective", "error"], diagnostic: "What does a loss value represent during training?", example: "A lower prediction error means lower loss.", rubric: ["prediction error", "minimize"] },
  { id: "learning_rate", name: "Learning Rate", order: 13, status: "unknown", explanation: "Learning rate controls update size. Too large may overshoot; too small makes learning slow.", keywords: ["learning rate", "step size"], diagnostic: "What can happen when the learning rate is too large?", example: "A larger rate makes a larger parameter update.", rubric: ["step size", "overshoot"] },
  { id: "gradient_descent", name: "Gradient Descent", order: 14, status: "unknown", explanation: "Gradient descent iteratively updates parameters opposite the gradient: θ ← θ − η∇L(θ).", keywords: ["gradient descent", "optimization", "minimize function"], diagnostic: "Why does gradient descent subtract the gradient when minimizing a loss?", example: "If θ=2, η=0.1 and gradient=4, θ becomes 1.6.", rubric: ["gradient points uphill", "negative gradient points downhill", "subtract the gradient", "reduce the loss"] },
  { id: "stochastic_gradient_descent", name: "Stochastic Gradient Descent", order: 15, status: "unknown", explanation: "SGD estimates gradients from one example or a small batch for cheaper, more frequent updates.", keywords: ["stochastic gradient descent", "sgd", "mini batch"], diagnostic: "How does SGD differ from full-batch gradient descent?", example: "A mini-batch of 32 examples estimates an update without scanning the entire dataset.", rubric: ["one example or mini-batch", "estimate", "noisier but cheaper"] },
];

export const prerequisiteEdges = [
  ["functions", "linear_functions"], ["linear_functions", "coordinate_change"], ["coordinate_change", "slope"],
  ["slope", "limits"], ["slope", "secant_slope"], ["limits", "derivatives"], ["secant_slope", "derivatives"],
  ["derivatives", "power_rule"], ["power_rule", "derivative_rules"], ["derivatives", "partial_derivatives"],
  ["partial_derivatives", "gradient"], ["derivative_rules", "gradient"], ["functions", "loss_functions"],
  ["loss_functions", "learning_rate"], ["gradient", "gradient_descent"], ["learning_rate", "gradient_descent"],
  ["loss_functions", "gradient_descent"], ["gradient_descent", "stochastic_gradient_descent"],
].map(([source, target]) => ({ source, target, type: "REQUIRES" as const }));

const STORAGE_KEY = "mindmesh-status-v1";

export function readStatuses(): Record<string, MasteryStatus> {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"); } catch { return {}; }
}

export function setStatus(conceptId: string, status: MasteryStatus): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...readStatuses(), [conceptId]: status }));
}

export function mockConcepts(studentId: string): Concept[] {
  const statuses = studentId === "demo" ? readStatuses() : {};
  return concepts.map(({ id, name, explanation, diagnostic }) => ({ id, name, explanation, diagnostic_question: diagnostic, status: statuses[id] || "unknown" }));
}

export function mockGraph(studentId: string, targetId: string): ConceptGraph {
  const all = mockConcepts(studentId);
  const required = new Set([targetId]);
  let changed = true;
  while (changed) {
    changed = false;
    for (const edge of prerequisiteEdges) {
      if (required.has(edge.target) && !required.has(edge.source)) { required.add(edge.source); changed = true; }
    }
  }
  const nodes = all.filter((concept) => required.has(concept.id));
  const target = nodes.find((concept) => concept.id === targetId);
  const next = target?.status === "demonstrated" ? target : nodes.filter((concept) => concept.status !== "demonstrated").sort((a, b) => concepts.find((c) => c.id === a.id)!.order - concepts.find((c) => c.id === b.id)!.order)[0];
  return { nodes: nodes.map(({ id, name, status }) => ({ id, name, status })), edges: prerequisiteEdges.filter((edge) => required.has(edge.source) && required.has(edge.target)), target: targetId, next_concept: next?.id || targetId };
}

export function getMockConcept(id: string) { return concepts.find((concept) => concept.id === id); }

export function gradeMockAnswer(answer: string, conceptId: string): { score: number; feedback: string; status: MasteryStatus } {
  const concept = getMockConcept(conceptId);
  if (!concept) return { score: 0, feedback: "Choose a concept first.", status: "unknown" };
  const text = answer.toLowerCase();
  const hits = concept.rubric.filter((point) => point.toLowerCase().split(/\s+/).some((word) => word.length > 3 && text.includes(word))).length;
  const score = Math.round((hits / concept.rubric.length) * 100) / 100;
  const status: MasteryStatus = score >= 0.7 ? "demonstrated" : "needs_review";
  setStatus(conceptId, status);
  const feedback = status === "demonstrated" ? "Good work. You covered the key ideas." : `Review the idea, then try again. Key points: ${concept.rubric.join("; ")}.`;
  return { score, feedback, status };
}
