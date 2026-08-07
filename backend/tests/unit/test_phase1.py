from app.core.config import settings
from app.schemas.evaluation import EvaluationMetrics
from app.schemas.research import ResearchSubTask
from app.schemas.source import GitHubRepoItem, PaperItem, SourceDocument
from app.schemas.state import ResearchState


def test_config_initialization():
    assert settings.PROJECT_NAME == "ResearchMind AI"
    assert settings.VERSION == "1.0.0"
    assert settings.API_V1_STR == "/api/v1"


def test_schemas_instantiation():
    doc = SourceDocument(
        id="doc_1",
        title="Sample Paper",
        content="This is a test content",
        source_type="arxiv"
    )
    assert doc.id == "doc_1"

    paper = PaperItem(
        id="paper_1",
        title="Attention is All You Need",
        authors=["Vaswani et al."],
        abstract="Transformer architecture...",
        url="https://arxiv.org/abs/1706.03762"
    )
    assert paper.authors[0] == "Vaswani et al."

    repo = GitHubRepoItem(
        name="researchmind-ai",
        full_name="org/researchmind-ai",
        url="https://github.com/org/researchmind-ai",
        stars=100
    )
    assert repo.stars == 100

    task = ResearchSubTask(
        id="task_1",
        title="Literature Search",
        description="Search recent papers on RAG",
        assigned_agent="Paper Retrieval Agent"
    )
    assert task.status == "pending"

    metrics = EvaluationMetrics(
        faithfulness_score=0.95,
        relevance_score=0.90,
        grounding_score=0.92,
        confidence_score=0.94,
        is_acceptable=True
    )
    assert metrics.is_acceptable is True


def test_research_state_structure():
    state: ResearchState = {
        "job_id": "test_job_123",
        "objective": "Study of Agentic Workflows",
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
    assert state["job_id"] == "test_job_123"
    assert state["status"] == "planning"
