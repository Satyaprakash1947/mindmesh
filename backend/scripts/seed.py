import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.graph import db, queries
from app.graph.seed_data import CONCEPTS, REQUIRES
from app.settings import get_settings


def main() -> None:
    settings = get_settings()
    if not (settings.neo4j_uri and settings.neo4j_username and settings.neo4j_password):
        raise SystemExit("Set NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD before seeding.")
    driver = db.connect(settings)
    if driver is None:
        raise SystemExit("Could not connect to Neo4j Aura. Check the configured credentials.")
    try:
        for query in queries.CREATE_CONSTRAINTS:
            db.run_query(driver, settings.neo4j_database, query)
        for concept in CONCEPTS:
            db.run_query(
                driver,
                settings.neo4j_database,
                queries.UPSERT_CONCEPT,
                {"id": concept["id"], "properties": concept},
            )
        for prerequisite, target in REQUIRES:
            db.run_query(
                driver,
                settings.neo4j_database,
                queries.UPSERT_REQUIRES,
                {"source": prerequisite, "target": target},
            )
    finally:
        driver.close()
    print(f"Seeded {len(CONCEPTS)} concepts and {len(REQUIRES)} prerequisite edges.")


if __name__ == "__main__":
    main()
