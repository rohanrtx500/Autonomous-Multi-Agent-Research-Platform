from typing import Annotated, Any, TypedDict

from app.schemas.evaluation import AgentExecutionLog, EvaluationMetrics
from app.schemas.research import (
    ExperimentRecommendation,
    MethodComparison,
    ResearchGap,
    ResearchReport,
    ResearchSubTask,
)
from app.schemas.source import GitHubRepoItem, PaperItem, SourceDocument


def log_reducer(left: list[AgentExecutionLog], right: list[AgentExecutionLog]) -> list[AgentExecutionLog]:
    if not left:
        return right or []
    if not right:
        return left
    return left + right


def paper_reducer(left: list[PaperItem], right: list[PaperItem]) -> list[PaperItem]:
    if not left:
        return right or []
    if not right:
        return left
    seen = {p.title.lower() for p in left}
    res = list(left)
    for p in right:
        if p.title.lower() not in seen:
            seen.add(p.title.lower())
            res.append(p)
    return res


def web_reducer(left: list[SourceDocument], right: list[SourceDocument]) -> list[SourceDocument]:
    if not left:
        return right or []
    if not right:
        return left
    return left + right


def repo_reducer(left: list[GitHubRepoItem], right: list[GitHubRepoItem]) -> list[GitHubRepoItem]:
    if not left:
        return right or []
    if not right:
        return left
    return left + right


def doc_reducer(left: list[SourceDocument], right: list[SourceDocument]) -> list[SourceDocument]:
    if not left:
        return right or []
    if not right:
        return left
    return left + right


class ResearchState(TypedDict, total=False):
    job_id: str
    objective: str
    sub_tasks: list[ResearchSubTask]
    
    # Parallel Retrieved Raw Data with Reducers
    retrieved_papers: Annotated[list[PaperItem], paper_reducer]
    retrieved_web_sources: Annotated[list[SourceDocument], web_reducer]
    retrieved_github_repos: Annotated[list[GitHubRepoItem], repo_reducer]
    retrieved_user_docs: Annotated[list[SourceDocument], doc_reducer]
    
    # Synthesized & Analyzed Knowledge
    synthesized_knowledge: dict[str, Any]
    method_comparisons: list[MethodComparison]
    research_gaps: list[ResearchGap]
    experiment_plan: list[ExperimentRecommendation]
    
    # Output & Feedback
    draft_report: ResearchReport | None
    final_report_markdown: str | None
    critic_feedback: str | None
    citation_verification: dict[str, Any] | None
    evaluation_metrics: EvaluationMetrics | None
    
    # Control Loop & Telemetry
    iteration_count: int
    max_iterations: int
    status: str
    agent_logs: Annotated[list[AgentExecutionLog], log_reducer]
    error_message: str | None
