# Day 5 - Resume Text Extraction
# Day 6 - Job Description Reading
# Day 7 - ATS Scoring
# Day 8 - Resume Section Segmentation
# Day 9 - Skill Extraction Engine

from parsers.resume_text_extractor import extract_resume_text
from parsers.resume_parser import parse_resume_text
from parsers.resume_section_classifier import (
    ResumeSectionClassifier
)
from parsers.skill_extraction_engine import (
    SkillExtractionEngine
)

from parsers.jd_parser import (
    read_job_description,
    parse_job_description
)

from ats_engine.ats_engine.candidate_profile import (
    CandidateProfile
)

from ats_engine.ats_engine.job_requirement import (
    JobRequirement
)

from ats_engine.ats_scoring import ATSScore


def main():

    # =========================================================
    # DAY 5 - RESUME TEXT EXTRACTION
    # =========================================================

    resume_file_path = (
        "data/resumes/ai-developer-resume.docx"
    )

    resume_text = extract_resume_text(
        resume_file_path
    )

    print("\n==============================")
    print("===== EXTRACTED RESUME =====")
    print("==============================\n")

    print(resume_text)

    # =========================================================
    # RESUME PARSING
    # =========================================================

    candidate_data = parse_resume_text(
        resume_text
    )

    candidate_profile = CandidateProfile(
        **candidate_data
    )

    print(
        "\n========================================"
    )
    print(
        "===== PYDANTIC CANDIDATE VALIDATION ====="
    )
    print(
        "========================================"
    )

    print(
        "Candidate Profile validation successful!"
    )

    # =========================================================
    # CANDIDATE PROFILE
    # =========================================================

    print(
        "\n===== CANDIDATE PROFILE ====="
    )

    print(
        "Name:",
        candidate_profile.name
    )

    print(
        "Skills:",
        candidate_profile.skills
    )

    print(
        "Experience:",
        candidate_profile.experience
    )

    print(
        "Education:",
        candidate_profile.education
    )

    print(
        "Certifications:",
        candidate_profile.certifications
    )

    print(
        "Languages:",
        candidate_profile.languages
    )

    # Save original parser skills before Day 9 modifies them.
    original_candidate_skills = list(
        candidate_profile.skills
    )

    # =========================================================
    # DAY 6 - JOB DESCRIPTION READING
    # =========================================================

    jd_file_path = (
        "data/job_descriptions/python_developer.txt"
    )

    jd_text = read_job_description(
        jd_file_path
    )

    print(
        "\n=============================="
    )
    print(
        "===== JOB DESCRIPTION ====="
    )
    print(
        "==============================\n"
    )

    print(jd_text)

    # =========================================================
    # JOB DESCRIPTION PARSING
    # =========================================================

    job_requirements = parse_job_description(
        jd_text
    )

    job_requirement = JobRequirement(
        **job_requirements
    )

    print(
        "\n========================================"
    )
    print(
        "===== PYDANTIC JOB VALIDATION ====="
    )
    print(
        "========================================"
    )

    print(
        "Job Requirement validation successful!"
    )

    # =========================================================
    # JOB REQUIREMENT OBJECT
    # =========================================================

    print(
        "\n===== JOB REQUIREMENT OBJECT ====="
    )

    print(
        "Role:",
        job_requirement.role
    )

    print(
        "Required Skills:",
        job_requirement.required_skills
    )

    print(
        "Experience:",
        job_requirement.experience
    )

    print(
        "Education:",
        job_requirement.education
    )

    print(
        "Responsibilities:",
        job_requirement.responsibilities
    )

    # =========================================================
    # DAY 8 - RESUME SECTION SEGMENTATION
    # =========================================================

    print(
        "\n=============================================="
    )
    print(
        "===== DAY 8 - RESUME SECTION SEGMENTATION ====="
    )
    print(
        "=============================================="
    )

    classifier = ResumeSectionClassifier()

    sections = classifier.segment(
        resume_text
    )

    detailed_blocks = (
        classifier.classify_blocks(
            resume_text
        )
    )

    # ---------------------------------------------------------
    # Display sections
    # ---------------------------------------------------------

    classifier.print_sections(
        sections
    )

    # ---------------------------------------------------------
    # Detailed classification
    # ---------------------------------------------------------

    if hasattr(
        classifier,
        "print_detailed_classification"
    ):

        classifier.print_detailed_classification(
            detailed_blocks
        )

    else:

        print(
            "\n===== DETAILED BLOCK CLASSIFICATION ====="
        )

        for block in detailed_blocks:

            print(
                f"\nBlock {block['block_id']}"
            )

            print(
                f"Section    : "
                f"{block['section']}"
            )

            print(
                f"Method     : "
                f"{block['method']}"
            )

            print(
                f"Confidence : "
                f"{block['confidence']}"
            )

            print(
                f"Text       : "
                f"{block['text'][:300]}"
            )

    # =========================================================
    # DAY 8 - SECTION SUMMARY
    # =========================================================

    if hasattr(
        classifier,
        "print_section_summary"
    ):

        classifier.print_section_summary(
            sections
        )

    else:

        print(
            "\n===== DAY 8 SECTION SUMMARY ====="
        )

        for section, contents in (
            sections.items()
        ):

            print(
                f"{section:<25}: "
                f"{len(contents)} block(s)"
            )

    # =========================================================
    # DAY 9 - SKILL EXTRACTION ENGINE
    # =========================================================

    print(
        "\n=============================================="
    )
    print(
        "===== DAY 9 - SKILL EXTRACTION ENGINE ====="
    )
    print(
        "=============================================="
    )

    skill_engine = SkillExtractionEngine()

    # ---------------------------------------------------------
    # Extract skills from Day 8 sections
    # ---------------------------------------------------------

    section_skill_result = (
        skill_engine.extract_from_sections(
            sections
        )
    )

    # ---------------------------------------------------------
    # Merge Day 8/Day 9 results with CandidateProfile skills
    #
    # This prevents valid skills from being lost when
    # DOCX extraction produces an empty Skills section.
    # ---------------------------------------------------------

    skill_result = (
        skill_engine.merge_candidate_skills(
            section_skill_result,
            original_candidate_skills
        )
    )

    # =========================================================
    # DAY 9 - UPDATE CANDIDATE PROFILE
    # =========================================================

    candidate_profile.skills = [
        skill["canonical"]
        for skill in skill_result["skills"]
    ]

    print(
        "\n===== UPDATED CANDIDATE SKILLS ====="
    )

    for skill in candidate_profile.skills:

        print(
            f"- {skill}"
        )

    # =========================================================
    # DAY 9 - DETAILED SKILL OUTPUT
    # =========================================================

    skill_engine.print_results(
        skill_result
    )

    # =========================================================
    # DAY 9 - COMPACT SKILL SUMMARY
    # =========================================================

    skill_engine.print_skill_summary(
        skill_result
    )

    # =========================================================
    # DAY 9 - UNIFIED SKILL SET
    # =========================================================

    print(
        "\n=============================================="
    )
    print(
        "===== DAY 9 - UNIFIED SKILL SET ====="
    )
    print(
        "=============================================="
    )

    normalized_skill_count = (
        skill_result["total_skills"]
    )

    print(
        f"\nUnified Skills Detected: "
        f"{normalized_skill_count}"
    )

    for skill in skill_result["skills"]:

        print(
            f"- {skill['canonical']}"
            f" | Category: {skill['category']}"
            f" | Confidence: "
            f"{skill['confidence']:.2f}"
            f" | Source: {skill['source']}"
            f" | Section: "
            f"{skill.get('section', 'unknown')}"
        )

    # =========================================================
    # DAY 9 - SOURCE BREAKDOWN
    # =========================================================

    print(
        "\n===== SKILL SOURCE BREAKDOWN ====="
    )

    source_counts = {}

    for skill in skill_result["skills"]:

        source = skill["source"]

        source_counts[source] = (
            source_counts.get(
                source,
                0
            ) + 1
        )

    for source, count in sorted(
        source_counts.items()
    ):

        print(
            f"{source:<25}: "
            f"{count}"
        )

    # =========================================================
    # DAY 9 - ORIGINAL VS UNIFIED
    # =========================================================

    print(
        "\n=============================================="
    )
    print(
        "===== DAY 9 - SKILL COMPARISON ====="
    )
    print(
        "=============================================="
    )

    print(
        "\nOriginal CandidateProfile Skills:"
    )

    if original_candidate_skills:

        for skill in original_candidate_skills:

            print(
                f"  - {skill}"
            )

    else:

        print(
            "  None"
        )

    print(
        "\nDay 9 Unified Skills:"
    )

    if skill_result["skills"]:

        for skill in skill_result["skills"]:

            print(
                f"  - {skill['canonical']}"
            )

    else:

        print(
            "  None"
        )

    # =========================================================
    # DAY 7 - ATS SCORING
    # =========================================================

    print(
        "\n=============================="
    )
    print(
        "===== DAY 7 - ATS SCORING ====="
    )
    print(
        "=============================="
    )

    # IMPORTANT:
    # CandidateProfile.skills now contains the normalized
    # Day 9 unified skills.
    #
    # Therefore ATSScore will use Day 9 skills.

    ats_score = ATSScore(
        candidate_profile,
        job_requirement
    )

    report = ats_score.generate_report()

    # =========================================================
    # ATS MATCHING REPORT
    # =========================================================

    print(
        "\n=============================="
    )
    print(
        "===== ATS MATCHING REPORT ====="
    )
    print(
        "=============================="
    )

    # =========================================================
    # ATS SCORE SUMMARY
    # =========================================================

    print(
        "\n===== ATS SCORE SUMMARY ====="
    )

    print(
        f"Overall ATS Score: "
        f"{report['overall_score']} %"
    )

    print(
        f"Skill Score: "
        f"{report['skill_score']} %"
    )

    print(
        f"Experience Score: "
        f"{report['experience_score']} %"
    )

    print(
        f"Education Score: "
        f"{report['education_score']} %"
    )

    # =========================================================
    # EXPERIENCE DETAILS
    # =========================================================

    print(
        "\n===== EXPERIENCE DETAILS ====="
    )

    candidate_experience = report.get(
        "total_experience_years",
        0
    )

    required_experience = (
        ats_score.extract_years(
            ats_score.job.experience
        )
    )

    experience_met = (
        candidate_experience
        >= required_experience
    )

    print(
        f"Candidate Experience: "
        f"{candidate_experience:.2f} years"
    )

    print(
        f"Required Experience: "
        f"{required_experience:.2f} years"
    )

    print(
        "Experience Requirement: "
        f"{'MET' if experience_met else 'NOT MET'}"
    )

    # =========================================================
    # ATS SKILL MATCHING
    # =========================================================

    print(
        "\n===== ATS SKILL MATCHING ====="
    )

    matched_skills = report[
        "matched_skills"
    ]

    missing_skills = report[
        "missing_skills"
    ]

    total_required_skills = len(
        ats_score.job.required_skills
    )

    total_matched_skills = len(
        matched_skills
    )

    print(
        f"Matched Skills: "
        f"{total_matched_skills}/"
        f"{total_required_skills}"
    )

    # ---------------------------------------------------------
    # MATCHED SKILLS
    # ---------------------------------------------------------

    print(
        "\nMatched Skills:"
    )

    if matched_skills:

        for skill in matched_skills:

            print(
                f"  ✓ {skill}"
            )

    else:

        print(
            "  None"
        )

    # ---------------------------------------------------------
    # MISSING SKILLS
    # ---------------------------------------------------------

    print(
        "\nMissing Skills:"
    )

    if missing_skills:

        for skill in missing_skills:

            print(
                f"  ✗ {skill}"
            )

    else:

        print(
            "  None"
        )

    # =========================================================
    # FINAL ANALYSIS SUMMARY
    # =========================================================

    detected_section_count = sum(
        1
        for contents in sections.values()
        if contents
    )

    classified_block_count = len(
        detailed_blocks
    )

    print(
        "\n=============================================="
    )
    print(
        "===== FINAL ANALYSIS SUMMARY ====="
    )
    print(
        "=============================================="
    )

    print(
        f"\nATS Score: "
        f"{report['overall_score']} %"
    )

    print(
        f"Skill Score: "
        f"{report['skill_score']} %"
    )

    print(
        f"Experience Score: "
        f"{report['experience_score']} %"
    )

    print(
        f"Education Score: "
        f"{report['education_score']} %"
    )

    print(
        f"Candidate Experience: "
        f"{candidate_experience:.2f} years"
    )

    print(
        f"Required Experience: "
        f"{required_experience:.2f} years"
    )

    print(
        f"Experience Requirement: "
        f"{'MET' if experience_met else 'NOT MET'}"
    )

    print(
        f"ATS Skills Matched: "
        f"{total_matched_skills}/"
        f"{total_required_skills}"
    )

    print(
        f"ATS Skills Missing: "
        f"{len(missing_skills)}"
    )

    print(
        f"Day 8 Sections Detected: "
        f"{detected_section_count}"
    )

    print(
        f"Day 8 Blocks Classified: "
        f"{classified_block_count}"
    )

    print(
        f"Day 9 Unified Skills: "
        f"{normalized_skill_count}"
    )

    # =========================================================
    # PROCESS COMPLETED
    # =========================================================

    print(
        "\n=============================="
    )
    print(
        "===== PROCESS COMPLETED ====="
    )
    print(
        "=============================="
    )


# =============================================================
# PROGRAM ENTRY POINT
# =============================================================

if __name__ == "__main__":
    main()