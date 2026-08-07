import time
import json
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.schemas.research import ExperimentRecommendation
from app.schemas.state import ResearchState


class ExperimentPlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Experiment Planner")

    def run(self, state: ResearchState) -> Dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "Research Topic")

        experiments = []
        if self.llm:
            try:
                prompt = (
                    f"Design 2 rigorous empirical experiment recommendations to evaluate: '{objective}'.\n"
                    f"Return ONLY a JSON list of objects with fields: title, hypothesis, recommended_datasets (list of 2-3 strings), recommended_metrics (list of 2-3 strings), baseline_models (list of 2 strings), step_by_step_plan (list of 4 strings)."
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
                    experiments.append(
                        ExperimentRecommendation(
                            title=item.get("title", "Empirical Evaluation Protocol"),
                            hypothesis=item.get("hypothesis", "Proposed strategy yields statistically significant improvements."),
                            recommended_datasets=item.get("recommended_datasets", ["Dataset A", "Benchmark Dataset B"]),
                            recommended_metrics=item.get("recommended_metrics", ["Primary Metric", "Efficiency Ratio"]),
                            baseline_models=item.get("baseline_models", ["Standard Baseline", "Alternative Method"]),
                            step_by_step_plan=item.get("step_by_step_plan", [
                                "Formulate baseline test conditions.",
                                "Gather domain observational and trial datasets.",
                                "Compute evaluation metrics across sample groups.",
                                "Statistical significance testing and risk analysis."
                            ])
                        )
                    )
            except Exception as e:
                self.log_execution("warning", start_time, f"LLM generation failed: {e}. Using domain-tailored experiment plan.")

        if not experiments:
            experiments = self._domain_tailored_experiments(objective)

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=f"Designed {len(experiments)} rigorous empirical experiments to validate hypotheses for '{objective}'.",
            details={"experiment_count": len(experiments)}
        )

        return {
            "experiment_plan": experiments,
            "status": "writing",
            "agent_logs": [log]
        }

    def _domain_tailored_experiments(self, objective: str) -> List[ExperimentRecommendation]:
        obj_lower = objective.lower()

        if any(w in obj_lower for w in ["income", "ubi", "economic", "labor", "inflation", "market", "poverty", "policy", "tax"]):
            return [
                ExperimentRecommendation(
                    title="Multi-Tiered Unconditional Cash Transfer Trial with Synthetic Controls",
                    hypothesis="Unconditional monthly transfers ($1,000/mo) increase entrepreneurship and education enrollment without causing local CPI inflation >0.5%.",
                    recommended_datasets=["Census Bureau CPS Data", "Local Consumer Price Index (CPI) Panel", "State Tax Return Datasets"],
                    recommended_metrics=["Labor Supply Elasticity", "Consumer Price Index Variance", "Net Business Formation Rate"],
                    baseline_models=["Means-Tested Welfare Baseline", "Unconditional Transfer Cohort"],
                    step_by_step_plan=[
                        "Select 3 treatment municipalities and 3 matched synthetic control municipalities with similar baseline demographic distributions.",
                        "Disburse $1,000 monthly unconditional transfers to 2,500 low- and middle-income households for 36 months.",
                        "Track monthly labor participation rates, job search durations, and local retail/rent price indices.",
                        "Execute difference-in-differences (DiD) regression analysis to isolate causal impact from national economic cycles."
                    ]
                ),
                ExperimentRecommendation(
                    title="Macroeconomic Inflationary Feedback Simulation Under Funding Models",
                    hypothesis="Funding UBI through progressive wealth/carbon taxation eliminates demand-pull inflation compared to deficit-financed UBI.",
                    recommended_datasets=["Bureau of Economic Analysis (BEA) Input-Output Tables", "OECD Tax Database"],
                    recommended_metrics=["Real GDP Growth", "Headline Inflation Rate", "Gini Coefficient Reduction"],
                    baseline_models=["Deficit-Financed UBI CGE Model", "Tax-Financed Revenue Neutral Model"],
                    step_by_step_plan=[
                        "Construct a dynamic stochastic general equilibrium (DSGE) model calibrated to national economic data.",
                        "Simulate a universal annual transfer funded via progressive wealth tax vs federal bond issuance.",
                        "Model consumer marginal propensity to consume (MPC) across income deciles.",
                        "Evaluate 10-year macroeconomic trajectory, debt-to-GDP ratio, and price level stability."
                    ]
                )
            ]

        return [
            ExperimentRecommendation(
                title=f"Empirical Benchmarking Protocol for {objective[:30]}...",
                hypothesis="Targeted methodology yields significant improvement over baseline control groups.",
                recommended_datasets=["Primary Field Dataset", "Public Reference Benchmark"],
                recommended_metrics=["Domain Efficiency Metric", "Statistical Confidence Index"],
                baseline_models=["Standard Baseline Strategy", "Proposed Experimental Approach"],
                step_by_step_plan=[
                    "Establish standardized control and treatment parameters.",
                    "Execute data collection across representative sample populations.",
                    "Perform comparative measurement and hypothesis testing.",
                    "Analyze secondary spillovers and long-term stability metrics."
                ]
            )
        ]
