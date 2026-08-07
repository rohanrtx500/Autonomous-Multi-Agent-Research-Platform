import time
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.schemas.state import ResearchState


class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Critic Agent")

    def run(self, state: ResearchState) -> Dict[str, Any]:
        start_time = time.time()
        report = state.get("draft_report")

        if not report or not report.full_markdown:
            feedback = "Draft report is missing content."
            return {
                "critic_feedback": feedback,
                "agent_logs": []
            }

        word_count = len(report.full_markdown.split())
        has_comparisons = len(report.method_comparison) > 0
        has_gaps = len(report.research_gaps) > 0
        has_refs = len(report.references) > 0

        feedback_items = []
        if word_count < 300:
            feedback_items.append("Expand sections with deeper technical details.")
        if not has_comparisons:
            feedback_items.append("Add structured method comparison matrix.")
        if not has_gaps:
            feedback_items.append("Include open research gaps.")
        if not has_refs:
            feedback_items.append("Include formal academic citations.")

        critic_summary = "Quality verified." if not feedback_items else "; ".join(feedback_items)

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=f"Reviewed report structure and consistency. Summary: {critic_summary}",
            details={"critic_feedback": critic_summary, "word_count": word_count}
        )

        return {
            "critic_feedback": critic_summary,
            "status": "evaluating",
            "agent_logs": [log]
        }
