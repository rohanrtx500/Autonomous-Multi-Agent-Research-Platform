from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ResearchSubTask(BaseModel):
    id: str
    title: str
    description: str
    assigned_agent: str
    status: str = "pending"  # pending, in_progress, completed, failed


class MethodComparison(BaseModel):
    method_name: str
    category: str
    advantages: List[str] = Field(default_factory=list)
    disadvantages: List[str] = Field(default_factory=list)
    datasets_used: List[str] = Field(default_factory=list)
    performance_summary: str


class ResearchGap(BaseModel):
    title: str
    area: str
    description: str
    severity: str  # High, Medium, Low
    potential_impact: str


class ExperimentRecommendation(BaseModel):
    title: str
    hypothesis: str
    recommended_datasets: List[str] = Field(default_factory=list)
    recommended_metrics: List[str] = Field(default_factory=list)
    baseline_models: List[str] = Field(default_factory=list)
    step_by_step_plan: List[str] = Field(default_factory=list)


class ResearchReport(BaseModel):
    title: str
    executive_summary: str
    problem_statement: str
    key_findings: List[str] = Field(default_factory=list)
    method_comparison: List[MethodComparison] = Field(default_factory=list)
    research_gaps: List[ResearchGap] = Field(default_factory=list)
    future_work: List[str] = Field(default_factory=list)
    suggested_experiments: List[ExperimentRecommendation] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    full_markdown: str
