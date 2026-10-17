"""Load the versioned seed graph used by both Neo4j and memory mode."""

import json
from pathlib import Path
from typing import Any

SEED_FILE = Path(__file__).resolve().parents[2] / "data" / "concepts.json"


def load_seed_data(path: Path = SEED_FILE) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
    """Read concepts and prerequisite edges from the repository's JSON seed file."""
    with path.open(encoding="utf-8") as seed_file:
        data = json.load(seed_file)
    concepts = data["concepts"]
    requires = [(edge[0], edge[1]) for edge in data["requires"]]
    return concepts, requires


CONCEPTS, REQUIRES = load_seed_data()
