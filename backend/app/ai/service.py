from __future__ import annotations

import json
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
            generated = json.loads(data)
            if not isinstance(generated, dict):
                return fallback
            explanation = generated.get("explanation")
            worked_example = generated.get("worked_example")
            if not isinstance(explanation, str) or not explanation.strip():
                return fallback
            if not isinstance(worked_example, str) or not worked_example.strip():
                return fallback
            return {
                "explanation": explanation.strip(),
                "worked_example": worked_example.strip(),
                "provider": "llm",
            }
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
            return fallback


def evaluate_answer(answer: str, rubric: list[str]) -> dict:
    """Return a bounded, inspectable rubric evaluation for a learner answer."""
    usable_rubric = [point.strip() for point in rubric if point.strip()]
    if not usable_rubric:
        return {
            "score": 0.0,
            "feedback": "There is no answer rubric for this concept yet.",
            "matched_points": [],
            "missing_points": [],
        }

    answer = answer.strip()
    answer_tokens = set(_tokens(answer))
    normalized_answer = " ".join(_tokens(answer))
    matched: list[str] = []
    missed: list[str] = []
    for point in usable_rubric:
        significant = set(_tokens(point))
        if not significant:
            continue
        overlap = len(significant & answer_tokens) / len(significant)
        normalized_point = " ".join(_tokens(point))
        if (normalized_point and normalized_point in normalized_answer) or overlap >= 0.6:
            matched.append(point)
        else:
            missed.append(point)
    score = round(len(matched) / len(usable_rubric), 2)
    if score >= 0.7:
        feedback = "Good work. Your answer covers the main idea."
    elif score > 0:
        feedback = "You have part of it. Revisit: " + "; ".join(missed[:2]) + "."
    else:
        feedback = "Try again after reviewing the explanation. Focus on: " + "; ".join(usable_rubric[:2]) + "."
    return {
        "score": score,
        "feedback": feedback,
        "matched_points": matched,
        "missing_points": missed,
    }


def grade_answer(answer: str, rubric: list[str]) -> tuple[float, str]:
    """Compatibility wrapper for callers that only need score and feedback."""
    result = evaluate_answer(answer, rubric)
    return result["score"], result["feedback"]


def _tokens(value: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", value.casefold()) if token not in _STOPWORDS]


_STOPWORDS = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "is", "it", "of", "on", "or", "the", "to", "with"}
