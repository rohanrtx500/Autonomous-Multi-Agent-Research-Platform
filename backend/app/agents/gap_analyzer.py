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
                    f"CRITICAL DOMAIN DIRECTIVE:\n"
                    f"Focus EXCLUSIVELY on the actual subject matter of '{objective}'.\n"
                    f"Do NOT drift into AI, machine learning, deep learning, or computer science unless the topic explicitly asks about technology.\n"
                    f"Ground open questions in genuine domain context (e.g., social, cultural, medical, historical, or economic).\n\n"
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

        if any(w in obj_lower for w in ["usa vs india", "india vs usa", "american vs indian", "relocating to usa", "moving to india"]):
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

        # Health, Fitness & Physical Training
        if any(w in obj_lower for w in ["gym", "exercise", "workout", "fitness", "physical training", "health", "diet", "nutrition", "body"]):
            return [
                ResearchGap(
                    title="Optimal Training Frequency vs Overtraining Syndrome and Central Nervous System Recovery",
                    area="Exercise Physiology & Recovery",
                    description="While daily training builds habit consistency, existing literature lacks large-scale biomarker tracking to distinguish between positive neuromuscular adaptation and cumulative overtraining or hormonal suppression.",
                    severity="High",
                    potential_impact="Enables practitioners and coaches to calibrate daily volume to prevent chronic fatigue and musculoskeletal degradation."
                ),
                ResearchGap(
                    title="Long-Term Adherence Mechanisms Across Heterogeneous Age and Lifestyle Cohorts",
                    area="Behavioral Medicine & Lifestyle Adherence",
                    description="Most gym intervention studies focus on 8-12 week randomized trials; longitudinal data tracking multi-year behavioral maintenance and adherence drop-off factors remains sparse.",
                    severity="Medium",
                    potential_impact="Informs sustainable public health exercise guidelines and personalized fitness prescription."
                )
            ]

        return [
            ResearchGap(
                title=f"Longitudinal Real-World Outcomes and Sustained Adherence Trajectories in {objective[:30]}",
                area="Empirical Research",
                description="Existing literature often relies on short-term observational studies rather than longitudinal protocols tracking multi-year efficacy and behavioral sustainability.",
                severity="High",
                potential_impact="Provides robust empirical verification required for policy, clinical, or personal decision-making."
            ),
            ResearchGap(
                title="Efficacy Variance Across Heterogeneous Baseline Cohorts",
                area="Comparative Systems",
                description="Aggregate metrics frequently obscure sharp internal divides across differing individual baselines, experience levels, and resource contexts.",
                severity="Medium",
                potential_impact="Prevents over-generalization and enhances analytical granularity."
            )
        ]
