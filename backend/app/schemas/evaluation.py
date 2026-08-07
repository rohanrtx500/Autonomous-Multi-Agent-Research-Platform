from typing import Any

from pydantic import BaseModel, Field


class EvaluationMetrics(BaseModel):
    faithfulness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    grounding_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    hallucination_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning_quality: float = Field(default=0.0, ge=0.0, le=1.0)
    is_acceptable: bool = False
    critique_comments: list[str] = Field(default_factory=list)


class AgentExecutionLog(BaseModel):
    timestamp: str
    agent_name: str
    status: str
    execution_time_ms: float
    decision_reasoning: str
    details: dict[str, Any] = Field(default_factory=dict)
