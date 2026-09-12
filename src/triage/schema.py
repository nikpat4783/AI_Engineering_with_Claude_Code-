from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class Citation(BaseModel):
    source_id: str
    source_type: Literal["paper", "patent", "trial_registry", "internal_report"]
    title: str
    status: Literal["active", "stale", "retracted"]
    relevance_score: float


class ConfidenceBreakdown(BaseModel):
    score: float
    level: Literal["high", "medium", "low", "none"]
    num_supporting_sources: int
    mean_relevance_score: float
    agreement: float
    stale_penalty_applied: bool
    rationale: str


class TriageResult(BaseModel):
    status: Literal["answered", "low_confidence", "refused", "escalated"]
    question: str
    answer: str | None
    confidence: ConfidenceBreakdown
    citations: list[Citation]
    gaps: list[str]
    generated_at: datetime
    review_status: Literal["pending", "approved", "rejected"] = "pending"


class ReviewDecision(BaseModel):
    reviewer_id: str
    reviewer_name: str
    decision: Literal["approve", "reject"]
    notes: str
    reviewed_at: datetime


class DraftAnswer(BaseModel):
    answer: str
    cited_source_ids: list[str]
    gaps: list[str]


class GroundingResult(BaseModel):
    ok: bool
    invalid_ids: list[str]
    citations: list[Citation]
