from __future__ import annotations

import re

import httpx

from app.ai.prompts import TUTOR_SYSTEM_PROMPT
from app.settings import Settings


class TutorService:
    """Optional OpenAI-compatible tutor with deterministic local fallback."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def teaching_material(self, concept: dict) -> dict[str, str]:
        fallback = {
            "explanation": concept["explanation"],
            "worked_example": concept["worked_example"],
            "provider": "mock",
        }
        if not (self.settings.llm_api_base and self.settings.llm_api_key):
            return fallback
        try:
            response = httpx.post(
                f"{self.settings.llm_api_base.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.llm_api_key}"},
                json={
                    "model": self.settings.llm_model or "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": TUTOR_SYSTEM_PROMPT,
                        },
                        {
                            "role": "user",
                            "content": f"Concept: {concept['name']}\nReference: {concept['explanation']}\nExample: {concept['worked_example']}",
                        },
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2,
                },
                timeout=8.0,
            )
            response.raise_for_status()
            data = response.json()["choices"][0]["message"]["content"]
            import json

            generated = json.loads(data)
            return {
                "explanation": str(generated.get("explanation") or fallback["explanation"]),
                "worked_example": str(generated.get("worked_example") or fallback["worked_example"]),
                "provider": "llm",
            }
        except Exception:
            return fallback


def grade_answer(answer: str, rubric: list[str]) -> tuple[float, str]:
    """Score answer coverage against rubric points; always returns a bounded score."""
    answer_tokens = set(_tokens(answer))
    if not rubric:
        return 0.0, "There is no answer rubric for this concept yet."
    matched: list[str] = []
    missed: list[str] = []
    for point in rubric:
        significant = set(_tokens(point))
        if not significant:
            continue
        overlap = len(significant & answer_tokens) / len(significant)
        if point.casefold() in answer.casefold() or overlap >= 0.6:
            matched.append(point)
        else:
            missed.append(point)
    score = round(len(matched) / len(rubric), 2)
    if score >= 0.7:
        feedback = "Good work. Your answer covers the main idea."
    elif score > 0:
        feedback = "You have part of it. Revisit: " + "; ".join(missed[:2]) + "."
    else:
        feedback = "Try again after reviewing the explanation. Focus on: " + "; ".join(rubric[:2]) + "."
    return score, feedback


def _tokens(value: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", value.casefold()) if token not in _STOPWORDS]


_STOPWORDS = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "is", "it", "of", "on", "or", "the", "to", "with"}
