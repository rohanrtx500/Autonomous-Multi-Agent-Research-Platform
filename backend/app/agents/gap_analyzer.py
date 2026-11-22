import json
import re
import time
from typing import Any

from app.agents.base import BaseAgent
from app.schemas.research import ResearchGap
from app.schemas.state import ResearchState


class ResearchGapAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Research Gap Analyzer")

    def run(self, state: ResearchState) -> dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "Research Topic")
        papers = state.get("retrieved_papers", [])
        web = state.get("retrieved_web_sources", [])

        context_snippets = [w.content[:200] for w in web[:3]] + [p.abstract[:200] for p in papers[:2]]
        evidence_summary = "\n".join(context_snippets)

        gaps = []
        if self.llm:
            try:
                prompt = (
                    f"You are a Senior Strategic Researcher. For the topic: '{objective}', "
                    f"identify 2-3 critical gaps, unresolved friction points, or open analytical challenges.\n\n"
                    f"Available Reference Context:\n{evidence_summary}\n\n"
                    f"Return ONLY a JSON list of objects with fields:\n"
                    f"- title: (string, descriptive title of the gap or challenge)\n"
                    f"- area: (string, domain area, e.g. 'Healthcare Accessibility', 'Cultural Adaptation', 'Economic Disparities')\n"
                    f"- description: (string, 2 sentences explaining the specific friction or unresolved challenge)\n"
                    f"- severity: ('High' or 'Medium')\n"
                    f"- potential_impact: (string, why resolving or understanding this gap matters for individuals or policymakers)\n\n"
                    f"Respond with JSON only:"
                )
                res = self.llm.invoke(prompt)
                raw_text = self.extract_text(res)

                cleaned = raw_text.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[1].split("```")[0].strip()
                elif "```" in cleaned:
                    cleaned = cleaned.split("```")[1].split("```")[0].strip()

                match = re.search(r"\[\s*\{.*\}\s*\]", cleaned, re.DOTALL)
                if match:
                    cleaned = match.group(0)

                parsed = json.loads(cleaned)
                for item in parsed:
                    gaps.append(
                        ResearchGap(
                            title=item.get("title", "Unresolved Domain Problem"),
                            area=item.get("area", "Core Domain"),
                            description=item.get("description", "Further investigation is required to reconcile disparate findings."),
                            severity=item.get("severity", "High"),
                            potential_impact=item.get("potential_impact", "Clarifies core trade-offs and structural implications.")
                        )
                    )
            except Exception as e:  # noqa: BLE001
                self.log_execution("warning", start_time, f"LLM gap analysis failed: {e}. Using dynamic gaps.")

        if not gaps:
            gaps = self._dynamic_gaps(objective)

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=f"Identified {len(gaps)} critical research gaps and open challenges for '{objective}'.",
            details={"gaps_count": len(gaps)}
        )

        return {
            "research_gaps": gaps,
            "status": "experimenting",
            "agent_logs": [log]
        }

    def _dynamic_gaps(self, objective: str) -> list[ResearchGap]:
        obj_lower = objective.lower()

        if any(w in obj_lower for w in ["lifestyle", "usa", "india", "culture", "living", "cost", "work-life", "society"]):
            return [
                ResearchGap(
                    title="Healthcare Security Disparities and Medical Bankruptcy Risk",
                    area="Public Health & Financial Safety",
                    description="While the US boasts advanced medical technology, high deductible structures and employer-tied insurance leave individuals vulnerable to acute medical debt. Conversely, India's out-of-pocket healthcare expenses create accessibility divides between Tier-1 and rural communities.",
                    severity="High",
                    potential_impact="Informs long-term expatriate, retirement, and public healthcare policy planning across differing socioeconomic strata."
                ),
                ResearchGap(
                    title="Cross-Cultural Friction in Remote and Hybrid Work Environments",
                    area="Organizational Behavior",
                    description="Global tech collaboration between US and Indian teams often encounters implicit communication friction, differing expectations regarding overtime availability, and boundary disparities between professional autonomy and hierarchical deference.",
                    severity="Medium",
                    potential_impact="Enables global enterprises to optimize cross-border productivity without exacerbating employee burnout or turnover."
                )
            ]

        return [
            ResearchGap(
                title=f"Longitudinal Quality of Life and Adaptation Trajectories in {objective[:30]}",
                area="Empirical Research",
                description="Existing literature often relies on cross-sectional surveys rather than longitudinal studies tracking long-term psychological and economic outcomes.",
                severity="High",
                potential_impact="Provides robust empirical verification required for policy, clinical, or personal decision-making."
            ),
            ResearchGap(
                title="Socioeconomic Variance Across Heterogeneous Sub-Populations",
                area="Comparative Systems",
                description="Aggregate metrics frequently obscure sharp internal divides across urban, suburban, and regional demographic cohorts.",
                severity="Medium",
                potential_impact="Prevents over-generalization and enhances analytical granularity."
            )
        ]
