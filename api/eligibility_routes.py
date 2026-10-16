"""Day 21 Eligibility Decision Engine API."""

from pathlib import Path

from fastapi import APIRouter, HTTPException

from api.eligibility_schemas import EligibilityRequest, EligibilityResponse
from api.services import get_resume, score_resume
from eligibility.config import load_rules_for_role
from eligibility.decision_engine import evaluate_eligibility


router = APIRouter(tags=["Eligibility"])

RULES_PATH = (
    Path(__file__).resolve().parent.parent
    / "configs"
    / "eligibility_rules.json"
)


@router.post(
    "/api/v1/resumes/{resume_id}/eligibility",
    response_model=EligibilityResponse,
)
def evaluate_resume_eligibility(
    resume_id: str,
    body: EligibilityRequest,
):
    """Evaluate a parsed resume using its ATS score and role rules."""

    try:
        resume = get_resume(resume_id)

        profile = resume.get("parsed_profile")
        if not isinstance(profile, dict):
            raise HTTPException(
                status_code=409,
                detail="Parse this resume before evaluating eligibility.",
            )

        rules = load_rules_for_role(
            str(RULES_PATH),
            body.role,
        )

        score_result = score_resume(
            resume_id=resume_id,
            job_description_id=body.job_description_id,
        )

        candidate = {
            "resume_id": resume_id,
            "ats_score": score_result.get("final_score"),
            "skills": profile.get("skills"),
            "experience_years": body.experience_years,
            "location": body.location,
            "availability_confirmed": body.availability_confirmed,
        }

        decision = evaluate_eligibility(candidate, rules)

        return EligibilityResponse(
            job_description_id=body.job_description_id,
            **decision,
        )

    except HTTPException:
        raise

    except KeyError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid eligibility role: {}".format(exc),
        ) from exc

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
