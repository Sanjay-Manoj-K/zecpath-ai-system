Day 22 HR Screening Dataset bundle

Merge the contents of this ZIP into the root of your existing repository:
E:\Zecser Tecnology\Tasks Completed\zecpath-ai-system

New files included:
- data/hr_screening/questions.json
- data/hr_screening/category_mapping.json
- data/hr_screening/question_templates.json
- data/hr_screening/roles.json
- screening_ai/__init__.py
- screening_ai/question_bank.py
- tests/test_hr_question_bank.py
- DAY22_HR_Screening_Dataset.md

The bundle does not overwrite screening_ai/screening_engine.py or the other empty placeholders. It adds a data-first question bank utility separately.

Validation commands from PowerShell at the repository root:
python -m pytest .\tests\test_hr_question_bank.py -q
python -m pytest -q

The first dataset language is en-IN. Translation fields are ready to populate but are intentionally empty until reviewed translations are available.
