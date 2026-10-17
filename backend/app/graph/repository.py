from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from neo4j import Driver

from app.graph import db, queries
from app.graph.mastery import mastery_status, recommend_next
from app.graph.seed_data import CONCEPTS, REQUIRES
from app.settings import Settings


class GraphRepository:
    """Neo4j-backed concept store with the same deterministic memory fallback."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.driver: Driver | None = db.connect(settings)
        self._concepts = {concept["id"]: dict(concept) for concept in CONCEPTS}
        self._requires = list(REQUIRES)
        self._attempts: list[dict] = []
        self.backend = "neo4j" if self.driver else "memory"

    def close(self) -> None:
        if self.driver:
            self.driver.close()

    def all_concepts(self) -> list[dict]:
        if not self.driver:
            return sorted(self._concepts.values(), key=lambda item: item["order"])
        records = db.run_query(
            self.driver, self.settings.neo4j_database, queries.ALL_CONCEPTS
        )
        return [dict(record["c"]) for record in records]

    def all_edges(self) -> list[tuple[str, str]]:
        if not self.driver:
            return list(self._requires)
        records = db.run_query(
            self.driver, self.settings.neo4j_database, queries.ALL_EDGES
        )
        return [(record["source"], record["target"]) for record in records]

    def get_concept(self, concept_id: str) -> dict | None:
        if not self.driver:
            return self._concepts.get(concept_id)
        records = db.run_query(
            self.driver,
            self.settings.neo4j_database,
            queries.GET_CONCEPT,
            {"id": concept_id},
        )
        return dict(records[0]["c"]) if records else None

    def statuses(self, student_id: str) -> dict[str, str]:
        if self.driver:
            records = db.run_query(
                self.driver,
                self.settings.neo4j_database,
                queries.MASTERY_STATUSES,
                {
                    "student_id": student_id,
                    "review_threshold": 0.5,
                    "mastery_threshold": self.settings.mastery_threshold,
                },
            )
            return {record["id"]: record["status"] for record in records}

        scores_by_concept: dict[str, list[float]] = {}
        for attempt in self._attempts:
            if attempt["student_id"] == student_id:
                scores_by_concept.setdefault(attempt["concept_id"], []).append(
                    attempt["score"]
                )
        return {
            concept_id: mastery_status(
                scores_by_concept.get(concept_id, []), self.settings.mastery_threshold
            )
            for concept_id in self._concepts
        }

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
        db.run_query(
            self.driver,
            self.settings.neo4j_database,
            queries.CREATE_ATTEMPT,
            attempt,
        )

    def status_for(self, student_id: str, concept_id: str) -> str:
        return self.statuses(student_id).get(concept_id, "unknown")

    def graph_for_target(self, student_id: str, target_id: str) -> dict:
        concepts = {item["id"]: item for item in self.all_concepts()}
        if target_id not in concepts:
            raise KeyError(target_id)
        edges = self.all_edges()
        relevant = {target_id}
        pending = [target_id]
        prerequisites: dict[str, list[str]] = {}
        for prerequisite, target in edges:
            prerequisites.setdefault(target, []).append(prerequisite)
        while pending:
            current = pending.pop()
            for prerequisite in prerequisites.get(current, []):
                if prerequisite not in relevant:
                    relevant.add(prerequisite)
                    pending.append(prerequisite)

        statuses = self.statuses(student_id)
        ordered_ids = sorted(relevant, key=lambda key: concepts[key].get("order", 0))
        next_concept, next_reason = recommend_next(
            target_id, concepts, edges, statuses
        )
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
            "next_reason": next_reason,
        }
