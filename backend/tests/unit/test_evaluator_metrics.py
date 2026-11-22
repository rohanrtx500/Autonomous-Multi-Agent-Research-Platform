from app.agents.evaluator import EvaluationAgent
from app.schemas.research import ResearchReport
from app.schemas.source import PaperItem
from app.schemas.state import ResearchState


def test_evaluator_measurable_ir_metrics():
    agent = EvaluationAgent()

    papers = [
        PaperItem(
            id="p1",
            title="Quantum Computing Grid Optimization",
            authors=["Alice"],
            abstract="Quantum computing algorithms for power grid optimization and renewable distribution balancing.",
            url="https://arxiv.org/abs/2401.0001"
        ),
        PaperItem(
            id="p2",
            title="Classical Grid Distribution",
            authors=["Bob"],
            abstract="Power grid management and optimization under transmission congestion.",
            url="https://arxiv.org/abs/2401.0002"
        ),
        PaperItem(
            id="p3",
            title="Marine Biology in Deep Oceans",
            authors=["Charlie"],
            abstract="Coral reef ecosystems under thermal variations in tropical zones.",
            url="https://arxiv.org/abs/2401.0003"
        )
    ]

    report = ResearchReport(
        title="Report: Quantum Grid Optimization",
        executive_summary="Quantum algorithms for power grid optimization.",
        problem_statement="Grid stability challenges.",
        key_findings=["Quantum optimization significantly reduces grid transmission losses."],
        full_markdown="# Comprehensive Research Report: Quantum Grid Optimization\n\nExecutive Summary of Quantum Grid Optimization..."
    )

    citation_verif = {
        "total_claims": 2,
        "supported_claims": 2,
        "partially_supported_claims": 0,
        "unsupported_claims": 0,
        "unverified_claims": 0,
        "citation_coverage": 1.0,
        "citation_correctness": 1.0,
        "unsupported_claim_rate": 0.0,
        "grounding_confidence": 1.0
    }

    state: ResearchState = {
        "job_id": "test_eval_01",
        "objective": "Quantum Computing Grid Optimization",
        "retrieved_papers": papers,
        "retrieved_web_sources": [],
        "retrieved_user_docs": [],
        "draft_report": report,
        "citation_verification": citation_verif,
        "critic_feedback": "Quality verified.",
        "agent_logs": []
    }

    res = agent.run(state)
    metrics = res["evaluation_metrics"]

    assert metrics.precision_at_k is not None
    assert metrics.precision_at_k > 0.5  # At least 2 of 3 sources are relevant
    assert metrics.mrr == 1.0  # Top ranked item is relevant
    assert metrics.recall_at_k is not None
    assert metrics.faithfulness_score == 1.0
    assert metrics.answer_relevance is not None
    assert metrics.answer_relevance > 0.0
    assert metrics.is_acceptable is True
    assert "precision_at_k" in metrics.deterministic_metrics


def test_evaluator_missing_data_handling():
    agent = EvaluationAgent()

    # Empty state without retrieved sources or report
    state: ResearchState = {
        "job_id": "test_eval_empty",
        "objective": "Unknown Objective",
        "retrieved_papers": [],
        "retrieved_web_sources": [],
        "retrieved_user_docs": [],
        "draft_report": None,
        "citation_verification": {},
        "agent_logs": []
    }

    res = agent.run(state)
    metrics = res["evaluation_metrics"]

    # Must return None for retrieval metrics instead of fabricating numbers
    assert metrics.precision_at_k is None
    assert metrics.recall_at_k is None
    assert metrics.mrr is None
    assert metrics.faithfulness_score == 0.0
    assert metrics.is_acceptable is False
