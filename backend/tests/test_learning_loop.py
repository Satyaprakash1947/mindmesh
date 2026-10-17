def test_answer_updates_mastery_and_recommendation(client):
    before = client.get("/api/graph/gradient_descent?student_id=learner-1").json()
    assert before["next_concept"] == "functions"

    updated = client.post(
        "/api/mastery/update",
        json={
            "student_id": "learner-1",
            "concept_id": "functions",
            "answer": "Each input has exactly one output.",
            "score": 0.95,
            "feedback": "Correct",
            "target_concept_id": "gradient_descent",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "demonstrated"
    assert updated.json()["next_concept"] == "linear_functions"


def test_scored_answer_is_recorded(client):
    response = client.post(
        "/api/answer",
        json={
            "student_id": "learner-2",
            "concept_id": "derivatives",
            "target_concept_id": "gradient_descent",
            "answer": "At x equals a, the derivative is the limit of secant slopes and gives the instantaneous rate of change and slope of the tangent line.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["score"] <= 1
    assert body["status"] == "demonstrated"
    assert body["next_concept"] == "functions"
