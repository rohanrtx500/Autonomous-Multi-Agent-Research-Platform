import time
from typing import Any

from app.agents.base import BaseAgent
from app.schemas.state import ResearchState
from app.services.github_service import GitHubSearchService

TECHNICAL_KEYWORDS = {
    "code", "github", "repo", "repository", "software", "algorithm", "model",
    "framework", "library", "api", "python", "javascript", "deep learning",
    "machine learning", "neural", "rag", "langgraph", "fastapi", "docker",
    "database", "architecture", "implementation", "pipeline", "benchmark",
    "dataset", "agent", "llm", "ai", "nlp", "computer vision", "frontend", "backend",
    "moe", "mixture of experts", "transformer", "deep", "embedding", "vector"
}


class GitHubResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="GitHub Research Agent")
        self.github = GitHubSearchService()

    def run(self, state: ResearchState) -> dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "")

        # Skip GitHub search for non-software / non-technical topics (lifestyle, history, culture, etc.)
        is_technical = any(kw in objective.lower() for kw in TECHNICAL_KEYWORDS)
        if not is_technical:
            log = self.log_execution(
                status="completed",
                start_time=start_time,
                reasoning=f"Objective '{objective}' is non-technical. Skipping GitHub repository search to maintain domain purity.",
                details={"repo_count": 0, "skipped": True}
            )
            return {
                "retrieved_github_repos": [],
                "agent_logs": [log]
            }

        try:
            repos = self.github.search_repositories(query=objective, max_results=5)
            status = "completed"
        except Exception as e:  # noqa: BLE001
            repos = []
            status = "partial_failure"
            self.log_execution("warning", start_time, f"GitHub search failed: {e}")

        log = self.log_execution(
            status=status,
            start_time=start_time,
            reasoning=f"Retrieved {len(repos)} GitHub repositories and codebases.",
            details={"repo_count": len(repos)}
        )

        return {
            "retrieved_github_repos": repos,
            "agent_logs": [log]
        }
