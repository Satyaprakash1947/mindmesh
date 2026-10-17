# API contract

Base URL: `/api`. JSON is used for requests and responses. IDs are lowercase slugs. Mastery status values are exactly `unknown`, `needs_review`, and `demonstrated`.

## `GET /health`

Returns `{ "status": "ok", "graph_backend": "neo4j" | "memory" }`.

## `GET /concepts`

Returns `{ "concepts": [{ "id", "name", "status", "explanation" }] }`. The optional query parameter `student_id` selects whose mastery is calculated.

## `GET /graph/{concept_id}?student_id=s1`

Returns the prerequisite subgraph and recommendation:

```json
{
  "nodes": [
    {"id":"gradient","name":"Gradient","status":"needs_review"},
    {"id":"gradient_descent","name":"Gradient Descent","status":"unknown"}
  ],
  "edges": [{"source":"partial_derivatives","target":"gradient","type":"REQUIRES"}],
  "target":"gradient_descent",
  "next_concept":"gradient",
  "next_reason":"Gradient is required for Gradient Descent."
}
```

Unknown concept IDs return `404`.

## `POST /learning/start`

Request: `{ "student_id":"s1", "question":"How do gradients help optimize a function?", "target_concept_id":null }`.

Returns the matched concept, confidence, prerequisite graph, and diagnostic prompt. If confidence is low and no explicit target was supplied, returns `needs_topic_selection: true` and available concepts.

## `POST /diagnose`

Request: `{ "student_id":"s1", "concept_id":"derivatives" }`.

Returns the diagnostic question, explanation, worked example, rubric, and mock/LLM provider name.

## `POST /answer`

Request: `{ "student_id":"s1", "concept_id":"derivatives", "answer":"..." }`.

Returns a structured rubric evaluation, saves the attempt, and recalculates the recommendation:

```json
{
  "score": 0.67,
  "feedback": "You have part of it. Revisit: one input cannot map to two outputs.",
  "matched_points": ["each input has exactly one output", "input output relationship"],
  "missing_points": ["one input cannot map to two outputs"],
  "status": "needs_review",
  "next_concept": "functions",
  "next_reason": "Functions is required for Gradient Descent."
}
```

Scores are between 0 and 1. `matched_points` and `missing_points` show which rubric criteria informed the score. Grading is deterministic and does not call the external tutor provider.

## `POST /learning/next`

Request: `{ "student_id":"s1", "target_concept_id":"gradient_descent" }`.

Returns the next unmet prerequisite or the target and its teaching material. When the learner masters a gap, a subsequent call can move toward the original target.

## `POST /mastery/update`

Request: `{ "student_id":"s1", "concept_id":"derivatives", "score":0.9, "answer":"ret test response", "feedback":"Good use of the slope definition." }`.

Stores an attempt and returns the updated status and recommendation. This is intended for integrations that grade externally; normal tutoring clients should use `/answer`.

## Errors

Errors use FastAPI's standard JSON detail response. `400` indicates invalid input, `404` an unknown concept, and `503` an unavailable configured graph database. If no Neo4j connection is configured, the app intentionally uses memory mode instead of returning `503`.
