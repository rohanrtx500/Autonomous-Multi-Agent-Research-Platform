import uuid
from app.infrastructure.job_repository import job_repository


def test_job_persistence_lifecycle():
    test_id = f"job_test_{uuid.uuid4().hex[:6]}"
    objective = "Empirical benchmark of KV cache compression"

    # 1. Create Job
    job = job_repository.create_job(job_id=test_id, objective=objective, max_iterations=2)
    assert job["job_id"] == test_id
    assert job["status"] == "pending"
    assert job["progress_percent"] == 5

    # 2. Update Progress
    job_repository.update_progress(
        job_id=test_id,
        status="running",
        progress_percent=50,
        current_step="synthesizer"
    )
    fetched = job_repository.get_job(test_id)
    assert fetched is not None
    assert fetched["status"] == "running"
    assert fetched["progress_percent"] == 50
    assert fetched["current_step"] == "synthesizer"

    # 3. Complete Job
    final_state = {
        "status": "completed",
        "iteration_count": 1,
        "final_report_markdown": "# Test Report Content",
        "evaluation_metrics": {"confidence_score": 0.92, "faithfulness_score": 0.95},
        "citation_verification": {"total_claims": 5, "supported_claims": 5},
        "retrieved_papers": [{"title": "Paper 1"}],
        "retrieved_web_sources": [],
        "retrieved_github_repos": [],
        "retrieved_user_docs": [],
        "agent_logs": [{"agent_name": "Planner", "status": "completed"}]
    }
    completed = job_repository.complete_job(test_id, final_state, execution_time_seconds=12.5)
    assert completed is not None
    assert completed["status"] == "completed"
    assert completed["progress_percent"] == 100
    assert completed["execution_time_seconds"] == 12.5
    assert completed["final_report_markdown"] == "# Test Report Content"


def test_job_cancellation():
    test_id = f"job_cancel_{uuid.uuid4().hex[:6]}"
    job_repository.create_job(job_id=test_id, objective="Job to be cancelled", max_iterations=2)

    # Cancel job
    cancelled = job_repository.cancel_job(test_id)
    assert cancelled is True

    fetched = job_repository.get_job(test_id)
    assert fetched["status"] == "cancelled"
    assert "cancelled by user" in fetched["error_message"]


def test_job_failure_recording():
    test_id = f"job_fail_{uuid.uuid4().hex[:6]}"
    job_repository.create_job(job_id=test_id, objective="Job destined to fail", max_iterations=2)

    job_repository.fail_job(test_id, "API quota exhausted on node 4")
    fetched = job_repository.get_job(test_id)
    assert fetched["status"] == "failed"
    assert "API quota exhausted" in fetched["error_message"]
