"""Day 21 rule-based candidate eligibility decisions."""
from typing import Any, Dict, List, Optional

from .config import EligibilityRules

ELIGIBLE = "ELIGIBLE"
REVIEW = "REVIEW"
REJECTED = "REJECTED"


def _normalise_text(value: Any) -> str:
    return " ".join(str(value).strip().casefold().split())


_SKILL_ALIASES = {
    "rest apis": "rest api",
    "restful api": "rest api",
    "restful apis": "rest api",
}


def _normalise_skill(value: Any) -> str:
    """Normalize known equivalent skill labels."""
    normalized = _normalise_text(value)
    return _SKILL_ALIASES.get(normalized, normalized)


def _number_or_none(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def evaluate_eligibility(
    candidate: Dict[str, Any],
    rules: EligibilityRules,
) -> Dict[str, Any]:
    """Evaluate a candidate and return a decision with reasons.

    Confirmed rule failures result in REJECTED. Missing or invalid information
    required by a configured rule results in REVIEW unless a confirmed failure
    also exists.
    """
    if not isinstance(candidate, dict):
        raise TypeError("candidate must be a dictionary")

    passed: List[str] = []
    failed: List[str] = []
    review_reasons: List[str] = []

    score = _number_or_none(
        candidate.get("ats_score", candidate.get("final_score"))
    )
    if score is None or not 0.0 <= score <= 1.0:
        review_reasons.append("ATS score is missing or invalid; manual review is required.")
    elif score < rules.minimum_ats_score:
        failed.append(
            "ATS score {:.3f} is below the minimum {:.3f}.".format(
                score, rules.minimum_ats_score
            )
        )
    else:
        passed.append("ATS score meets the configured minimum.")

    if rules.mandatory_skills:
        raw_skills = candidate.get("skills")
        if raw_skills is None or not isinstance(raw_skills, list) or not raw_skills:
            review_reasons.append("Skills are missing or invalid; manual review is required.")
        else:
            skills = {
                _normalise_skill(skill)
                for skill in raw_skills
                if str(skill).strip()
            }
            missing = [
                skill for skill in rules.mandatory_skills
                if _normalise_skill(skill) not in skills
            ]
            if missing:
                failed.append("Mandatory skill(s) not found: {}.".format(", ".join(missing)))
            else:
                passed.append("All configured mandatory skills were found.")

    if rules.min_experience_years is not None or rules.max_experience_years is not None:
        years = _number_or_none(candidate.get("experience_years"))
        if years is None or years < 0:
            review_reasons.append(
                "Experience duration is missing or invalid; manual review is required."
            )
        elif rules.min_experience_years is not None and years < rules.min_experience_years:
            failed.append(
                "Experience {:.2f} years is below the minimum {:.2f} years.".format(
                    years, rules.min_experience_years
                )
            )
        elif rules.max_experience_years is not None and years > rules.max_experience_years:
            failed.append(
                "Experience {:.2f} years exceeds the maximum {:.2f} years.".format(
                    years, rules.max_experience_years
                )
            )
        else:
            passed.append("Experience duration is within the configured range.")

    if rules.allowed_locations:
        location = candidate.get("location")
        if not isinstance(location, str) or not location.strip():
            review_reasons.append("Location is missing; manual review is required.")
        elif _normalise_text(location) not in {
            _normalise_text(item) for item in rules.allowed_locations
        }:
            failed.append("Candidate location is outside the allowed locations.")
        else:
            passed.append("Candidate location meets the configured rule.")

    if rules.require_availability_confirmation:
        availability = candidate.get("availability_confirmed")
        if not isinstance(availability, bool):
            review_reasons.append(
                "Availability is not confirmed; manual review is required."
            )
        elif not availability:
            failed.append("Candidate availability does not meet the configured requirement.")
        else:
            passed.append("Candidate availability meets the configured requirement.")

    if failed:
        decision = REJECTED
    elif review_reasons:
        decision = REVIEW
    else:
        decision = ELIGIBLE

    return {
        "candidate_id": str(candidate.get("candidate_id", candidate.get("resume_id", ""))),
        "role": rules.role,
        "decision": decision,
        "ats_score": score,
        "reasons": failed + review_reasons + passed,
        "passed_rules": passed,
        "failed_rules": failed,
        "review_reasons": review_reasons,
        "review_required": decision == REVIEW,
    }

