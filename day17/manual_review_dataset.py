"""
Day 17 - ATS System Testing
Controlled manual-reference dataset.

The role/resume positive mappings come from the existing Day 12
controlled benchmark:
- AI / ML Engineer -> ai-developer-resume.docx
- Data Scientist -> data-scientist-resume.pdf
- Finance Analyst -> finance-resume.docx
- Legal Intern -> legal-resume.docx
- Software Engineer -> software-engineering-resume.docx

All other resume/JD combinations are treated as negative reference cases.
"""

from pathlib import Path


BASE_RESUME_DIR = Path("data/resumes")
BASE_JD_DIR = Path("data/day12_benchmarks")


RESUMES = [
    "ai-developer-resume.docx",
    "asst-report-writter-resume.docx",
    "bussines-strategist-resume.docx",
    "data-scientist-resume.pdf",
    "Fernandus_Bernard_Resume.docx",
    "finance-resume.docx",
    "Junior_Python_Developer_Resume.docx",
    "legal-resume.docx",
    "marketing-resume.docx",
    "mechanical-engineering-resume.docx",
    "software-engineering-resume.docx",
    "tax-resume.docx",
]


JOBS = {
    "ai_ml_engineer": {
        "file": "ai_ml_engineer.txt",
        "role_type": "tech",
        "positive_resume": "ai-developer-resume.docx",
    },
    "data_scientist": {
        "file": "data_scientist.txt",
        "role_type": "tech",
        "positive_resume": "data-scientist-resume.pdf",
    },
    "finance_analyst": {
        "file": "finance_analyst.txt",
        "role_type": "non-tech",
        "positive_resume": "finance-resume.docx",
    },
    "legal_intern": {
        "file": "legal_intern.txt",
        "role_type": "non-tech",
        "positive_resume": "legal-resume.docx",
    },
    "software_engineer": {
        "file": "software_engineer.txt",
        "role_type": "tech",
        "positive_resume": "software-engineering-resume.docx",
    },
}


def build_manual_reference_dataset():
    cases = []

    for job_id, job in JOBS.items():
        for resume_name in RESUMES:

            manual_suitable = (
                resume_name == job["positive_resume"]
            )

            cases.append(
                {
                    "case_id": f"{job_id}__{Path(resume_name).stem}",
                    "resume_file": str(
                        BASE_RESUME_DIR / resume_name
                    ),
                    "job_file": str(
                        BASE_JD_DIR / job["file"]
                    ),
                    "role": job_id,
                    "role_type": job["role_type"],
                    "manual_suitable": manual_suitable,
                    "manual_basis": (
                        "Controlled positive benchmark pair"
                        if manual_suitable
                        else "Controlled negative benchmark pair"
                    ),
                }
            )

    return cases


if __name__ == "__main__":
    dataset = build_manual_reference_dataset()

    print("=" * 70)
    print("DAY 17 MANUAL REFERENCE DATASET")
    print("=" * 70)
    print(f"Total test cases: {len(dataset)}")

    positive = sum(
        1 for case in dataset
        if case["manual_suitable"]
    )

    negative = len(dataset) - positive

    print(f"Positive reference cases: {positive}")
    print(f"Negative reference cases: {negative}")
    print()

    for case in dataset:
        print(
            f"{case['role']:20} | "
            f"{Path(case['resume_file']).name:40} | "
            f"{'SUITABLE' if case['manual_suitable'] else 'NOT SUITABLE'}"
        )