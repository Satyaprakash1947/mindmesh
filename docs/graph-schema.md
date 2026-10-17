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

Mastery considers the latest two attempt scores for a concept, ordered by `created_at` descending. No attempts means `unknown`. A latest score below `0.5` means `needs_review`. Otherwise, an average of the latest two scores at or above `MASTERY_THRESHOLD` means `demonstrated`; a lower average means `needs_review`. The default threshold is `0.7`.

## Query behavior

The graph endpoint returns the target and its transitive prerequisite subgraph. Edges use `{source, target, type}`. Recommended next step is the closest unmet prerequisite whose own prerequisites are all demonstrated. Ties use seed order and then concept ID. The graph payload includes `next_reason`, a readable prerequisite path. If all prerequisites are demonstrated, the target is ready; if the target is already demonstrated, the API reports that status in the reason.

## Seed data and query safety

`backend/data/concepts.json` is the source of truth for 15 concept records and 18 directed prerequisite edges. Each concept includes an original explanation, diagnostic question, worked example, and rubric. `backend/scripts/seed.py` creates unique ID constraints, then uses `MERGE` for concepts and edges so it can safely run more than once. All values are passed as Cypher parameters; query text is defined in `backend/app/graph/queries.py`.

The in-memory implementation uses the same seed data, mastery function, and recommendation logic as the Neo4j adapter so the API stays usable without credentials.
