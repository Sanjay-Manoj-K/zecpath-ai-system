import json

import pytest

from eligibility.config import EligibilityRules, load_rules_for_role
from eligibility.decision_engine import ELIGIBLE, REJECTED, REVIEW, evaluate_eligibility


def make_rules(**overrides):
    data = {
        "role": "test_role",
        "minimum_ats_score": 0.70,
        "mandatory_skills": ["Python", "REST API"],
    }
    data.update(overrides)
    return EligibilityRules(**data)


def make_candidate(**overrides):
    data = {
        "candidate_id": "C-1",
        "final_score": 0.85,
        "skills": ["Python", "REST API"],
    }
    data.update(overrides)
    return data


def test_qualified_candidate_is_eligible():
    assert evaluate_eligibility(make_candidate(), make_rules())["decision"] == ELIGIBLE


def test_low_score_is_rejected():
    result = evaluate_eligibility(make_candidate(final_score=0.60), make_rules())
    assert result["decision"] == REJECTED
    assert result["failed_rules"]


def test_missing_mandatory_skill_is_rejected():
    result = evaluate_eligibility(make_candidate(skills=["Python"]), make_rules())
    assert result["decision"] == REJECTED
    assert "REST API" in result["failed_rules"][0]


def test_skill_matching_is_case_insensitive():
    result = evaluate_eligibility(
        make_candidate(skills=["python", "rest api"]), make_rules()
    )
    assert result["decision"] == ELIGIBLE


def test_missing_score_requires_review():
    candidate = make_candidate()
    del candidate["final_score"]
    assert evaluate_eligibility(candidate, make_rules())["decision"] == REVIEW


def test_missing_skills_requires_review():
    candidate = make_candidate()
    del candidate["skills"]
    assert evaluate_eligibility(candidate, make_rules())["decision"] == REVIEW


def test_experience_below_minimum_is_rejected():
    rules = make_rules(min_experience_years=2)
    result = evaluate_eligibility(make_candidate(experience_years=1), rules)
    assert result["decision"] == REJECTED


def test_experience_above_maximum_is_rejected():
    rules = make_rules(max_experience_years=3)
    result = evaluate_eligibility(make_candidate(experience_years=4), rules)
    assert result["decision"] == REJECTED


def test_missing_required_experience_requires_review():
    rules = make_rules(min_experience_years=1)
    result = evaluate_eligibility(make_candidate(), rules)
    assert result["decision"] == REVIEW


def test_allowed_location_is_case_insensitive():
    rules = make_rules(allowed_locations=["Kochi", "Kozhikode"])
    result = evaluate_eligibility(make_candidate(location="KOCHI"), rules)
    assert result["decision"] == ELIGIBLE


def test_disallowed_location_is_rejected():
    rules = make_rules(allowed_locations=["Kochi"])
    result = evaluate_eligibility(make_candidate(location="Chennai"), rules)
    assert result["decision"] == REJECTED


def test_missing_required_location_requires_review():
    rules = make_rules(allowed_locations=["Kochi"])
    result = evaluate_eligibility(make_candidate(), rules)
    assert result["decision"] == REVIEW


def test_unavailable_candidate_is_rejected_when_required():
    rules = make_rules(require_availability_confirmation=True)
    result = evaluate_eligibility(
        make_candidate(availability_confirmed=False), rules
    )
    assert result["decision"] == REJECTED


def test_missing_availability_requires_review():
    rules = make_rules(require_availability_confirmation=True)
    result = evaluate_eligibility(make_candidate(), rules)
    assert result["decision"] == REVIEW


def test_invalid_experience_range_is_rejected():
    with pytest.raises(ValueError):
        make_rules(min_experience_years=5, max_experience_years=2)


def test_score_threshold_must_use_zero_to_one_scale():
    with pytest.raises(ValueError):
        make_rules(minimum_ats_score=70)


def test_rules_load_from_json(tmp_path):
    path = tmp_path / "rules.json"
    path.write_text(
        json.dumps({"roles": {"qa": {"minimum_ats_score": 0.6,
                                     "mandatory_skills": ["Testing"]}}}),
        encoding="utf-8",
    )
    rules = load_rules_for_role(str(path), "qa")
    assert rules.role == "qa"
    assert rules.minimum_ats_score == 0.6


def test_unknown_role_raises_clear_error(tmp_path):
    path = tmp_path / "rules.json"
    path.write_text('{"roles": {}}', encoding="utf-8")
    with pytest.raises(KeyError):
        load_rules_for_role(str(path), "missing")
def test_rest_apis_matches_rest_api():
    result = evaluate_eligibility(
        make_candidate(skills=["Python", "REST APIs"]),
        make_rules(),
    )
    assert result["decision"] == ELIGIBLE


def test_restful_api_matches_rest_api():
    result = evaluate_eligibility(
        make_candidate(skills=["Python", "RESTful API"]),
        make_rules(),
    )
    assert result["decision"] == ELIGIBLE