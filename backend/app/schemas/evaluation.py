from typing import Any, Literal
from pydantic import BaseModel, Field

ClaimStatus = Literal["supported", "partially_supported", "unsupported", "unverified"]


class ClaimVerificationItem(BaseModel):
    claim_id: str
    claim_text: str
    section: str = "Key Findings"
    citation_indices: list[int] = Field(default_factory=list)
    source_identifiers: list[str] = Field(default_factory=list)
    status: ClaimStatus = "unverified"
    evidence_snippets: list[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    verification_notes: str = ""


class CitationVerificationResult(BaseModel):
    total_claims: int = 0
    supported_claims: int = 0
    partially_supported_claims: int = 0
    unsupported_claims: int = 0
    unverified_claims: int = 0
    claims_with_citations: int = 0
    claims_missing_citations: int = 0
    citation_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    citation_correctness: float = Field(default=0.0, ge=0.0, le=1.0)
    unsupported_claim_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    grounding_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    verification_status: str = "Pending"
    claim_details: list[ClaimVerificationItem] = Field(default_factory=list)


class EvaluationMetrics(BaseModel):
    # Core legacy fields for backward compatibility
    faithfulness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    grounding_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    hallucination_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning_quality: float = Field(default=0.0, ge=0.0, le=1.0)
    is_acceptable: bool = False
    critique_comments: list[str] = Field(default_factory=list)

    # Rigorous measurable evaluation metrics
    precision_at_k: float | None = Field(default=None, ge=0.0, le=1.0)
    recall_at_k: float | None = Field(default=None, ge=0.0, le=1.0)
    mrr: float | None = Field(default=None, ge=0.0, le=1.0)
    context_relevance: float | None = Field(default=None, ge=0.0, le=1.0)
    answer_relevance: float | None = Field(default=None, ge=0.0, le=1.0)
    citation_coverage: float | None = Field(default=None, ge=0.0, le=1.0)
    citation_correctness: float | None = Field(default=None, ge=0.0, le=1.0)
    unsupported_claim_rate: float | None = Field(default=None, ge=0.0, le=1.0)

    # Methodology and metadata
    deterministic_metrics: dict[str, Any] = Field(default_factory=dict)
    llm_judge_metrics: dict[str, Any] = Field(default_factory=dict)
    methodology: str | None = None
    limitations: list[str] = Field(default_factory=list)


class AgentExecutionLog(BaseModel):
    timestamp: str
    agent_name: str
    status: str
    execution_time_ms: float
    decision_reasoning: str
    details: dict[str, Any] = Field(default_factory=dict)
