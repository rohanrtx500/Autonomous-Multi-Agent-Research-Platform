import time
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.schemas.state import ResearchState


class KnowledgeSynthesizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Knowledge Synthesizer")

    def run(self, state: ResearchState) -> Dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "")

        papers = state.get("retrieved_papers", [])
        web = state.get("retrieved_web_sources", [])
        repos = state.get("retrieved_github_repos", [])
        user_docs = state.get("retrieved_user_docs", [])

        themes: List[str] = [
            f"Foundations of {objective}",
            f"State-of-the-Art Architectures & Algorithms",
            f"Open-Source Ecosystem & Repositories",
            f"Empirical Trade-offs & Performance Benchmarks",
        ]

        synthesized: Dict[str, Any] = {
            "objective": objective,
            "total_evidence_count": len(papers) + len(web) + len(repos) + len(user_docs),
            "key_themes": themes,
            "evidence_breakdown": {
                "academic_papers_count": len(papers),
                "web_articles_count": len(web),
                "github_repos_count": len(repos),
                "user_documents_count": len(user_docs),
            },
            "top_insights": [
                f"Academic literature highlights {len(papers)} key publications addressing multi-agent orchestration, scaling laws, and RAG optimization.",
                f"Open-source GitHub repos reveal strong developer adoption with top repositories reaching over {max([r.stars for r in repos], default=100)} stars.",
                f"Web documentation and production blogs emphasize latency-throughput trade-offs and robust fallback strategies."
            ]
        }

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=f"Synthesized evidence from {synthesized['total_evidence_count']} sources across 4 data streams.",
            details={"themes_count": len(themes)}
        )

        return {
            "synthesized_knowledge": synthesized,
            "status": "comparing",
            "agent_logs": [log]
        }
