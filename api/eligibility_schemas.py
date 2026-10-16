"""Day 21 eligibility API request and response schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class EligibilityRequest(BaseModel):
    """Inputs for evaluating one parsed resume against a job."""

    job_description_id: str = Field(..., min_length=1)
    role: str = Field(
        ...,
        min_length=1,
        description="Role key configured in configs/eligibility_rules.json",
    )
    experience_years: Optional[float] = Field(
        None,
        ge=0,
        description="Optional verified experience duration in years.",
    )
    location: Optional[str] = Field(
        None,
        description="Optional verified candidate location.",
    )
    availability_confirmed: Optional[bool] = Field(
        None,
        description="Whether the candidate's availability has been confirmed.",
    )


class EligibilityResponse(BaseModel):
    """Decision and explainable rule evaluation results."""

    job_description_id: str
    candidate_id: str
    role: str
    decision: str
    ats_score: Optional[float] = None
    reasons: List[str] = Field(default_factory=list)
    passed_rules: List[str] = Field(default_factory=list)
    failed_rules: List[str] = Field(default_factory=list)
    review_reasons: List[str] = Field(default_factory=list)
    review_required: bool
