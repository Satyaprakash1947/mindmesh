"""Pure mastery and recommendation logic shared by Neo4j and memory mode."""

from collections import deque
from collections.abc import Iterable, Mapping

from app.models.schemas import MasteryStatus

REVIEW_SCORE_THRESHOLD = 0.5
MASTERY_WINDOW = 2


def mastery_status(scores: Iterable[float], threshold: float = 0.7) -> MasteryStatus:
    """Classify attempts using the latest score and mean of the latest two scores."""
    recent = [float(score) for score in scores][-MASTERY_WINDOW:]
    if not recent:
        return "unknown"
    if recent[-1] < REVIEW_SCORE_THRESHOLD:
        return "needs_review"
    if sum(recent) / len(recent) >= threshold:
        return "demonstrated"
    return "needs_review"


def recommend_next(
    target_id: str,
    concepts: Mapping[str, dict],
    edges: Iterable[tuple[str, str]],
    statuses: Mapping[str, str],
) -> tuple[str, str]:
    """Return the closest unlocked unmet prerequisite and explain its path to target."""
    prerequisite_map: dict[str, list[str]] = {}
    child_map: dict[str, list[str]] = {}
    for prerequisite, target in edges:
        prerequisite_map.setdefault(target, []).append(prerequisite)
        child_map.setdefault(prerequisite, []).append(target)

    if statuses.get(target_id) == "demonstrated":
        return target_id, "The target concept is already demonstrated."

    distance = {target_id: 0}
    pending = deque([target_id])
    while pending:
        current = pending.popleft()
        for prerequisite in prerequisite_map.get(current, []):
            if prerequisite not in distance:
                distance[prerequisite] = distance[current] + 1
                pending.append(prerequisite)

    eligible = [
        concept_id
        for concept_id in distance
        if concept_id != target_id
        and statuses.get(concept_id, "unknown") != "demonstrated"
        and all(
            statuses.get(prerequisite, "unknown") == "demonstrated"
            for prerequisite in prerequisite_map.get(concept_id, [])
        )
    ]
    if eligible:
        eligible.sort(
            key=lambda concept_id: (
                distance[concept_id],
                concepts.get(concept_id, {}).get("order", 0),
                concept_id,
            )
        )
        next_id = eligible[0]
        path = _path_to_target(next_id, target_id, child_map, concepts)
        names = [concepts[concept_id]["name"] for concept_id in path]
        if len(names) == 2:
            reason = f"{names[0]} is required for {names[1]}."
        else:
            reason = f"{names[0]} is required for " + ", which is required for ".join(names[1:]) + "."
        return next_id, reason

    target_ready = all(
        statuses.get(prerequisite, "unknown") == "demonstrated"
        for prerequisite in prerequisite_map.get(target_id, [])
    )
    if target_ready:
        return target_id, "All prerequisites are demonstrated; the target is ready."
    return target_id, "No unmet prerequisite is currently available to learn."


def _path_to_target(
    start_id: str,
    target_id: str,
    child_map: Mapping[str, list[str]],
    concepts: Mapping[str, dict],
) -> list[str]:
    pending = deque([(start_id, [start_id])])
    visited = {start_id}
    while pending:
        current, path = pending.popleft()
        if current == target_id:
            return path
        children = sorted(
            child_map.get(current, []),
            key=lambda concept_id: (
                concepts.get(concept_id, {}).get("order", 0),
                concept_id,
            ),
        )
        for child in children:
            if child not in visited:
                visited.add(child)
                pending.append((child, [*path, child]))
    return [start_id, target_id]
