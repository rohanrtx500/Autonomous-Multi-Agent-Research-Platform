import time
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.services.github_service import GitHubSearchService
from app.schemas.state import ResearchState


class GitHubResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="GitHub Research Agent")
        self.github = GitHubSearchService()

    def run(self, state: ResearchState) -> Dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "")

        repos = self.github.search_repositories(query=objective, max_results=5)

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=f"Retrieved {len(repos)} GitHub repositories and codebases.",
            details={"repo_count": len(repos)}
        )

        return {
            "retrieved_github_repos": repos,
            "agent_logs": [log]
        }
