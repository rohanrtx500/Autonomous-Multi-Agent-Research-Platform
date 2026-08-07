import operator
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from app.schemas.source import SourceDocument, PaperItem, GitHubRepoItem
from app.schemas.research import ResearchSubTask, MethodComparison, ResearchGap, ExperimentRecommendation, ResearchReport
from app.schemas.evaluation import EvaluationMetrics, AgentExecutionLog


def log_reducer(left: List[AgentExecutionLog], right: List[AgentExecutionLog]) -> List[AgentExecutionLog]:
    if not left:
        return right or []
    if not right:
        return left
    return left + right


def paper_reducer(left: List[PaperItem], right: List[PaperItem]) -> List[PaperItem]:
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


def web_reducer(left: List[SourceDocument], right: List[SourceDocument]) -> List[SourceDocument]:
    if not left:
        return right or []
    if not right:
        return left
    return left + right


def repo_reducer(left: List[GitHubRepoItem], right: List[GitHubRepoItem]) -> List[GitHubRepoItem]:
    if not left:
        return right or []
    if not right:
        return left
    return left + right


def doc_reducer(left: List[SourceDocument], right: List[SourceDocument]) -> List[SourceDocument]:
    if not left:
        return right or []
    if not right:
        return left
    return left + right


class ResearchState(TypedDict, total=False):
    job_id: str
    objective: str
    sub_tasks: List[ResearchSubTask]
    
    # Parallel Retrieved Raw Data with Reducers
    retrieved_papers: Annotated[List[PaperItem], paper_reducer]
    retrieved_web_sources: Annotated[List[SourceDocument], web_reducer]
    retrieved_github_repos: Annotated[List[GitHubRepoItem], repo_reducer]
    retrieved_user_docs: Annotated[List[SourceDocument], doc_reducer]
    
    # Synthesized & Analyzed Knowledge
    synthesized_knowledge: Dict[str, Any]
    method_comparisons: List[MethodComparison]
    research_gaps: List[ResearchGap]
    experiment_plan: List[ExperimentRecommendation]
    
    # Output & Feedback
    draft_report: Optional[ResearchReport]
    final_report_markdown: Optional[str]
    critic_feedback: Optional[str]
    citation_verification: Optional[Dict[str, Any]]
    evaluation_metrics: Optional[EvaluationMetrics]
    
    # Control Loop & Telemetry
    iteration_count: int
    max_iterations: int
    status: str
    agent_logs: Annotated[List[AgentExecutionLog], log_reducer]
    error_message: Optional[str]
