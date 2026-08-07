import json
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

        gaps = []
        if self.llm:
            try:
                prompt = (
                    f"Identify 3 critical research gaps and open problems for the topic: '{objective}'.\n"
                    f"Return ONLY a JSON list of objects with fields: title, area, description, severity ('High' or 'Medium'), potential_impact."
                )
                res = self.llm.invoke(prompt)
                content = res.content if hasattr(res, 'content') else str(res)
                cleaned = content.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned.split("```json")[1].split("```")[0].strip()
                elif cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1].split("```")[0].strip()

                parsed = json.loads(cleaned)
                for item in parsed:
                    gaps.append(
                        ResearchGap(
                            title=item.get("title", "Unresolved Domain Problem"),
                            area=item.get("area", "Core Domain"),
                            description=item.get("description", "Further empirical investigation is needed."),
                            severity=item.get("severity", "High"),
                            potential_impact=item.get("potential_impact", "Unlocks higher precision and domain understanding.")
                        )
                    )
            except Exception as e:  # noqa: BLE001
                self.log_execution("warning", start_time, f"LLM generation failed: {e}. Using domain-tailored gaps.")

        if not gaps:
            gaps = self._domain_tailored_gaps(objective)

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=f"Identified {len(gaps)} critical research gaps and open problems in '{objective}'.",
            details={"gaps_count": len(gaps)}
        )

        return {
            "research_gaps": gaps,
            "status": "experimenting",
            "agent_logs": [log]
        }

    def _domain_tailored_gaps(self, objective: str) -> list[ResearchGap]:
        obj_lower = objective.lower()

        if any(w in obj_lower for w in ["income", "ubi", "economic", "labor", "inflation", "market", "poverty", "policy", "tax"]):
            return [
                ResearchGap(
                    title="Long-Term Labor Market Attrition vs Re-skilling Dynamics",
                    area="Labor Economics",
                    description="Most UBI pilot trials run for 1 to 3 years, creating an anticipation bias where recipients know the transfer is temporary and alter long-term career investment decisions.",
                    severity="High",
                    potential_impact="Resolving this enables policymakers to accurately forecast whether permanent UBI causes permanent workforce withdrawal or accelerates adult education and entrepreneurship."
                ),
                ResearchGap(
                    title="Regional Supply-Side Elasticity and Inflationary Spillover",
                    area="Macroeconomic Transmission",
                    description="Lack of multi-region trial data measuring how local housing markets and food suppliers adjust prices when lower-income populations receive guaranteed cash influxes.",
                    severity="High",
                    potential_impact="Prevents local landlords or retailers from capturing consumer surplus through rent increases or demand-pull price spikes."
                ),
                ResearchGap(
                    title="Optimal Integration with Existing Social Safety Nets",
                    area="Public Policy Architecture",
                    description="Uncertainty regarding whether UBI should replace existing means-tested benefits (food assistance, healthcare subsidies) or act as a complementary floor.",
                    severity="Medium",
                    potential_impact="Ensures net welfare gains without accidentally impoverishing specialized disability or high-need benefit recipients."
                )
            ]

        if any(w in obj_lower for w in ["gene", "crispr", "medicine", "health", "cancer", "drug", "disease", "cell", "clinical"]):
            return [
                ResearchGap(
                    title="Off-Target Cleavage & Long-Term Genomic Instability",
                    area="Molecular Biology & Safety",
                    description="Current sequencing assays struggle to detect rare off-target Double-Strand Breaks (DSBs) across heterochromatin regions in vivo.",
                    severity="High",
                    potential_impact="Crucial for preventing secondary oncogenic mutations in clinical cell therapy recipients."
                ),
                ResearchGap(
                    title="Targeted Extrahepatic Tissue Delivery Mechanisms",
                    area="Pharmacokinetics & Delivery",
                    description="Nanoparticle delivery vehicles heavily accumulate in the liver, limiting therapeutic payload concentration in central nervous system and cardiac tissues.",
                    severity="High",
                    potential_impact="Unlocks curative genetic treatments for neurodegenerative and muscular disorders."
                )
            ]

        return [
            ResearchGap(
                title=f"Long-Term Empirical Validation of {objective[:30]}...",
                area="Domain Methodology",
                description="Current literature lacks longitudinal datasets evaluating long-term systemic stability and performance metrics under extreme edge conditions.",
                severity="High",
                potential_impact="Provides robust empirical verification required for policy, clinical, or production deployment."
            ),
            ResearchGap(
                title="Cross-Domain Generalization & Scaling Constraints",
                area="Systems Architecture",
                description="Existing frameworks exhibit performance degradation when transferred from controlled benchmark environments to real-world heterogeneous settings.",
                severity="Medium",
                potential_impact="Enables seamless scaling and deployment across diverse operational environments."
            )
        ]
