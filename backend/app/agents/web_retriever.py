import time
from typing import Any

from app.agents.base import BaseAgent
from app.schemas.state import ResearchState
from app.services.tavily_service import TavilySearchService


class WebResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Web Research Agent")
        self.tavily = TavilySearchService()

    def run(self, state: ResearchState) -> dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "")

        try:
            web_results = self.tavily.search_web(query=objective, max_results=5)
            status = "completed"
        except Exception as e:  # noqa: BLE001
            web_results = []
            status = "partial_failure"
            self.log_execution("warning", start_time, f"Tavily web search failed: {e}")

        log = self.log_execution(
            status=status,
            start_time=start_time,
            reasoning=f"Retrieved {len(web_results)} web search results and technical articles via Tavily.",
            details={"web_results_count": len(web_results)}
        )

        return {
            "retrieved_web_sources": web_results,
            "agent_logs": [log]
        }
