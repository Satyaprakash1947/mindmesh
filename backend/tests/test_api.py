def test_root_explains_api_entry_points(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "name": "MindMesh API",
        "status": "ready",
        "docs": "/docs",
        "health": "/api/health",
    }


def test_health_reports_memory_demo_mode(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "graph_backend": "memory"}


def test_vite_loopback_origin_is_allowed(client):
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def test_graph_has_nodes_edges_and_target(client):
    response = client.get("/api/graph/gradient_descent?student_id=s1")
    assert response.status_code == 200
    data = response.json()
    assert {"id", "name", "status"}.issubset(data["nodes"][0])
    assert {"source", "target", "type"}.issubset(data["edges"][0])
    assert data["target"] == "gradient_descent"
    assert data["next_concept"] == "functions"


def test_unknown_concept_returns_404(client):
    response = client.get("/api/graph/not-a-concept")
    assert response.status_code == 404


def test_low_confidence_question_requests_topic_choice(client):
    response = client.post(
        "/api/learning/start",
        json={"student_id": "s1", "question": "Can you help me?"},
    )
    assert response.status_code == 200
    assert response.json()["needs_topic_selection"] is True
    assert len(response.json()["concepts"]) >= 10


def test_question_maps_to_gradient_descent(client):
    response = client.post(
        "/api/learning/start",
        json={
            "student_id": "s1",
            "question": "How do I use gradient descent to minimize a function?",
        },
    )
    assert response.status_code == 200
    assert response.json()["target_concept_id"] == "gradient_descent"
    assert response.json()["diagnostic"]["concept_id"] == "functions"
