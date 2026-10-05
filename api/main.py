"""
Day 16 - Zecpath ATS FastAPI Application
"""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    Request,
    UploadFile,
)

from fastapi.exceptions import (
    RequestValidationError,
)

from fastapi.responses import JSONResponse

from api.schemas import (
    ErrorDetail,
    ErrorResponse,
    JobCreateRequest,
    JobCreateResponse,
    JobStatusResponse,
    ResumeParseResponse,
    ResumeUploadResponse,
    ScoreRequest,
    ScoreResponse,
    ShortlistingRequest,
    ShortlistingResponse,
    RankedCandidateResponse,
)

from api.services import (
    create_job,
    execute_job,
    get_job,
    get_resume,
    get_job_description,
    health_status,
    parse_resume,
    save_uploaded_resume,
    score_resume,
    shortlist_candidates,
)


# ============================================================================
# APP
# ============================================================================


app = FastAPI(
    title="Zecpath ATS API",
    description=(
        "REST API for the Zecpath AI "
        "Applicant Tracking System."
    ),
    version="1.0.0",
)


# ============================================================================
# LOGGING
# ============================================================================


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(
    "zecpath_ats_api"
)


# ============================================================================
# REQUEST LOGGING
# ============================================================================


@app.middleware("http")
async def request_logging(
    request: Request,
    call_next,
):
    """Log basic request information."""

    request_id = (
        request.headers.get(
            "X-Request-ID"
        )
        or f"REQ-{uuid.uuid4().hex[:8]}"
    )

    start = time.perf_counter()

    try:
        response = await call_next(
            request
        )

    except Exception:

        logger.exception(
            "request_id=%s method=%s path=%s status=500",
            request_id,
            request.method,
            request.url.path,
        )

        raise

    duration = (
        time.perf_counter()
        - start
    )

    response.headers[
        "X-Request-ID"
    ] = request_id

    logger.info(
        "request_id=%s method=%s path=%s "
        "status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration * 1000,
    )

    return response


# ============================================================================
# ERROR HELPER
# ============================================================================


def make_error(
    request_id: str,
    code: str,
    message: str,
    status_code: int,
    details=None,
):
    """Create the standard API error response."""

    response = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            details=details,
            request_id=request_id,
        )
    )

    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
    )


def request_id(
    request: Request,
) -> str:
    """Get request ID."""

    return (
        request.headers.get(
            "X-Request-ID"
        )
        or "unknown"
    )


# ============================================================================
# VALIDATION ERROR
# ============================================================================


@app.exception_handler(
    RequestValidationError
)
async def validation_error(
    request: Request,
    exc: RequestValidationError,
):
    """Return standardized validation errors."""

    return make_error(
        request_id=request_id(
            request
        ),
        code="VALIDATION_ERROR",
        message=(
            "Request validation failed."
        ),
        status_code=422,
        details=exc.errors(),
    )


# ============================================================================
# HEALTH
# ============================================================================


@app.get(
    "/health"
)
async def health():
    """Health check."""

    return health_status()


# ============================================================================
# RESUME UPLOAD
# ============================================================================


@app.post(
    "/api/v1/resumes",
    response_model=ResumeUploadResponse,
    status_code=201,
)
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
):
    """Upload a resume."""

    try:

        result = save_uploaded_resume(
            file
        )

        return ResumeUploadResponse(
            resume_id=result[
                "resume_id"
            ],
            filename=result[
                "filename"
            ],
            status=result[
                "status"
            ],
            message=(
                "Resume uploaded successfully."
            ),
        )

    except ValueError as exc:

        return make_error(
            request_id=request_id(
                request
            ),
            code="INVALID_FILE",
            message=str(exc),
            status_code=400,
        )

    except Exception as exc:

        logger.exception(
            "Resume upload failed."
        )

        return make_error(
            request_id=request_id(
                request
            ),
            code="PROCESSING_ERROR",
            message=(
                "Unable to upload resume."
            ),
            status_code=500,
        )


# ============================================================================
# RESUME PARSING
# ============================================================================


@app.post(
    "/api/v1/resumes/{resume_id}/parse",
    response_model=ResumeParseResponse,
)
async def parse_resume_api(
    resume_id: str,
    request: Request,
):
    """Parse an uploaded resume."""

    try:

        get_resume(
            resume_id
        )

        parsed = parse_resume(
            resume_id
        )

        return ResumeParseResponse(
            resume_id=resume_id,
            status="PARSED",
            candidate=parsed,
        )

    except LookupError as exc:

        return make_error(
            request_id=request_id(
                request
            ),
            code="RESUME_NOT_FOUND",
            message=str(exc),
            status_code=404,
        )

    except ValueError as exc:

        return make_error(
            request_id=request_id(
                request
            ),
            code="INVALID_REQUEST",
            message=str(exc),
            status_code=400,
        )


# ============================================================================
# SCORING
# ============================================================================


@app.post(
    "/api/v1/resumes/{resume_id}/score",
    response_model=ScoreResponse,
)
async def score_resume_api(
    resume_id: str,
    request: Request,
    body: ScoreRequest,
):
    """Score one resume against a job description."""

    try:

        result = score_resume(
            resume_id=resume_id,
            job_description_id=(
                body.job_description_id
            ),
        )

        return ScoreResponse(
            resume_id=resume_id,
            job_description_id=(
                body.job_description_id
            ),
            candidate_id=str(
                result.get(
                    "candidate_id",
                    "",
                )
            ),
            role=str(
                result.get(
                    "role",
                    "",
                )
            ),
            normalized_role=str(
                result.get(
                    "normalized_role",
                    "",
                )
            ),
            final_score=float(
                result.get(
                    "final_score",
                    0.0,
                )
            ),
            final_percentage=float(
                result.get(
                    "final_percentage",
                    0.0,
                )
            ),
            available_signals=list(
                result.get(
                    "available_signals",
                    [],
                )
            ),
            missing_signals=list(
                result.get(
                    "missing_signals",
                    [],
                )
            ),
            components=result.get(
                "components",
                {},
            ),
        )

    except LookupError as exc:

        message = str(exc)

        code = (
            "RESUME_NOT_FOUND"
            if "Resume" in message
            else "JOB_DESCRIPTION_NOT_FOUND"
        )

        return make_error(
            request_id=request_id(
                request
            ),
            code=code,
            message=message,
            status_code=404,
        )

    except Exception:

        logger.exception(
            "Resume scoring failed."
        )

        return make_error(
            request_id=request_id(
                request
            ),
            code="PROCESSING_ERROR",
            message="Resume scoring failed.",
            status_code=500,
        )


# ============================================================================
# SHORTLISTING
# ============================================================================


@app.post(
    "/api/v1/shortlisting",
    response_model=ShortlistingResponse,
)
async def shortlisting_api(
    request: Request,
    body: ShortlistingRequest,
):
    """Rank and classify multiple candidates."""

    try:

        result = shortlist_candidates(
            job_description_id=(
                body.job_description_id
            ),
            candidate_ids=(
                body.candidate_ids
            ),
            top_n=body.top_n,
            shortlist_threshold=(
                body.thresholds.shortlist
            ),
            review_threshold=(
                body.thresholds.review
            ),
        )

        ranked = []

        for candidate in result[
            "ranked_candidates"
        ]:

            ranked.append(
                RankedCandidateResponse(
                    rank=int(
                        candidate.get(
                            "rank",
                            0,
                        )
                    ),
                    candidate_id=str(
                        candidate.get(
                            "candidate_id",
                            "",
                        )
                    ),
                    candidate_name=str(
                        candidate.get(
                            "candidate_name",
                            candidate.get(
                                "candidate_id",
                                "",
                            ),
                        )
                    ),
                    score=float(
                        candidate.get(
                            "final_score",
                            0.0,
                        )
                    ),
                    score_percentage=float(
                        candidate.get(
                            "score_percentage",
                            candidate.get(
                                "final_percentage",
                                0.0,
                            ),
                        )
                    ),
                    status=str(
                        candidate.get(
                            "status",
                            "",
                        )
                    ),
                )
            )

        top = ranked[:body.top_n]

        return ShortlistingResponse(
            job_description_id=(
                body.job_description_id
            ),
            total_candidates=len(
                ranked
            ),
            shortlisted_count=len(
                result[
                    "shortlisted_candidates"
                ]
            ),
            review_count=len(
                result[
                    "review_candidates"
                ]
            ),
            rejected_count=len(
                result[
                    "rejected_candidates"
                ]
            ),
            ranked_candidates=ranked,
            top_candidates=top,
        )

    except LookupError as exc:

        return make_error(
            request_id=request_id(
                request
            ),
            code="RESOURCE_NOT_FOUND",
            message=str(exc),
            status_code=404,
        )

    except ValueError as exc:

        return make_error(
            request_id=request_id(
                request
            ),
            code="VALIDATION_ERROR",
            message=str(exc),
            status_code=422,
        )

    except Exception:

        logger.exception(
            "Shortlisting failed."
        )

        return make_error(
            request_id=request_id(
                request
            ),
            code="PROCESSING_ERROR",
            message="Shortlisting failed.",
            status_code=500,
        )


# ============================================================================
# ASYNC JOB CREATION
# ============================================================================


@app.post(
    "/api/v1/jobs",
    response_model=JobCreateResponse,
    status_code=202,
)
async def create_async_job(
    request: Request,
    body: JobCreateRequest,
    background_tasks: BackgroundTasks,
):
    """Create an asynchronous ATS job."""

    try:

        job = create_job(
            operation=body.operation,
            job_description_id=(
                body.job_description_id
            ),
            resume_ids=body.resume_ids,
        )

        background_tasks.add_task(
            execute_job,
            job["job_id"],
        )

        return JobCreateResponse(
            job_id=job["job_id"],
            status=job["status"],
            message=(
                "ATS processing job accepted."
            ),
        )

    except Exception:

        logger.exception(
            "Async job creation failed."
        )

        return make_error(
            request_id=request_id(
                request
            ),
            code="PROCESSING_ERROR",
            message=(
                "Unable to create ATS job."
            ),
            status_code=500,
        )


# ============================================================================
# ASYNC JOB STATUS
# ============================================================================


@app.get(
    "/api/v1/jobs/{job_id}",
    response_model=JobStatusResponse,
)
async def job_status_api(
    job_id: str,
    request: Request,
):
    """Get asynchronous job status."""

    try:

        job = get_job(
            job_id
        )

        return JobStatusResponse(
            job_id=job[
                "job_id"
            ],
            status=job[
                "status"
            ],
            progress=job.get(
                "progress"
            ),
            result=job.get(
                "result"
            ),
            error=job.get(
                "error"
            ),
        )

    except LookupError as exc:

        return make_error(
            request_id=request_id(
                request
            ),
            code="JOB_NOT_FOUND",
            message=str(exc),
            status_code=404,
        )


# ============================================================================
# START SERVER
# ============================================================================


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )