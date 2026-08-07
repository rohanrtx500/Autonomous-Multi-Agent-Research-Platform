import pytest
from app.graph.workflow import research_graph
from app.schemas.state import ResearchState


def test_full_langgraph_research_workflow():
    initial_state: ResearchState = {
        "job_id": "integration_test_101",
        "objective": "Autonomous AI Research Frameworks in 2026",
        "sub_tasks": [],
        "retrieved_papers": [],
        "retrieved_web_sources": [],
        "retrieved_github_repos": [],
        "retrieved_user_docs": [],
        "synthesized_knowledge": {},
        "method_comparisons": [],
        "research_gaps": [],
        "experiment_plan": [],
        "iteration_count": 0,
        "max_iterations": 2,
        "status": "planning",
        "agent_logs": []
    }

    final_state = research_graph.invoke(initial_state)

    assert final_state["status"] in ["completed", "refining"]
    assert len(final_state["agent_logs"]) >= 10
    assert final_state["final_report_markdown"] is not None
    assert "Comprehensive Research Report" in final_state["final_report_markdown"]
    assert final_state["evaluation_metrics"] is not None
