"""Load and validate the structured HR screening question bank.

This module is intentionally data-first: it selects questions and prepares
conversation-ready objects but does not make hiring decisions or score candidates.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path("data") / "hr_screening"

REQUIRED_QUESTION_FIELDS = {
    "question_id", "role_id", "category_id", "question_text",
    "expected_answer_type", "mandatory", "scoring_importance",
    "template_id", "language", "translations", "guidance",
}


class QuestionBankError(ValueError):
    """Raised when a question-bank dataset is malformed or inconsistent."""


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8-sig") as stream:
            value = json.load(stream)
    except FileNotFoundError as exc:
        raise QuestionBankError("Required question-bank file not found: {}".format(path)) from exc
    except json.JSONDecodeError as exc:
        raise QuestionBankError("Invalid JSON in {}: {}".format(path, exc)) from exc
    if not isinstance(value, dict):
        raise QuestionBankError("Top-level JSON value must be an object: {}".format(path))
    return value


def load_question_bank(root: Optional[Path] = None) -> Dict[str, Any]:
    """Load and cross-validate questions, categories, roles, and templates."""
    project_root = Path(root) if root is not None else DEFAULT_ROOT
    data_root = project_root / DATA_DIR
    question_doc = _read_json(data_root / "questions.json")
    category_doc = _read_json(data_root / "category_mapping.json")
    template_doc = _read_json(data_root / "question_templates.json")
    role_doc = _read_json(data_root / "roles.json")

    questions = question_doc.get("questions")
    categories = category_doc.get("categories")
    roles = role_doc.get("roles")
    templates = template_doc.get("templates")
    if not isinstance(questions, list) or not questions:
        raise QuestionBankError("The dataset must contain a non-empty questions list.")
    if not isinstance(categories, dict) or not categories:
        raise QuestionBankError("Category mapping must be a non-empty object.")
    if not isinstance(roles, list) or not roles:
        raise QuestionBankError("Role configuration must contain a non-empty roles list.")
    if not isinstance(templates, list) or not templates:
        raise QuestionBankError("Template file must contain a non-empty templates list.")

    role_ids = [r.get("role_id") for r in roles if isinstance(r, dict)]
    template_ids = [t.get("template_id") for t in templates if isinstance(t, dict)]
    question_ids = []
    for question in questions:
        if not isinstance(question, dict):
            raise QuestionBankError("Every question entry must be an object.")
        missing = REQUIRED_QUESTION_FIELDS - set(question)
        if missing:
            raise QuestionBankError("Question is missing fields: {}".format(sorted(missing)))
        question_ids.append(question["question_id"])
        if question["role_id"] not in role_ids:
            raise QuestionBankError("Unknown role_id in question {}: {}".format(question["question_id"], question["role_id"]))
        if question["category_id"] not in categories:
            raise QuestionBankError("Unknown category_id in question {}: {}".format(question["question_id"], question["category_id"]))
        if question["template_id"] not in template_ids:
            raise QuestionBankError("Unknown template_id in question {}: {}".format(question["question_id"], question["template_id"]))
        if not isinstance(question["mandatory"], bool):
            raise QuestionBankError("mandatory must be a boolean for {}".format(question["question_id"]))
        importance = question["scoring_importance"]
        if isinstance(importance, bool) or not isinstance(importance, int) or not 1 <= importance <= 5:
            raise QuestionBankError("scoring_importance must be an integer from 1 to 5 for {}".format(question["question_id"]))
        if not isinstance(question["question_text"], str) or not question["question_text"].strip():
            raise QuestionBankError("question_text must be a non-empty string for {}".format(question["question_id"]))
        if not isinstance(question["translations"], dict):
            raise QuestionBankError("translations must be an object for {}".format(question["question_id"]))
    if len(set(question_ids)) != len(question_ids):
        raise QuestionBankError("question_id values must be unique.")
    if len(set(role_ids)) != len(role_ids):
        raise QuestionBankError("role_id values must be unique.")
    if len(set(template_ids)) != len(template_ids):
        raise QuestionBankError("template_id values must be unique.")

    return {
        "dataset": question_doc,
        "categories": categories,
        "roles": roles,
        "templates": templates,
    }


def get_questions(
    role_id: Optional[str] = None,
    category_id: Optional[str] = None,
    mandatory_only: bool = False,
    language: Optional[str] = None,
    root: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Return matching question objects; use a translation if one is available."""
    bank = load_question_bank(root)
    valid_role_ids = {role["role_id"] for role in bank["roles"]}
    if role_id is not None and role_id not in valid_role_ids:
        raise ValueError("Unknown role_id: {}".format(role_id))
    if category_id is not None and category_id not in bank["categories"]:
        raise ValueError("Unknown category_id: {}".format(category_id))

    selected = []
    for original in bank["dataset"]["questions"]:
        if role_id is not None and original["role_id"] != role_id:
            continue
        if category_id is not None and original["category_id"] != category_id:
            continue
        if mandatory_only and not original["mandatory"]:
            continue
        question = deepcopy(original)
        target_language = language or bank["dataset"].get("default_language", "en-IN")
        translation = question["translations"].get(target_language)
        if isinstance(translation, str) and translation.strip():
            question["question_text"] = translation
            question["language"] = target_language
        selected.append(question)
    return selected


def build_conversation_payload(role_id: str, language: str = "en-IN", mandatory_only: bool = False,
                               root: Optional[Path] = None) -> Dict[str, Any]:
    """Build a portable payload suitable for a later conversational screening layer."""
    bank = load_question_bank(root)
    role = next((r for r in bank["roles"] if r["role_id"] == role_id), None)
    if role is None:
        raise ValueError("Unknown role_id: {}".format(role_id))
    questions = get_questions(role_id=role_id, mandatory_only=mandatory_only, language=language, root=root)
    return {
        "schema_version": "1.0.0",
        "role_id": role_id,
        "role_label": role.get("label", role_id),
        "language": language,
        "questions": questions,
        "note": "scoring_importance is a recruiter-defined priority label, not an automated hiring decision.",
    }
