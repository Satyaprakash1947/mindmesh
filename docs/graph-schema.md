# Graph schema

## Nodes

### `Concept`

Properties: `id` (stable unique key), `name`, `explanation`, `diagnostic_question`, `worked_example`, `rubric` (list of accepted ideas), `keywords` (topic-mapping terms), and `order` (seed order).

### `Student`

Properties: `id` (stable learner key), `created_at`.

### `Attempt`

Properties: `id`, `student_id`, `concept_id`, `answer`, `score` (0–1), `feedback`, `created_at`.

## Relationships

- `(prerequisite:Concept)-[:REQUIRES]->(target:Concept)` means the prerequisite should be mastered before the target.
- `(student:Student)-[:HAS_ATTEMPT]->(attempt:Attempt)` records learner activity.
- `(attempt:Attempt)-[:FOR_CONCEPT]->(concept:Concept)` associates an answer with its concept.

## Mastery

Mastery is the mean of the learner's latest five attempt scores for a concept. No attempts means `unknown`; a mean below `MASTERY_THRESHOLD` means `needs_review`; otherwise the concept is `demonstrated`. Recent attempts are ordered by `created_at` descending.

## Query behavior

The graph endpoint returns the target and its transitive prerequisite subgraph. Edges use `{source, target, type}`. Recommended next step is the earliest prerequisite on a shortest path that is not demonstrated; if all prerequisites are demonstrated, it is the target itself unless the target is also demonstrated.

The in-memory implementation uses the same graph and mastery rules as the Neo4j adapter so the API stays usable without credentials.
