# Day 22 — HR Screening Dataset Creation

## Objective
Create a structured, AI-ready question bank for automated HR screening calls.

## Deliverables
- `data/hr_screening/questions.json`: 42 role-specific question objects for Python Developer, AI/ML Engineer, and Software Developer.
- `data/hr_screening/category_mapping.json`: the seven categories from the task sheet and their metadata.
- `data/hr_screening/question_templates.json`: reusable templates and declared placeholders.
- `data/hr_screening/roles.json`: role identifiers, labels, language default, and question counts.
- `screening_ai/question_bank.py`: validates and loads the dataset, filters questions, and builds a conversation-ready payload.
- `tests/test_hr_question_bank.py`: automated structural and API-helper tests.

## Question object contract
Each question includes a stable identifier, role and category IDs, question text, expected answer type, mandatory flag, scoring-importance value (1–5), template ID, language tag, translations object, and guidance.

## Categories
Introduction, education, experience, skills, location, salary, and notice period.

## Roles and language support
The initial question text is English (`en-IN`). The `translations` object is intentionally empty until reviewed translations are supplied; it allows locale-specific strings such as `ml-IN` and `hi-IN` to be added without changing the object shape. The dataset is multilingual-ready in structure, but the initial dataset does not claim to contain completed translations.

## Validation
Run from the repository root:

```powershell
python -m pytest .\tests\test_hr_question_bank.py -q
python -m pytest -q
```

The automated question-bank tests validate JSON loading, unique IDs, category and role coverage, mandatory-only filtering, and conversation payload construction.

## Responsible-use note
`scoring_importance` is a recruiter-set question priority (1–5), not a candidate score or automatic hiring decision. Compensation, location and notice-period answers should be handled only for job-relevant purposes and reviewed by a human. This dataset does not perform candidate evaluation.
