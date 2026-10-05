"""
Day 16 - ATS API Service Layer

Connects the FastAPI endpoints to the existing
Zecpath ATS processing modules.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List

from fastapi import UploadFile

from scoring import day13_candidate_score as day13

from scoring.day14_end_to_end import (
    score_candidate,
)

from scoring.resume_ranking_engine import (
    CandidateRankingEngine,
    RankingThresholds,
)


# ============================================================================
# PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

UPLOAD_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "api_uploads"
)

UPLOAD_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

JOB_DESCRIPTION_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "job_descriptions"
)


# ============================================================================
# IN-MEMORY STORAGE
# ============================================================================

RESUME_STORE: Dict[str, Dict[str, Any]] = {}

SCORE_STORE: Dict[str, Dict[str, Any]] = {}

JOB_STORE: Dict[str, Dict[str, Any]] = {}

STORE_LOCK = Lock()

_resume_counter = 0
_job_counter = 0


JOB_DESCRIPTION_REGISTRY = {
    "JD-000001": (
        JOB_DESCRIPTION_DIRECTORY
        / "python_developer.txt"
    ),
}


# ============================================================================
# ID GENERATION
# ============================================================================


def generate_resume_id() -> str:
    """Generate a unique resume ID."""

    global _resume_counter

    with STORE_LOCK:
        _resume_counter += 1
        return f"RES-{_resume_counter:06d}"


def generate_job_id() -> str:
    """Generate a unique asynchronous job ID."""

    global _job_counter

    with STORE_LOCK:
        _job_counter += 1
        return f"JOB-{_job_counter:06d}"


# ============================================================================
# RESUME UPLOAD
# ============================================================================


def save_uploaded_resume(
    upload: UploadFile,
) -> Dict[str, Any]:
    """Save an uploaded resume."""

    if not upload.filename:
        raise ValueError(
            "Uploaded file must have a filename."
        )

    original_filename = Path(
        upload.filename
    ).name

    extension = Path(
        original_filename
    ).suffix.lower()

    supported_extensions = {
        ".pdf",
        ".docx",
        ".txt",
    }

    if extension not in supported_extensions:
        raise ValueError(
            "Unsupported resume format. "
            "Supported formats: PDF, DOCX, TXT."
        )

    resume_id = generate_resume_id()

    stored_filename = (
        f"{resume_id}{extension}"
    )

    stored_path = (
        UPLOAD_DIRECTORY
        / stored_filename
    )

    try:
        with stored_path.open("wb") as output_file:
            shutil.copyfileobj(
                upload.file,
                output_file,
            )

    except OSError as exc:
        raise RuntimeError(
            "Unable to save uploaded resume."
        ) from exc

    record = {
        "resume_id": resume_id,
        "filename": original_filename,
        "stored_path": str(stored_path),
        "status": "UPLOADED",
    }

    with STORE_LOCK:
        RESUME_STORE[
            resume_id
        ] = record

    return record


# ============================================================================
# RESUME LOOKUP
# ============================================================================


def get_resume(
    resume_id: str,
) -> Dict[str, Any]:
    """Get an uploaded resume record."""

    record = RESUME_STORE.get(
        resume_id
    )

    if record is None:
        raise LookupError(
            f"Resume not found: {resume_id}"
        )

    return record


# ============================================================================
# RESUME PARSING
# ============================================================================


def parse_resume(
    resume_id: str,
) -> Dict[str, Any]:
    """
    Parse an uploaded resume and normalize the existing parser output
    into the API response contract.
    """

    record = get_resume(
        resume_id
    )

    resume_path = Path(
        record["stored_path"]
    )

    if not resume_path.exists():
        raise LookupError(
            "Stored resume file was not found."
        )

    resume_text = (
        day13.extract_resume_text(
            str(resume_path)
        )
    )

    if not resume_text.strip():
        raise ValueError(
            "Resume text could not be extracted."
        )

    parsed = day13.parse_resume_text(
        resume_text
    )

    if not isinstance(parsed, dict):
        raise ValueError(
            "Resume parser returned an invalid result."
        )

    # --------------------------------------------------------------
    # Helper: safely convert parser fields into lists
    # --------------------------------------------------------------

    def ensure_list(value):
        if value is None:
            return []

        if isinstance(value, str):

            cleaned = value.strip()

            if not cleaned:
                return []

            return [cleaned]

        if isinstance(value, (list, tuple)):
            return list(value)

        return [value]

    # --------------------------------------------------------------
    # Normalize skills
    # --------------------------------------------------------------

    skills = ensure_list(
        parsed.get(
            "skills",
            []
        )
    )

    skills = [
        str(skill).strip()
        for skill in skills
        if str(skill).strip()
    ]

    # --------------------------------------------------------------
    # Normalize certifications
    # --------------------------------------------------------------

    certifications = ensure_list(
        parsed.get(
            "certifications",
            []
        )
    )

    certifications = [
        str(cert).strip()
        for cert in certifications
        if str(cert).strip()
    ]

    # --------------------------------------------------------------
    # Normalize experience
    # --------------------------------------------------------------

    raw_experience = ensure_list(
        parsed.get(
            "experience",
            []
        )
    )

    normalized_experience = []

    for item in raw_experience:

        if isinstance(item, dict):

            normalized_experience.append(
                {
                    "job_title": str(
                        item.get(
                            "job_title",
                            item.get(
                                "title",
                                "",
                            ),
                        )
                        or ""
                    ).strip(),

                    "company": str(
                        item.get(
                            "company",
                            item.get(
                                "organization",
                                "",
                            ),
                        )
                        or ""
                    ).strip(),

                    "start_date": str(
                        item.get(
                            "start_date",
                            "",
                        )
                        or ""
                    ).strip(),

                    "end_date": str(
                        item.get(
                            "end_date",
                            "",
                        )
                        or ""
                    ).strip(),

                    "description": str(
                        item.get(
                            "description",
                            item.get(
                                "responsibilities",
                                "",
                            ),
                        )
                        or ""
                    ).strip(),
                }
            )

        elif isinstance(item, str):

            cleaned = item.strip()

            if cleaned:
                normalized_experience.append(
                    {
                        "job_title": "",
                        "company": "",
                        "start_date": "",
                        "end_date": "",
                        "description": cleaned,
                    }
                )

    # --------------------------------------------------------------
    # Normalize education
    # --------------------------------------------------------------

    raw_education = ensure_list(
        parsed.get(
            "education",
            []
        )
    )

    normalized_education = []

    for item in raw_education:

        if isinstance(item, dict):

            normalized_education.append(
                {
                    "degree": str(
                        item.get(
                            "degree",
                            item.get(
                                "qualification",
                                "",
                            ),
                        )
                        or ""
                    ).strip(),

                    "field_of_study": str(
                        item.get(
                            "field_of_study",
                            item.get(
                                "field",
                                "",
                            ),
                        )
                        or ""
                    ).strip(),

                    "institution": str(
                        item.get(
                            "institution",
                            item.get(
                                "college",
                                item.get(
                                    "university",
                                    "",
                                ),
                            ),
                        )
                        or ""
                    ).strip(),

                    "start_date": str(
                        item.get(
                            "start_date",
                            "",
                        )
                        or ""
                    ).strip(),

                    "end_date": str(
                        item.get(
                            "end_date",
                            "",
                        )
                        or ""
                    ).strip(),
                }
            )

        elif isinstance(item, str):

            cleaned = item.strip()

            if cleaned:
                normalized_education.append(
                    {
                        "degree": cleaned,
                        "field_of_study": "",
                        "institution": "",
                        "start_date": "",
                        "end_date": "",
                    }
                )

    # --------------------------------------------------------------
    # Normalize projects
    # --------------------------------------------------------------

    raw_projects = ensure_list(
        parsed.get(
            "projects",
            []
        )
    )

    normalized_projects = []

    for item in raw_projects:

        if isinstance(item, dict):

            technologies = ensure_list(
                item.get(
                    "technologies",
                    item.get(
                        "skills",
                        [],
                    ),
                )
            )

            normalized_projects.append(
                {
                    "name": str(
                        item.get(
                            "name",
                            item.get(
                                "title",
                                "",
                            ),
                        )
                        or ""
                    ).strip(),

                    "description": str(
                        item.get(
                            "description",
                            "",
                        )
                        or ""
                    ).strip(),

                    "technologies": [
                        str(value).strip()
                        for value in technologies
                        if str(value).strip()
                    ],
                }
            )

        elif isinstance(item, str):

            cleaned = item.strip()

            if cleaned:
                normalized_projects.append(
                    {
                        "name": cleaned,
                        "description": "",
                        "technologies": [],
                    }
                )

    # --------------------------------------------------------------
    # Build normalized API profile
    # --------------------------------------------------------------

    normalized_profile = {
        "name": str(
            parsed.get(
                "name",
                parsed.get(
                    "candidate_name",
                    "",
                ),
            )
            or ""
        ).strip(),

        "summary": str(
            parsed.get(
                "summary",
                parsed.get(
                    "profile",
                    parsed.get(
                        "objective",
                        "",
                    ),
                ),
            )
            or ""
        ).strip(),

        "skills": skills,

        "experience": normalized_experience,

        "education": normalized_education,

        "certifications": certifications,

        "projects": normalized_projects,
    }

    # --------------------------------------------------------------
    # Store normalized profile
    # --------------------------------------------------------------

    with STORE_LOCK:

        RESUME_STORE[
            resume_id
        ]["status"] = "PARSED"

        RESUME_STORE[
            resume_id
        ]["parsed_profile"] = (
            normalized_profile
        )

    return normalized_profile

# ============================================================================
# JOB DESCRIPTION LOOKUP
# ============================================================================


def get_job_description(
    job_description_id: str,
) -> Path:
    """Resolve a job-description ID to its local project file."""

    path = JOB_DESCRIPTION_REGISTRY.get(
        job_description_id
    )

    if path is None:
        raise LookupError(
            "Job description not found: "
            f"{job_description_id}"
        )

    if not path.exists():
        raise LookupError(
            f"Job description file not found: "
            f"{path}"
        )

    return path

# ============================================================================
# SCORING
# ============================================================================


def score_resume(
    resume_id: str,
    job_description_id: str,
) -> Dict[str, Any]:
    """Run the existing Day 13 ATS scoring pipeline."""

    record = get_resume(
        resume_id
    )

    jd_path = get_job_description(
        job_description_id
    )

    resume_path = Path(
        record["stored_path"]
    )

    result = score_candidate(
        resume_path=resume_path,
        jd_path=jd_path,
    )

    score_key = (
        f"{resume_id}:{job_description_id}"
    )

    with STORE_LOCK:
        SCORE_STORE[
            score_key
        ] = result

        RESUME_STORE[
            resume_id
        ]["status"] = "SCORED"

    return result


# ============================================================================
# SHORTLISTING
# ============================================================================


def shortlist_candidates(
    job_description_id: str,
    candidate_ids: List[str],
    top_n: int,
    shortlist_threshold: float,
    review_threshold: float,
) -> Dict[str, Any]:
    """Score and rank multiple candidates."""

    thresholds = RankingThresholds(
        shortlist=shortlist_threshold,
        review=review_threshold,
    )

    ranking_engine = CandidateRankingEngine(
        thresholds=thresholds
    )

    candidates = []

    for candidate_id in candidate_ids:

        result = score_resume(
            resume_id=candidate_id,
            job_description_id=(
                job_description_id
            ),
        )

        candidates.append(
            result
        )

    return ranking_engine.process_candidates(
        candidates=candidates,
        score_key="final_score",
        top_n=top_n,
    )


# ============================================================================
# ASYNC JOBS
# ============================================================================


def create_job(
    operation: str,
    job_description_id: str,
    resume_ids: List[str],
) -> Dict[str, Any]:
    """Create an asynchronous ATS processing job."""

    job_id = generate_job_id()

    record = {
        "job_id": job_id,
        "operation": operation,
        "job_description_id": (
            job_description_id
        ),
        "resume_ids": list(
            resume_ids
        ),
        "status": "QUEUED",
        "progress": 0,
        "result": None,
        "error": None,
    }

    with STORE_LOCK:
        JOB_STORE[
            job_id
        ] = record

    return record


def get_job(
    job_id: str,
) -> Dict[str, Any]:
    """Get an asynchronous job."""

    job = JOB_STORE.get(
        job_id
    )

    if job is None:
        raise LookupError(
            f"Job not found: {job_id}"
        )

    return job


def execute_job(
    job_id: str,
) -> None:
    """Execute an asynchronous score-and-rank job."""

    job = get_job(
        job_id
    )

    try:

        with STORE_LOCK:
            job["status"] = "PROCESSING"
            job["progress"] = 10

        if job["operation"] != "score_and_rank":
            raise ValueError(
                "Unsupported operation: "
                f"{job['operation']}"
            )

        resume_ids = job[
            "resume_ids"
        ]

        jd_id = job[
            "job_description_id"
        ]

        scores = []

        total = len(
            resume_ids
        )

        for index, resume_id in enumerate(
            resume_ids,
            start=1,
        ):

            result = score_resume(
                resume_id=resume_id,
                job_description_id=jd_id,
            )

            scores.append(
                result
            )

            with STORE_LOCK:
                job["progress"] = (
                    10
                    + int(
                        (
                            index
                            / total
                        )
                        * 80
                    )
                )

        ranking_engine = CandidateRankingEngine()

        ranking_result = (
            ranking_engine.process_candidates(
                candidates=scores,
                score_key="final_score",
                top_n=5,
            )
        )

        with STORE_LOCK:
            job["status"] = "COMPLETED"
            job["progress"] = 100
            job["result"] = ranking_result

    except Exception as exc:

        with STORE_LOCK:
            job["status"] = "FAILED"
            job["error"] = {
                "code": "PROCESSING_ERROR",
                "message": str(exc),
            }
# ============================================================================
# HEALTH CHECK
# ============================================================================


def health_status() -> Dict[str, str]:
    """Return ATS API health information."""

    return {
        "status": "healthy",
        "service": "Zecpath ATS API",
        "version": "v1",
    }