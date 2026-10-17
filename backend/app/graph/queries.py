"""Parameterized Cypher statements for the MindMesh concept and mastery graph."""

CREATE_CONSTRAINTS = (
    (
        "CREATE CONSTRAINT concept_id IF NOT EXISTS "
        "FOR (c:Concept) REQUIRE c.id IS UNIQUE"
    ),
    (
        "CREATE CONSTRAINT student_id IF NOT EXISTS "
        "FOR (s:Student) REQUIRE s.id IS UNIQUE"
    ),
    (
        "CREATE CONSTRAINT attempt_id IF NOT EXISTS "
        "FOR (a:Attempt) REQUIRE a.id IS UNIQUE"
    ),
)

UPSERT_CONCEPT = "MERGE (c:Concept {id: $id}) SET c += $properties"
UPSERT_REQUIRES = (
    "MATCH (source:Concept {id: $source}), (target:Concept {id: $target}) "
    "MERGE (source)-[:REQUIRES]->(target)"
)
ALL_CONCEPTS = "MATCH (c:Concept) RETURN c ORDER BY c.order"
ALL_EDGES = (
    "MATCH (source:Concept)-[:REQUIRES]->(target:Concept) "
    "RETURN source.id AS source, target.id AS target"
)
GET_CONCEPT = "MATCH (c:Concept {id: $id}) RETURN c"
MASTERY_STATUSES = (
    "MATCH (c:Concept) "
    "OPTIONAL MATCH (:Student {id: $student_id})-[:HAS_ATTEMPT]->(a:Attempt)"
    "-[:FOR_CONCEPT]->(c) "
    "WITH c, a ORDER BY a.created_at DESC "
    "WITH c, collect(a.score)[0..2] AS scores "
    "RETURN c.id AS id, CASE WHEN size(scores) = 0 THEN 'unknown' "
    "WHEN scores[0] < $review_threshold THEN 'needs_review' "
    "WHEN reduce(total = 0.0, score IN scores | total + score) / size(scores) "
    ">= $mastery_threshold THEN 'demonstrated' ELSE 'needs_review' END AS status"
)
CREATE_ATTEMPT = (
    "MERGE (s:Student {id: $student_id}) "
    "ON CREATE SET s.created_at = $created_at "
    "MATCH (c:Concept {id: $concept_id}) "
    "CREATE (a:Attempt {id: $id, student_id: $student_id, "
    "concept_id: $concept_id, answer: $answer, score: $score, "
    "feedback: $feedback, created_at: $created_at}) "
    "CREATE (s)-[:HAS_ATTEMPT]->(a) "
    "CREATE (a)-[:FOR_CONCEPT]->(c)"
)
