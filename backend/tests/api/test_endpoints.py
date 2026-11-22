from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "ready"]
    assert data["service"] == "ResearchMind AI"
    assert "database" in data


def test_status_endpoint():
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert "system_status" in data
    assert "total_jobs_stored" in data


def test_research_endpoint_integration():
    payload = {
        "objective": "Survey of Multimodal LLMs",
        "max_iterations": 1
    }
    response = client.post("/api/v1/research", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"].startswith("job_")
    assert data["status"] in ["completed", "refining"]
    assert data["final_report_markdown"] is not None
    assert data["agent_logs_count"] > 0

    # Test persistent job retrieval
    job_id = data["job_id"]
    job_res = client.get(f"/api/v1/jobs/{job_id}")
    assert job_res.status_code == 200
    job_data = job_res.json()
    assert job_data["job_id"] == job_id
    assert job_data["status"] in ["completed", "refining"]
    assert job_data["final_report_markdown"] is not None


def test_metrics_endpoint():
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "faithfulness_avg" in data
    assert "status" in data
