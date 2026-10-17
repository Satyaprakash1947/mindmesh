import httpx

from app.ai.service import TutorService, evaluate_answer
from app.settings import Settings


def test_rubric_evaluation_returns_score_feedback_and_point_breakdown():
    result = evaluate_answer(
        "A function gives exactly one output for each input.",
        [
            "each input has exactly one output",
            "one input cannot map to two outputs",
            "input output relationship",
        ],
    )

    assert result["score"] == 0.67
    assert result["matched_points"] == [
        "each input has exactly one output",
        "input output relationship",
    ]
    assert result["missing_points"] == ["one input cannot map to two outputs"]
    assert "part of it" in result["feedback"]


def test_function_rubric_accepts_concise_correct_definition():
    result = evaluate_answer(
        "A function gives exactly one output for each input.",
        ["each input has exactly one output"],
    )

    assert result["score"] == 1.0
    assert result["matched_points"] == ["each input has exactly one output"]
    assert result["missing_points"] == []


def test_function_rubric_rejects_answer_that_allows_multiple_outputs():
    result = evaluate_answer(
        "A function can give many outputs for the same input.",
        ["each input has exactly one output"],
    )

    assert result["score"] == 0.0
    assert result["matched_points"] == []
    assert result["missing_points"] == ["each input has exactly one output"]


def test_empty_or_whitespace_rubric_does_not_divide_by_zero():
    result = evaluate_answer("some answer", ["", "  "])

    assert result == {
        "score": 0.0,
        "feedback": "There is no answer rubric for this concept yet.",
        "matched_points": [],
        "missing_points": [],
    }


def test_tutor_uses_mock_material_without_provider_credentials():
    tutor = TutorService(Settings(_env_file=None))

    result = tutor.teaching_material(
        {"name": "Slope", "explanation": "Reference explanation", "worked_example": "Reference example"}
    )

    assert result == {
        "explanation": "Reference explanation",
        "worked_example": "Reference example",
        "provider": "mock",
    }


def test_tutor_falls_back_when_provider_returns_invalid_material(monkeypatch):
    tutor = TutorService(
        Settings(
            _env_file=None,
            llm_api_base="https://llm.example/v1",
            llm_api_key="test-key",
        )
    )
    response = httpx.Response(
        200,
        json={"choices": [{"message": {"content": '{"explanation":"  ","worked_example":[]}'}}]},
        request=httpx.Request("POST", "https://llm.example/v1/chat/completions"),
    )
    monkeypatch.setattr("app.ai.service.httpx.post", lambda *args, **kwargs: response)

    result = tutor.teaching_material(
        {"name": "Slope", "explanation": "Reference explanation", "worked_example": "Reference example"}
    )

    assert result == {
        "explanation": "Reference explanation",
        "worked_example": "Reference example",
        "provider": "mock",
    }


def test_tutor_falls_back_when_provider_returns_non_object_json(monkeypatch):
    tutor = TutorService(
        Settings(
            _env_file=None,
            llm_api_base="https://llm.example/v1",
            llm_api_key="test-key",
        )
    )
    response = httpx.Response(
        200,
        json={"choices": [{"message": {"content": "[]"}}]},
        request=httpx.Request("POST", "https://llm.example/v1/chat/completions"),
    )
    monkeypatch.setattr("app.ai.service.httpx.post", lambda *args, **kwargs: response)

    result = tutor.teaching_material(
        {"name": "Slope", "explanation": "Reference explanation", "worked_example": "Reference example"}
    )

    assert result["provider"] == "mock"
    assert result["explanation"] == "Reference explanation"


def test_tutor_falls_back_on_provider_error(monkeypatch):
    tutor = TutorService(
        Settings(
            _env_file=None,
            llm_api_base="https://llm.example/v1",
            llm_api_key="test-key",
        )
    )

    def raise_timeout(*args, **kwargs):
        raise httpx.TimeoutException("provider timed out")

    monkeypatch.setattr("app.ai.service.httpx.post", raise_timeout)
    result = tutor.teaching_material(
        {"name": "Slope", "explanation": "Reference explanation", "worked_example": "Reference example"}
    )

    assert result["provider"] == "mock"
    assert result["explanation"] == "Reference explanation"
    assert result["worked_example"] == "Reference example"
