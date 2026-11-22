from typing import Any

from pydantic import BaseModel, Field


class ResearchSubTask(BaseModel):
    id: str
    title: str
    description: str
    assigned_agent: str
    status: str = "pending"
    result: dict[str, Any] | None = None


class MethodComparison(BaseModel):
    method_name: str
    category: str
    advantages: list[str] = Field(default_factory=list)
    disadvantages: list[str] = Field(default_factory=list)
    performance_summary: str = ""


class ResearchGap(BaseModel):
    title: str
    area: str
    description: str
    potential_impact: str
    severity: str = "Medium"


class ExperimentRecommendation(BaseModel):
    title: str
    hypothesis: str
    recommended_datasets: list[str] = Field(default_factory=list)
    recommended_metrics: list[str] = Field(default_factory=list)
    baseline_models: list[str] = Field(default_factory=list)
    step_by_step_plan: list[str] = Field(default_factory=list)


class ResearchReport(BaseModel):
    title: str
    executive_summary: str
    problem_statement: str
    key_findings: list[str] = Field(default_factory=list)
    method_comparison: list[MethodComparison] = Field(default_factory=list)
    research_gaps: list[ResearchGap] = Field(default_factory=list)
    future_work: list[str] = Field(default_factory=list)
    suggested_experiments: list[ExperimentRecommendation] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    full_markdown: str = ""
