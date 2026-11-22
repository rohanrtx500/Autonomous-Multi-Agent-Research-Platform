import json
import re
import time
from typing import Any

from app.agents.base import BaseAgent
from app.schemas.research import ExperimentRecommendation
from app.schemas.state import ResearchState


class ExperimentPlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Experiment Planner")

    def run(self, state: ResearchState) -> dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "Research Topic")
        papers = state.get("retrieved_papers", [])
        web = state.get("retrieved_web_sources", [])

        context_snippets = [w.content[:200] for w in web[:3]] + [p.abstract[:200] for p in papers[:2]]
        evidence_summary = "\n".join(context_snippets)

        experiments = []
        if self.llm:
            try:
                prompt = (
                    f"You are a Research Director designing investigative methodologies or empirical studies.\n"
                    f"For the topic: '{objective}', design 1-2 rigorous research protocols or comparative investigative studies.\n\n"
                    f"CRITICAL DOMAIN DIRECTIVE:\n"
                    f"Design research studies tailored strictly to '{objective}'.\n"
                    f"For social, cultural, medical, historical, or economic topics, design field surveys, observational studies, or comparative statistical evaluations—NOT machine learning experiments.\n"
                    f"Do NOT drift into AI/ML/DL terminology unless the objective is explicitly about software/AI.\n\n"
                    f"Available Reference Context:\n{evidence_summary}\n\n"
                    f"Return ONLY a JSON list of objects with fields:\n"
                    f"- title: (string, descriptive title of the study or experimental protocol)\n"
                    f"- hypothesis: (string, the core hypothesis or premise to test)\n"
                    f"- recommended_datasets: (list of 2-3 strings, e.g. 'Pew Research Survey', 'Cost of Living Index', 'BLS Time Use Survey')\n"
                    f"- recommended_metrics: (list of 2-3 strings, e.g. 'Discretionary Time Per Day', 'Purchasing Power Parity Index')\n"
                    f"- baseline_models: (list of 2 strings, e.g. 'Cohort A (US Metros)', 'Cohort B (Tier-1 Indian Metros)')\n"
                    f"- step_by_step_plan: (list of 4 strings outlining chronological methodology)\n\n"
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
                    experiments.append(
                        ExperimentRecommendation(
                            title=item.get("title", "Empirical Evaluation Protocol"),
                            hypothesis=item.get("hypothesis", "Comparative analysis reveals statistically significant divergence in core indicators."),
                            recommended_datasets=item.get("recommended_datasets", ["Primary Field Survey", "National Statistical Index"]),
                            recommended_metrics=item.get("recommended_metrics", ["Satisfaction Index", "Cost Efficiency"]),
                            baseline_models=item.get("baseline_models", ["Primary Group Baseline", "Comparative Cohort"]),
                            step_by_step_plan=item.get("step_by_step_plan", [
                                "Formulate baseline test conditions and sample stratifications.",
                                "Gather multi-source observational datasets across targeted cohorts.",
                                "Normalize metrics against regional economic baselines.",
                                "Conduct difference analysis and validate significance."
                            ])
                        )
                    )
            except Exception as e:  # noqa: BLE001
                self.log_execution("warning", start_time, f"LLM experiment planning failed: {e}. Using dynamic study design.")

        if not experiments:
            experiments = self._dynamic_experiments(objective)

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=f"Designed {len(experiments)} empirical research protocols to evaluate '{objective}'.",
            details={"experiment_count": len(experiments)}
        )

        return {
            "experiment_plan": experiments,
            "status": "writing",
            "agent_logs": [log]
        }

    def _dynamic_experiments(self, objective: str) -> list[ExperimentRecommendation]:
        obj_lower = objective.lower()

        if any(w in obj_lower for w in ["usa vs india", "india vs usa", "american vs indian", "relocating to usa", "moving to india"]):
            return [
                ExperimentRecommendation(
                    title="Cross-National Time-Use and Subjective Well-Being Longitudinal Study",
                    hypothesis="Professionals in the US allocate higher discrete daily hours to independent domestic chores and commuting, whereas Indian urban professionals leverage informal service economies to preserve family and social connectivity despite longer official office hours.",
                    recommended_datasets=["BLS American Time Use Survey", "NSSO India Time Use Survey Panel", "WHO-5 Well-Being Index"],
                    recommended_metrics=["Daily Discretionary Social Hours", "Burnout & Psychological Strain Score", "Effective Commute Burden"],
                    baseline_models=["US Metropolitan Professional Cohort (NYC/SF)", "Indian Metro Professional Cohort (Bengaluru/Mumbai)"],
                    step_by_step_plan=[
                        "Recruit matched cohorts of 1,200 tech and corporate professionals across equivalent salary percentiles in US and Indian metropolitan clusters.",
                        "Track daily time logs over a 12-month period covering working hours, domestic tasks, leisure, sleep, and familial caregiving.",
                        "Administer quarterly psychological well-being and social support assessments using standardized psychometric instruments.",
                        "Perform multivariable regression to isolate the causal impact of domestic support infrastructure on perceived work-life satisfaction."
                    ]
                )
            ]

        # Health, Fitness & Physical Training
        if any(w in obj_lower for w in ["gym", "exercise", "workout", "fitness", "physical training", "health", "diet", "nutrition", "body"]):
            return [
                ExperimentRecommendation(
                    title="Longitudinal Evaluation of Daily Gymnasium Resistance & Cardio vs Periodized Rest on Biomarkers",
                    hypothesis=f"Systematic evaluation of '{objective}' reveals that modulated frequency with adequate recovery yields superior cardiovascular endurance and lower systemic cortisol than continuous unmodulated daily load.",
                    recommended_datasets=["NHANES Biomarker Database", "ACSM Exercise Physiology Registry", "WHO Physical Activity Panel"],
                    recommended_metrics=["VO2 Max / Aerobic Capacity", "Resting Heart Rate & HRV", "Serum Cortisol & Creatine Kinase", "Self-Reported Energy & Sleep Quality"],
                    baseline_models=["Daily High-Volume Cohort (7 days/wk)", "Periodized Split Cohort (4-5 days/wk + Active Recovery)"],
                    step_by_step_plan=[
                        "Recruit 400 healthy adult participants stratified by age, biological sex, and baseline fitness levels.",
                        "Randomize participants into Daily Continuous Training vs Periodized Volume with active rest cycles over a 24-week intervention.",
                        "Collect bi-weekly blood panels measuring hormonal markers (cortisol, testosterone/estrogen ratio) and muscle damage enzymes (CK).",
                        "Evaluate changes in body composition (DEXA scan), neuromuscular power, and subjective psychological recovery scores."
                    ]
                )
            ]

        return [
            ExperimentRecommendation(
                title=f"Empirical Controlled Investigation of {objective[:35]}",
                hypothesis=f"Systematic implementation of '{objective}' demonstrates statistically significant positive variance in primary outcomes compared to baseline controls.",
                recommended_datasets=["Cross-Domain Survey Panel", "Historical Benchmark Database", "Empirical Field Observations"],
                recommended_metrics=["Target Performance Efficacy", "Long-term Adherence Rate", "Resource-to-Benefit Efficiency"],
                baseline_models=["Standard Unstructured Baseline", "Systematic Structured Protocol"],
                step_by_step_plan=[
                    "Define operational boundary conditions and sample stratifications across target cohorts.",
                    "Collect structured quantitative metrics and observational data across diverse deployment contexts.",
                    "Normalize indicators to adjust for extraneous ambient variables.",
                    "Execute regression and hypothesis testing to validate findings."
                ]
            )
        ]
