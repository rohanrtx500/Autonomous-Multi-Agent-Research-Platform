import time
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.services.tavily_service import TavilySearchService
from app.schemas.state import ResearchState


class WebResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Web Research Agent")
        self.tavily = TavilySearchService()

    def run(self, state: ResearchState) -> Dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "")

        web_results = self.tavily.search_web(query=objective, max_results=5)

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=f"Retrieved {len(web_results)} web search results and technical articles via Tavily.",
            details={"web_results_count": len(web_results)}
        )

        return {
            "retrieved_web_sources": web_results,
            "agent_logs": [log]
        }
