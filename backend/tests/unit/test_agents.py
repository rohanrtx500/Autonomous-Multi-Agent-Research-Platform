import pytest
from app.schemas.state import ResearchState
from app.agents.planner import PlannerAgent
from app.agents.paper_retriever import PaperRetrievalAgent
from app.agents.web_retriever import WebResearchAgent
from app.agents.github_retriever import GitHubResearchAgent
from app.agents.doc_retriever import DocRetrievalAgent
from app.agents.synthesizer import KnowledgeSynthesizerAgent
from app.agents.comparator import ComparisonAgent
from app.agents.gap_analyzer import ResearchGapAnalyzerAgent
from app.agents.experiment_planner import ExperimentPlannerAgent
from app.agents.writer import WriterAgent
from app.agents.critic import CriticAgent
from app.agents.citation_verifier import CitationVerificationAgent
from app.agents.evaluator import EvaluationAgent


@pytest.fixture
def base_state() -> ResearchState:
    return {
        "job_id": "test_agent_job",
        "objective": "Deep Research on Mixture of Experts (MoE)",
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


def test_planner_agent(base_state):
    planner = PlannerAgent()
    res = planner.run(base_state)
    assert len(res["sub_tasks"]) == 4
    assert res["status"] == "retrieving"


def test_retrieval_agents(base_state):
    paper_agent = PaperRetrievalAgent()
    web_agent = WebResearchAgent()
    github_agent = GitHubResearchAgent()
    doc_agent = DocRetrievalAgent()

    s1 = paper_agent.run(base_state)
    assert len(s1["retrieved_papers"]) > 0

    s2 = web_agent.run(base_state)
    assert len(s2["retrieved_web_sources"]) > 0

    s3 = github_agent.run(base_state)
    assert len(s3["retrieved_github_repos"]) > 0

    s4 = doc_agent.run(base_state)
    assert "retrieved_user_docs" in s4
    assert len(s4["agent_logs"]) == 1


def test_synthesis_and_reasoning_agents(base_state):
    synth = KnowledgeSynthesizerAgent()
    comp = ComparisonAgent()
    gap = ResearchGapAnalyzerAgent()
    exp = ExperimentPlannerAgent()

    s1 = synth.run(base_state)
    assert "total_evidence_count" in s1["synthesized_knowledge"]

    s2 = comp.run(base_state)
    assert len(s2["method_comparisons"]) > 0

    s3 = gap.run(base_state)
    assert len(s3["research_gaps"]) > 0

    s4 = exp.run(base_state)
    assert len(s4["experiment_plan"]) > 0


def test_writer_critic_evaluator_agents(base_state):
    writer = WriterAgent()
    critic = CriticAgent()
    citation = CitationVerificationAgent()
    evaluator = EvaluationAgent()

    s1 = writer.run(base_state)
    assert s1["draft_report"] is not None

    s2 = critic.run(s1)
    assert s2["critic_feedback"] is not None

    s3 = citation.run(s2)
    assert s3["citation_verification"] is not None

    s4 = evaluator.run(s3)
    assert s4["evaluation_metrics"] is not None
    assert s4["evaluation_metrics"].confidence_score > 0.0
