import time
from typing import Any

from app.agents.base import BaseAgent
from app.schemas.state import ResearchState


class KnowledgeSynthesizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Knowledge Synthesizer")

    def run(self, state: ResearchState) -> dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "Research Objective")

        papers = state.get("retrieved_papers", [])
        web = state.get("retrieved_web_sources", [])
        repos = state.get("retrieved_github_repos", [])
        user_docs = state.get("retrieved_user_docs", [])

        themes: list[str] = [
            f"Core Dimensions & Foundations of {objective}",
            "Comparative Dynamics & Empirical Perspectives",
            "Socioeconomic & Practical Real-World Implications",
            "Key Trade-Offs & Open Questions",
        ]

        top_insights = []
        if web:
            top_insights.append(
                f"Web evidence highlights {len(web)} authoritative sources discussing real-world experiences, practical benchmarks, and contemporary insights."
            )
        if papers:
            top_insights.append(
                f"Academic literature provides {len(papers)} formal research studies investigating underlying causal factors and systematic indicators."
            )
        if user_docs:
            top_insights.append(
                f"Internal knowledge base contributes {len(user_docs)} specialized reference excerpts."
            )
        if not top_insights:
            top_insights.append(f"Synthesizing qualitative and quantitative indicators for '{objective}'.")

        synthesized: dict[str, Any] = {
            "objective": objective,
            "total_evidence_count": len(papers) + len(web) + len(repos) + len(user_docs),
            "key_themes": themes,
            "evidence_breakdown": {
                "academic_papers_count": len(papers),
                "web_articles_count": len(web),
                "github_repos_count": len(repos),
                "user_documents_count": len(user_docs),
            },
            "top_insights": top_insights
        }

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=f"Synthesized evidence from {synthesized['total_evidence_count']} sources across active data streams.",
            details={"themes_count": len(themes)}
        )

        return {
            "synthesized_knowledge": synthesized,
            "status": "comparing",
            "agent_logs": [log]
        }
