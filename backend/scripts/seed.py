from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from neo4j import GraphDatabase

from app.graph.seed_data import CONCEPTS, REQUIRES
from app.settings import get_settings


def main() -> None:
    settings = get_settings()
    if not (settings.neo4j_uri and settings.neo4j_username and settings.neo4j_password):
        raise SystemExit("Set NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD before seeding.")
    with GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    ) as driver:
        driver.verify_connectivity()
        with driver.session(database=settings.neo4j_database) as session:
            session.run(
                "CREATE CONSTRAINT concept_id IF NOT EXISTS "
                "FOR (c:Concept) REQUIRE c.id IS UNIQUE"
            ).consume()
            session.run(
                "CREATE CONSTRAINT student_id IF NOT EXISTS "
                "FOR (s:Student) REQUIRE s.id IS UNIQUE"
            ).consume()
            session.run(
                "CREATE CONSTRAINT attempt_id IF NOT EXISTS "
                "FOR (a:Attempt) REQUIRE a.id IS UNIQUE"
            ).consume()
            for concept in CONCEPTS:
                session.run(
                    "MERGE (c:Concept {id: $id}) SET c += $properties",
                    id=concept["id"],
                    properties=concept,
                ).consume()
            for prerequisite, target in REQUIRES:
                session.run(
                    "MATCH (source:Concept {id: $source}), (target:Concept {id: $target}) "
                    "MERGE (source)-[:REQUIRES]->(target)",
                    source=prerequisite,
                    target=target,
                ).consume()
    print(f"Seeded {len(CONCEPTS)} concepts and {len(REQUIRES)} prerequisite edges.")


if __name__ == "__main__":
    main()
