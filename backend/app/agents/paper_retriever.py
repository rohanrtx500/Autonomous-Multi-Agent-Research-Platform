import time
from typing import Any

from app.agents.base import BaseAgent
from app.schemas.state import ResearchState
from app.services.arxiv_service import ArxivService
from app.services.semantic_scholar_service import SemanticScholarService


class PaperRetrievalAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Paper Retrieval Agent")
        self.arxiv = ArxivService()
        self.semantic_scholar = SemanticScholarService()

    def run(self, state: ResearchState) -> dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "")

        arxiv_papers = self.arxiv.search_papers(query=objective, max_results=3)
        s2_papers = self.semantic_scholar.search_papers(query=objective, limit=3)
        all_new_papers = arxiv_papers + s2_papers

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=f"Retrieved {len(arxiv_papers)} arXiv and {len(s2_papers)} Semantic Scholar papers.",
            details={"paper_count": len(all_new_papers)}
        )

        return {
            "retrieved_papers": all_new_papers,
            "agent_logs": [log]
        }
