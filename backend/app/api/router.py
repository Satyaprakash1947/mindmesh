from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException, Request

from app.ai.service import evaluate_answer
from app.models.schemas import (
    AnswerRequest,
    DiagnoseRequest,
    LearningNextRequest,
    LearningStartRequest,
    MasteryUpdateRequest,
)

router = APIRouter(prefix="/api")
LOW_CONFIDENCE = 0.35


def _runtime(request: Request):
    return request.app.state.runtime


def _match_concept(question: str, concepts: list[dict]) -> tuple[dict | None, float]:
    normalized = _normalize(question)
    if not normalized:
        return None, 0.0
    ranked: list[tuple[int, dict]] = []
    for concept in concepts:
        matches = sum(1 for keyword in concept.get("keywords", []) if _normalize(keyword) in normalized)
        ranked.append((matches, concept))
    matches, concept = max(ranked, key=lambda item: (item[0], item[1].get("order", 0)))
    confidence = min(1.0, matches * 0.45)
    return (concept, confidence) if matches else (None, 0.0)


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def _graph_response(runtime, student_id: str, target_id: str) -> dict:
    try:
        return runtime.graph.graph_for_target(student_id, target_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown concept: {target_id}") from exc


@router.get("/health")
def health(request: Request) -> dict:
    runtime = _runtime(request)
    return {"status": "ok", "graph_backend": runtime.graph.backend}


@router.get("/concepts")
def concepts(request: Request, student_id: str = "demo") -> dict:
    runtime = _runtime(request)
    statuses = runtime.graph.statuses(student_id)
    return {
        "concepts": [
            {
                "id": item["id"],
                "name": item["name"],
                "status": statuses.get(item["id"], "unknown"),
                "explanation": item["explanation"],
                "diagnostic_question": item["diagnostic_question"],
            }
            for item in runtime.graph.all_concepts()
        ]
    }


@router.get("/graph/{concept_id}")
def graph(concept_id: str, request: Request, student_id: str = "demo") -> dict:
    return _graph_response(_runtime(request), student_id, concept_id)


@router.post("/learning/start")
def learning_start(payload: LearningStartRequest, request: Request) -> dict:
    runtime = _runtime(request)
    concept = None
    confidence = 0.0
    if payload.target_concept_id:
        concept = runtime.graph.get_concept(payload.target_concept_id)
        if concept is None:
            raise HTTPException(status_code=404, detail=f"Unknown concept: {payload.target_concept_id}")
        confidence = 1.0
    else:
        concept, confidence = _match_concept(payload.question, runtime.graph.all_concepts())
    if concept is None or confidence < LOW_CONFIDENCE:
        return {
            "needs_topic_selection": True,
            "confidence": round(confidence, 2),
            "concepts": [
                {"id": item["id"], "name": item["name"]}
                for item in runtime.graph.all_concepts()
            ],
        }
    target_id = concept["id"]
    runtime.sessions[payload.student_id] = target_id
    graph_data = _graph_response(runtime, payload.student_id, target_id)
    current_id = graph_data["next_concept"] or target_id
    current = runtime.graph.get_concept(current_id)
    material = runtime.tutor.teaching_material(current)
    return {
        "needs_topic_selection": False,
        "target_concept_id": target_id,
        "confidence": round(confidence, 2),
        "graph": graph_data,
        "diagnostic": {
            "concept_id": current_id,
            "question": current["diagnostic_question"],
            **material,
        },
    }


@router.post("/diagnose")
def diagnose(payload: DiagnoseRequest, request: Request) -> dict:
    runtime = _runtime(request)
    concept = runtime.graph.get_concept(payload.concept_id)
    if concept is None:
        raise HTTPException(status_code=404, detail=f"Unknown concept: {payload.concept_id}")
    runtime.sessions.setdefault(payload.student_id, payload.concept_id)
    return {
        "student_id": payload.student_id,
        "concept_id": payload.concept_id,
        "question": concept["diagnostic_question"],
        **runtime.tutor.teaching_material(concept),
        "rubric": concept["rubric"],
    }


@router.post("/answer")
def answer(payload: AnswerRequest, request: Request) -> dict:
    runtime = _runtime(request)
    concept = runtime.graph.get_concept(payload.concept_id)
    if concept is None:
        raise HTTPException(status_code=404, detail=f"Unknown concept: {payload.concept_id}")
    evaluation = evaluate_answer(payload.answer, concept["rubric"])
    runtime.graph.record_attempt(
        payload.student_id,
        payload.concept_id,
        payload.answer,
        evaluation["score"],
        evaluation["feedback"],
    )
    target_id = payload.target_concept_id or runtime.sessions.get(payload.student_id, payload.concept_id)
    graph_data = _graph_response(runtime, payload.student_id, target_id)
    return {
        **evaluation,
        "status": runtime.graph.status_for(payload.student_id, payload.concept_id),
        "next_concept": graph_data["next_concept"] or target_id,
        "next_reason": graph_data["next_reason"],
        "graph": graph_data,
    }


@router.post("/learning/next")
def learning_next(payload: LearningNextRequest, request: Request) -> dict:
    runtime = _runtime(request)
    graph_data = _graph_response(runtime, payload.student_id, payload.target_concept_id)
    next_id = graph_data["next_concept"] or payload.target_concept_id
    concept = runtime.graph.get_concept(next_id)
    runtime.sessions[payload.student_id] = payload.target_concept_id
    return {
        "target_concept_id": payload.target_concept_id,
        "next_concept": next_id,
        "status": runtime.graph.status_for(payload.student_id, next_id),
        "next_reason": graph_data["next_reason"],
        "question": concept["diagnostic_question"],
        **runtime.tutor.teaching_material(concept),
        "graph": graph_data,
    }


@router.post("/mastery/update")
def mastery_update(payload: MasteryUpdateRequest, request: Request) -> dict:
    runtime = _runtime(request)
    if runtime.graph.get_concept(payload.concept_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown concept: {payload.concept_id}")
    runtime.graph.record_attempt(
        payload.student_id,
        payload.concept_id,
        payload.answer,
        payload.score,
        payload.feedback,
    )
    target_id = payload.target_concept_id or runtime.sessions.get(payload.student_id, payload.concept_id)
    graph_data = _graph_response(runtime, payload.student_id, target_id)
    return {
        "status": runtime.graph.status_for(payload.student_id, payload.concept_id),
        "next_concept": graph_data["next_concept"] or target_id,
        "next_reason": graph_data["next_reason"],
        "graph": graph_data,
    }
