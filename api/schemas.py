"""
Day 16 - ATS API Schemas

Pydantic request and response contracts for the Zecpath ATS API.

These schemas define the data exchanged between backend clients
and the ATS service.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================================
# COMMON RESPONSE
# ============================================================================


class MessageResponse(BaseModel):
    """Generic API message response."""

    message: str


# ============================================================================
# RESUME UPLOAD
# ============================================================================


class ResumeUploadResponse(BaseModel):
    """Response returned after successful resume upload."""

    resume_id: str = Field(
        ...,
        description="Unique identifier for the uploaded resume.",
    )

    filename: str = Field(
        ...,
        description="Original uploaded filename.",
    )

    status: str = Field(
        ...,
        description="Current resume processing status.",
    )

    message: str = Field(
        ...,
        description="Human-readable upload result.",
    )


# ============================================================================
# RESUME PARSING
# ============================================================================


class ExperienceResponse(BaseModel):
    """Structured work-experience record."""

    job_title: str = ""
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""


class EducationResponse(BaseModel):
    """Structured education record."""

    degree: str = ""
    field_of_study: str = ""
    institution: str = ""
    start_date: str = ""
    end_date: str = ""


class ProjectResponse(BaseModel):
    """Structured project record."""

    name: str = ""
    description: str = ""
    technologies: List[str] = Field(
        default_factory=list
    )


class CandidateProfileResponse(BaseModel):
    """Parsed candidate profile."""

    name: str = ""

    summary: str = ""

    skills: List[str] = Field(
        default_factory=list
    )

    experience: List[ExperienceResponse] = Field(
        default_factory=list
    )

    education: List[EducationResponse] = Field(
        default_factory=list
    )

    certifications: List[str] = Field(
        default_factory=list
    )

    projects: List[ProjectResponse] = Field(
        default_factory=list
    )


class ResumeParseResponse(BaseModel):
    """Response returned after resume parsing."""

    resume_id: str

    status: str

    candidate: CandidateProfileResponse


# ============================================================================
# SCORING REQUEST
# ============================================================================


class ScoreRequest(BaseModel):
    """Request to score one resume against a job description."""

    job_description_id: str = Field(
        ...,
        description="Identifier of the job description.",
    )


# ============================================================================
# SCORE COMPONENT
# ============================================================================


class ScoreComponentResponse(BaseModel):
    """Explainable ATS scoring component."""

    score: Optional[float] = None

    base_weight: float = 0.0

    effective_weight: float = 0.0

    contribution: float = 0.0

    available: bool = False


# ============================================================================
# SCORING RESPONSE
# ============================================================================


class ScoreResponse(BaseModel):
    """ATS scoring response."""

    resume_id: str

    job_description_id: str

    candidate_id: str

    role: str

    normalized_role: str

    final_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )

    final_percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
    )

    available_signals: List[str] = Field(
        default_factory=list
    )

    missing_signals: List[str] = Field(
        default_factory=list
    )

    components: Dict[
        str,
        ScoreComponentResponse
    ] = Field(
        default_factory=dict
    )


# ============================================================================
# SHORTLISTING REQUEST
# ============================================================================


class ShortlistingThresholds(BaseModel):
    """Configurable shortlisting thresholds."""

    shortlist: float = Field(
        0.70,
        ge=0.0,
        le=1.0,
        description="Minimum normalized score for shortlist.",
    )

    review: float = Field(
        0.50,
        ge=0.0,
        le=1.0,
        description="Minimum normalized score for review.",
    )


class ShortlistingRequest(BaseModel):
    """Request for ranking and shortlisting candidates."""

    job_description_id: str

    candidate_ids: List[str] = Field(
        ...,
        min_length=1,
    )

    top_n: int = Field(
        5,
        ge=1,
    )

    thresholds: ShortlistingThresholds = Field(
        default_factory=ShortlistingThresholds
    )


# ============================================================================
# RANKED CANDIDATE
# ============================================================================


class RankedCandidateResponse(BaseModel):
    """Recruiter-friendly ranked candidate."""

    rank: int = Field(
        ...,
        ge=1,
    )

    candidate_id: str

    candidate_name: str

    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )

    score_percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
    )

    status: str


# ============================================================================
# SHORTLISTING RESPONSE
# ============================================================================


class ShortlistingResponse(BaseModel):
    """Response containing ranking and recruitment zones."""

    job_description_id: str

    total_candidates: int = Field(
        ...,
        ge=0,
    )

    shortlisted_count: int = Field(
        ...,
        ge=0,
    )

    review_count: int = Field(
        ...,
        ge=0,
    )

    rejected_count: int = Field(
        ...,
        ge=0,
    )

    ranked_candidates: List[
        RankedCandidateResponse
    ] = Field(
        default_factory=list
    )

    top_candidates: List[
        RankedCandidateResponse
    ] = Field(
        default_factory=list
    )


# ============================================================================
# ASYNC JOB
# ============================================================================


class JobCreateRequest(BaseModel):
    """Request for asynchronous ATS processing."""

    operation: str

    job_description_id: str

    resume_ids: List[str] = Field(
        ...,
        min_length=1,
    )


class JobCreateResponse(BaseModel):
    """Response returned when an async job is created."""

    job_id: str

    status: str

    message: str


class JobStatusResponse(BaseModel):
    """Current asynchronous job status."""

    job_id: str

    status: str

    progress: Optional[int] = Field(
        None,
        ge=0,
        le=100,
    )

    result: Optional[
        Dict[str, Any]
    ] = None

    error: Optional[
        Dict[str, Any]
    ] = None


# ============================================================================
# ERROR RESPONSE
# ============================================================================


class ErrorDetail(BaseModel):
    """Structured API error detail."""

    code: str

    message: str

    details: Optional[Any] = None

    request_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard API error response."""

    error: ErrorDetail