import time
from typing import Any

from app.agents.base import BaseAgent
from app.schemas.state import ResearchState
from app.services.github_service import GitHubSearchService


class GitHubResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="GitHub Research Agent")
        self.github = GitHubSearchService()

    def run(self, state: ResearchState) -> dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "")

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
