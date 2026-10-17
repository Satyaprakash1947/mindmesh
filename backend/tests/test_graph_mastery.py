from app.graph.mastery import mastery_status
from app.graph.queries import UPSERT_CONCEPT, UPSERT_REQUIRES
from app.graph.seed_data import CONCEPTS, REQUIRES


def test_mastery_is_unknown_without_attempts():
    assert mastery_status([]) == "unknown"


def test_latest_low_attempt_requires_review():
    assert mastery_status([0.95, 0.49]) == "needs_review"


def test_two_recent_attempts_can_demonstrate_mastery():
    assert mastery_status([0.41, 0.99]) == "demonstrated"


def test_mastery_uses_only_the_latest_two_attempts():
    assert mastery_status([0.1, 0.4, 0.8, 0.8]) == "demonstrated"


def test_seed_contains_complete_unique_concepts_and_valid_edges():
    concept_ids = [concept["id"] for concept in CONCEPTS]
    assert len(CONCEPTS) == 15
    assert len(concept_ids) == len(set(concept_ids))
    assert len(REQUIRES) == 18
    assert all(
        concept.get(field)
        for concept in CONCEPTS
        for field in ("explanation", "diagnostic_question", "worked_example", "rubric")
    )
    assert all(source in concept_ids and target in concept_ids for source, target in REQUIRES)


def test_seed_queries_use_merge_and_parameters():
    assert "MERGE (c:Concept {id: $id})" in UPSERT_CONCEPT
    assert "MERGE (source)-[:REQUIRES]->(target)" in UPSERT_REQUIRES
    assert "$source" in UPSERT_REQUIRES and "$target" in UPSERT_REQUIRES
