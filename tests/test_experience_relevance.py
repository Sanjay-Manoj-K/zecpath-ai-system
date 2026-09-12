"""
Day 10 - Experience Relevance Test

Uses the actual resume file.

Usage:

    python tests/test_experience_relevance.py

or:

    python tests/test_experience_relevance.py \
        data/resumes/finance-resume.docx
"""

import sys

from parsers.resume_text_extractor import (
    extract_resume_text
)

from parsers.resume_section_classifier import (
    ResumeSectionClassifier
)

from parsers.jd_parser import (
    read_job_description,
    parse_job_description
)

from ats_engine.ats_engine.job_requirement import (
    JobRequirement
)

from parsers.experience_parser import (
    ExperienceParser
)

from scoring.experience_relevance import (
    ExperienceRelevanceScorer
)


def main():

    # =========================================================
    # RESUME FILE
    # =========================================================

    if len(sys.argv) > 1:

        resume_file_path = sys.argv[1]

    else:

        resume_file_path = (
            "data/resumes/ai-developer-resume.docx"
        )

    print(
        "\n=============================================="
    )

    print(
        "===== DAY 10 - EXPERIENCE RELEVANCE TEST ====="
    )

    print(
        "=============================================="
    )

    print(
        f"\nResume: {resume_file_path}"
    )

    # =========================================================
    # DAY 5 - RESUME TEXT EXTRACTION
    # =========================================================

    resume_text = extract_resume_text(
        resume_file_path
    )

    if not resume_text.strip():

        print(
            "\nERROR: Resume text is empty."
        )

        return

    # =========================================================
    # DAY 8 - SECTION SEGMENTATION
    # =========================================================

    classifier = ResumeSectionClassifier()

    sections = classifier.segment(
        resume_text
    )

    work_experience_sections = (
        sections.get(
            "work_experience",
            []
        )
    )

    print(
        "\n===== WORK EXPERIENCE SECTION ====="
    )

    if work_experience_sections:

        for block in (
            work_experience_sections
        ):

            print(block)

            print(
                "----------------------------------------"
            )

    else:

        print(
            "No work experience section detected."
        )

        return

    # =========================================================
    # DAY 10 - EXPERIENCE PARSING
    # =========================================================

    experience_text = "\n".join(
        work_experience_sections
    )

    experience_parser = ExperienceParser()

    experience_result = (
        experience_parser.parse_experience(
            experience_text
        )
    )

    print(
        "\n===== PARSED EXPERIENCE ====="
    )

    experience_parser.print_results(
        experience_result
    )

    # =========================================================
    # JOB DESCRIPTION
    # =========================================================

    jd_file_path = (
        "data/job_descriptions/"
        "python_developer.txt"
    )

    jd_text = read_job_description(
        jd_file_path
    )

    job_data = parse_job_description(
        jd_text
    )

    job_requirement = JobRequirement(
        **job_data
    )

    print(
        "\n===== TARGET JOB ====="
    )

    print(
        f"Role: "
        f"{job_requirement.role}"
    )

    print(
        "Required Skills:"
    )

    for skill in (
        job_requirement.required_skills
    ):

        print(
            f"- {skill}"
        )

    # =========================================================
    # DAY 10 - EXPERIENCE RELEVANCE
    # =========================================================

    scorer = ExperienceRelevanceScorer()

    relevance_result = (
        scorer.score_experiences(
            experience_result[
                "experiences"
            ],
            job_requirement
        )
    )

    # =========================================================
    # DISPLAY
    # =========================================================

    scorer.print_results(
        relevance_result
    )


if __name__ == "__main__":
    main()