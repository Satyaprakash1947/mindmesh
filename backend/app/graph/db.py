"""Small Neo4j connection and parameterized query helpers."""

from typing import Any

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import Neo4jError

from app.settings import Settings


def connect(settings: Settings) -> Driver | None:
    """Connect to Neo4j when credentials are configured; otherwise use memory mode."""
    if not (settings.neo4j_uri and settings.neo4j_username and settings.neo4j_password):
        return None
    driver = None
    try:
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
        )
        driver.verify_connectivity()
    except (Neo4jError, ValueError):
        if driver is not None:
            driver.close()
        return None
    return driver


def run_query(
    driver: Driver,
    database: str,
    query: str,
    parameters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Run one Cypher statement with a parameter map and return plain dictionaries."""
    with driver.session(database=database) as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]
