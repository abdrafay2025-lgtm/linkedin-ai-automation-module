from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"

def test_search_query_endpoint_invalid_input():
    response = client.post("/ai/search-query", json={"raw_keywords": "    "})
    assert response.status_code in (400, 422)

def test_personalize_endpoint_success():
    payload = {
        "template": "Hi {{FIRST_NAME}}, let's connect regarding {{HEADLINE}}.",
        "profile": {
            "first_name": "Hamza",
            "headline": "Software Architect",
            "connection_level": "1st"
        }
    }
    response = client.post("/ai/personalize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "Hamza" in data["personalized_message"]
    assert data["validation"]["status"] == "PASS"

def test_personalize_endpoint_rejects_non_first_degree():
    payload = {
        "template": "Hi {{FIRST_NAME}}, let's connect.",
        "profile": {
            "first_name": "Tariq",
            "connection_level": "2nd"
        }
    }
    response = client.post("/ai/personalize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILED"
    assert data["validation"]["status"] == "FAIL"
