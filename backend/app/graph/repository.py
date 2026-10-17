from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from app.graph.seed_data import CONCEPTS, REQUIRES
from app.settings import Settings


class GraphRepository:
    """Neo4j-backed concept store with a deterministic in-memory demo mode."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.driver = None
        self._concepts = {concept["id"]: dict(concept) for concept in CONCEPTS}
        self._requires = list(REQUIRES)
        self._attempts: list[dict] = []
        self.backend = "memory"
        if settings.neo4j_uri and settings.neo4j_username and settings.neo4j_password:
            try:
                driver = GraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_username, settings.neo4j_password),
                )
                driver.verify_connectivity()
                self.driver = driver
                self.backend = "neo4j"
            except (Neo4jError, ValueError):
                if "driver" in locals():
                    driver.close()

    def close(self) -> None:
        if self.driver:
            self.driver.close()

    def all_concepts(self) -> list[dict]:
        if not self.driver:
            return sorted(self._concepts.values(), key=lambda item: item["order"])
        with self.driver.session(database=self.settings.neo4j_database) as session:
            records = session.run(
                "MATCH (c:Concept) RETURN c ORDER BY c.order"
            ).data()
        return [dict(record["c"]) for record in records]

    def all_edges(self) -> list[tuple[str, str]]:
        if not self.driver:
            return list(self._requires)
        with self.driver.session(database=self.settings.neo4j_database) as session:
            records = session.run(
                "MATCH (source:Concept)-[:REQUIRES]->(target:Concept) "
                "RETURN source.id AS source, target.id AS target"
            ).data()
        return [(record["source"], record["target"]) for record in records]

    def get_concept(self, concept_id: str) -> dict | None:
        if not self.driver:
            return self._concepts.get(concept_id)
        with self.driver.session(database=self.settings.neo4j_database) as session:
            record = session.run(
                "MATCH (c:Concept {id: $id}) RETURN c", id=concept_id
            ).single()
        return dict(record["c"]) if record else None

    def statuses(self, student_id: str) -> dict[str, str]:
        if not self.driver:
            scores_by_concept: dict[str, list[float]] = {}
            for attempt in self._attempts:
                if attempt["student_id"] == student_id:
                    scores_by_concept.setdefault(attempt["concept_id"], []).append(attempt["score"])
            return {
                concept_id: self._status(scores_by_concept.get(concept_id, []))
                for concept_id in self._concepts
            }
        with self.driver.session(database=self.settings.neo4j_database) as session:
            records = session.run(
                "MATCH (c:Concept) "
                "OPTIONAL MATCH (:Student {id: $student_id})-[:HAS_ATTEMPT]->(a:Attempt)"
                "-[:FOR_CONCEPT]->(c) "
                "WITH c, a ORDER BY a.created_at DESC "
                "WITH c, collect(a.score)[0..5] AS scores "
                "RETURN c.id AS id, CASE WHEN size(scores) = 0 THEN 'unknown' "
                "WHEN reduce(total = 0.0, score IN scores | total + score) / size(scores) "
                "< $threshold THEN 'needs_review' ELSE 'demonstrated' END AS status",
                student_id=student_id,
                threshold=self.settings.mastery_threshold,
            ).data()
        return {record["id"]: record["status"] for record in records}

    def record_attempt(
        self,
        student_id: str,
        concept_id: str,
        answer: str,
        score: float,
        feedback: str,
    ) -> None:
        attempt = {
            "id": str(uuid4()),
            "student_id": student_id,
            "concept_id": concept_id,
            "answer": answer,
            "score": round(float(score), 4),
            "feedback": feedback,
            "created_at": datetime.now(UTC).isoformat(),
        }
        if not self.driver:
            self._attempts.append(attempt)
            return
        with self.driver.session(database=self.settings.neo4j_database) as session:
            session.run(
                "MERGE (s:Student {id: $student_id}) "
                "ON CREATE SET s.created_at = $created_at "
                "MATCH (c:Concept {id: $concept_id}) "
                "CREATE (a:Attempt {id: $id, student_id: $student_id, "
                "concept_id: $concept_id, answer: $answer, score: $score, "
                "feedback: $feedback, created_at: $created_at}) "
                "CREATE (s)-[:HAS_ATTEMPT]->(a) "
                "CREATE (a)-[:FOR_CONCEPT]->(c)",
                **attempt,
            ).consume()

    def status_for(self, student_id: str, concept_id: str) -> str:
        return self.statuses(student_id).get(concept_id, "unknown")

    def graph_for_target(self, student_id: str, target_id: str) -> dict:
        concepts = {item["id"]: item for item in self.all_concepts()}
        if target_id not in concepts:
            raise KeyError(target_id)
        edges = self.all_edges()
        parents: dict[str, list[str]] = {}
        children: dict[str, list[str]] = {}
        for source, target in edges:
            parents.setdefault(target, []).append(source)
            children.setdefault(source, []).append(target)

        relevant = {target_id}
        pending = [target_id]
        while pending:
            current = pending.pop()
            for prerequisite in parents.get(current, []):
                if prerequisite not in relevant:
                    relevant.add(prerequisite)
                    pending.append(prerequisite)

        statuses = self.statuses(student_id)
        ordered_ids = sorted(relevant, key=lambda key: concepts[key].get("order", 0))
        next_concept = self.recommendation(target_id, relevant, concepts, children, statuses)
        return {
            "nodes": [
                {
                    "id": concept_id,
                    "name": concepts[concept_id]["name"],
                    "status": statuses.get(concept_id, "unknown"),
                }
                for concept_id in ordered_ids
            ],
            "edges": [
                {"source": source, "target": target, "type": "REQUIRES"}
                for source, target in edges
                if source in relevant and target in relevant
            ],
            "target": target_id,
            "next_concept": next_concept,
        }

    @staticmethod
    def recommendation(
        target_id: str,
        relevant: set[str],
        concepts: dict[str, dict],
        children: dict[str, list[str]],
        statuses: dict[str, str],
    ) -> str:
        if statuses.get(target_id) == "demonstrated":
            return target_id
        outstanding = [
            concept_id
            for concept_id in relevant
            if statuses.get(concept_id, "unknown") != "demonstrated"
        ]
        if not outstanding:
            return target_id
        # Follow prerequisite order: if an early gap remains, learn it before its dependents.
        outstanding.sort(key=lambda key: (concepts[key].get("order", 0), key))
        return outstanding[0]

    def _status(self, scores: list[float]) -> str:
        if not scores:
            return "unknown"
        recent_mean = sum(scores[-5:]) / min(len(scores), 5)
        return "demonstrated" if recent_mean >= self.settings.mastery_threshold else "needs_review"
