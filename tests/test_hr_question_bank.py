import json
from pathlib import Path

import pytest

from screening_ai.question_bank import (
    QuestionBankError,
    build_conversation_payload,
    get_questions,
    load_question_bank,
)

ROOT = Path(__file__).resolve().parents[1]


def test_dataset_loads_and_has_42_questions():
    bank = load_question_bank(ROOT)
    assert bank["dataset"]["question_count"] == 42
    assert len(bank["dataset"]["questions"]) == 42


def test_each_role_has_14_questions_across_all_seven_categories():
    bank = load_question_bank(ROOT)
    for role in bank["roles"]:
        qs = get_questions(role_id=role["role_id"], root=ROOT)
        assert len(qs) == 14
        assert {q["category_id"] for q in qs} == set(bank["categories"].keys())


def test_question_ids_are_unique_and_importance_is_valid():
    bank = load_question_bank(ROOT)
    qs = bank["dataset"]["questions"]
    assert len({q["question_id"] for q in qs}) == len(qs)
    assert all(1 <= q["scoring_importance"] <= 5 for q in qs)


def test_mandatory_filter_only_returns_mandatory_questions():
    qs = get_questions(role_id="python_developer", mandatory_only=True, root=ROOT)
    assert qs
    assert all(q["mandatory"] is True for q in qs)


def test_category_filter_returns_matching_questions():
    qs = get_questions(role_id="ai_ml_engineer", category_id="skills", root=ROOT)
    assert len(qs) == 2
    assert all(q["category_id"] == "skills" for q in qs)


def test_payload_has_conversation_ready_metadata():
    payload = build_conversation_payload("software_developer", root=ROOT)
    assert payload["schema_version"] == "1.0.0"
    assert payload["role_id"] == "software_developer"
    assert len(payload["questions"]) == 14
    assert payload["language"] == "en-IN"


def test_unknown_role_is_rejected():
    with pytest.raises(ValueError, match="Unknown role_id"):
        get_questions(role_id="unknown_role", root=ROOT)


def test_dataset_json_files_are_valid_json():
    folder = ROOT / "data" / "hr_screening"
    for name in ("questions.json", "category_mapping.json", "question_templates.json", "roles.json"):
        with (folder / name).open("r", encoding="utf-8") as stream:
            json.load(stream)
