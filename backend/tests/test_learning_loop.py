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
    assert updated.json()["next_concept"] == "loss_functions"
    assert updated.json()["next_reason"] == "Loss Functions is required for Gradient Descent."


def test_wrong_answer_then_correct_retest_changes_mastery_and_recommendation(client):
    target = "gradient_descent"
    before = client.get(f"/api/graph/{target}?student_id=learner-retest").json()
    assert before["next_concept"] == "functions"

    wrong = client.post(
        "/api/mastery/update",
        json={
            "student_id": "learner-retest",
            "concept_id": "functions",
            "answer": "An input can have two outputs.",
            "score": 0.41,
            "feedback": "Try again.",
            "target_concept_id": target,
        },
    )
    assert wrong.status_code == 200
    assert wrong.json()["status"] == "needs_review"
    assert wrong.json()["next_concept"] == "functions"

    retest = client.post(
        "/api/mastery/update",
        json={
            "student_id": "learner-retest",
            "concept_id": "functions",
            "answer": "Each input has exactly one output.",
            "score": 0.99,
            "feedback": "Correct.",
            "target_concept_id": target,
        },
    )
    assert retest.status_code == 200
    assert retest.json()["status"] == "demonstrated"
    assert retest.json()["next_concept"] == "loss_functions"
    assert retest.json()["next_reason"] == "Loss Functions is required for Gradient Descent."


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
    assert body["matched_points"]
    assert isinstance(body["missing_points"], list)
    assert body["status"] == "demonstrated"
    assert body["next_concept"] == "functions"
