# Day 5 - Resume Text Extraction
# Day 6 - Job Description Reading
# Day 7 - ATS Scoring
# Day 8 - Resume Section Segmentation

from parsers.resume_section_classifier import ResumeSectionClassifier
from parsers.resume_text_extractor import extract_resume_text
from parsers.resume_parser import parse_resume_text
from parsers.jd_parser import (
    read_job_description,
    parse_job_description
)

from ats_engine.ats_engine.candidate_profile import CandidateProfile
from ats_engine.ats_engine.job_requirement import JobRequirement

from ats_engine.ats_scoring import ATSScore


def main():

    # =========================================================
    # DAY 5 - RESUME TEXT EXTRACTION
    # =========================================================

    resume_file_path = "data/resumes/ai-developer-resume.docx"

    resume_text = extract_resume_text(resume_file_path)

    print("\n==============================")
    print("===== EXTRACTED RESUME =====")
    print("==============================\n")

    print(resume_text)

    # =========================================================
    # RESUME PARSING
    # =========================================================

    candidate_data = parse_resume_text(resume_text)

    candidate_profile = CandidateProfile(**candidate_data)

    print("\n===== PYDANTIC CANDIDATE VALIDATION =====")
    print("Candidate Profile validation successful!")

    # =========================================================
    # CANDIDATE PROFILE
    # =========================================================

    print("\n===== CANDIDATE PROFILE =====")

    print("Name:", candidate_profile.name)
    print("Skills:", candidate_profile.skills)
    print("Experience:", candidate_profile.experience)
    print("Education:", candidate_profile.education)
    print("Certifications:", candidate_profile.certifications)
    print("Languages:", candidate_profile.languages)

    # =========================================================
    # DAY 6 - JOB DESCRIPTION READING
    # =========================================================

    jd_file_path = "data/job_descriptions/python_developer.txt"

    jd_text = read_job_description(jd_file_path)

    print("\n==============================")
    print("===== JOB DESCRIPTION =====")
    print("==============================\n")

    print(jd_text)

    # =========================================================
    # JOB DESCRIPTION PARSING
    # =========================================================

    job_requirements = parse_job_description(jd_text)

    job_requirement = JobRequirement(**job_requirements)

    print("\n===== PYDANTIC JOB VALIDATION =====")
    print("Job Requirement validation successful!")

    # =========================================================
    # JOB REQUIREMENT OBJECT
    # =========================================================

    print("\n===== JOB REQUIREMENT OBJECT =====")

    print("Role:", job_requirement.role)
    print("Required Skills:", job_requirement.required_skills)
    print("Experience:", job_requirement.experience)
    print("Education:", job_requirement.education)
    print("Responsibilities:", job_requirement.responsibilities)

    # =========================================================
    # STRUCTURED JOB REQUIREMENTS
    # =========================================================

    print("\n===== STRUCTURED JOB REQUIREMENTS =====")

    print("Role:", job_requirement.role)

    print("\nRequired Skills:")

    for skill in job_requirement.required_skills:
        print("-", skill)

    print("\nExperience:", job_requirement.experience)

    print("Education:", job_requirement.education)

    print("\nResponsibilities:")

    for responsibility in job_requirement.responsibilities:
        print("-", responsibility)

    # =========================================================
    # DAY 7 - ATS SCORING
    # =========================================================

    print("\n==============================")
    print("===== DAY 7 - ATS SCORING =====")
    print("==============================")

    ats_score = ATSScore(
        candidate_profile,
        job_requirement
    )

    report = ats_score.generate_report()

    # =========================================================
    # ATS MATCHING REPORT
    # =========================================================

    print("\n==============================")
    print("===== ATS MATCHING REPORT =====")
    print("==============================")

    # ---------------------------------------------------------
    # SCORE SUMMARY
    # ---------------------------------------------------------

    print("\n===== ATS SCORE SUMMARY =====")

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

    print("\n===== EXPERIENCE DETAILS =====")

    candidate_experience = report.get(
        "total_experience_years",
        0
    )

    required_experience = ats_score.extract_years(
        ats_score.job.experience
    )

    print(
        f"Candidate Experience: "
        f"{candidate_experience:.2f} years"
    )

    print(
        f"Required Experience: "
        f"{required_experience:.2f} years"
    )

    if candidate_experience >= required_experience:

        print(
            "Experience Requirement: MET"
        )

    else:

        print(
            "Experience Requirement: NOT MET"
        )

    # =========================================================
    # SKILL MATCHING
    # =========================================================

    print("\n===== SKILL MATCHING =====")

    matched_skills = report["matched_skills"]
    missing_skills = report["missing_skills"]

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

    if matched_skills:

        print("\nMatched Skills:")

        for skill in matched_skills:
            print(f"  ✓ {skill}")

    else:

        print("\nMatched Skills:")
        print("  None")

    # ---------------------------------------------------------
    # MISSING SKILLS
    # ---------------------------------------------------------

    if missing_skills:

        print("\nMissing Skills:")

        for skill in missing_skills:
            print(f"  ✗ {skill}")

    else:

        print("\nMissing Skills:")
        print("  None")

    # =========================================================
    # DAY 8 - RESUME SECTION SEGMENTATION
    # =========================================================

    print("\n==============================")
    print("===== DAY 8 - RESUME SECTION SEGMENTATION =====")
    print("==============================")

    # Create classifier
    classifier = ResumeSectionClassifier()

    # ---------------------------------------------------------
    # SEGMENT RESUME
    # ---------------------------------------------------------

    sections = classifier.segment(resume_text)

    # ---------------------------------------------------------
    # DISPLAY SEGMENTED SECTIONS
    # ---------------------------------------------------------

    classifier.print_sections(sections)

    # =========================================================
    # DAY 8 - DETAILED BLOCK CLASSIFICATION
    # =========================================================

    print("\n========================================")
    print("===== DAY 8 - DETAILED CLASSIFICATION =====")
    print("========================================")

    detailed_blocks = classifier.classify_blocks(
        resume_text
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
            "Text       : "
            f"{block['text'][:300]}"
        )

    # =========================================================
    # DAY 8 - SECTION SUMMARY
    # =========================================================

    print("\n========================================")
    print("===== DAY 8 - SECTION SUMMARY =====")
    print("========================================")

    for section, contents in sections.items():

        print(
            f"{section:25} : "
            f"{len(contents)} block(s)"
        )

    # =========================================================
    # FINAL ANALYSIS SUMMARY
    # =========================================================

    print("\n========================================")
    print("===== FINAL ANALYSIS SUMMARY =====")
    print("========================================")

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
        f"{'MET' if candidate_experience >= required_experience else 'NOT MET'}"
    )

    print(
        f"Skills Matched: "
        f"{total_matched_skills}/"
        f"{total_required_skills}"
    )

    print(
        f"Skills Missing: "
        f"{len(missing_skills)}"
    )

    print(
        f"Resume Sections Detected: "
        f"{sum(1 for contents in sections.values() if contents)}"
    )

    print(
        f"Resume Blocks Classified: "
        f"{len(detailed_blocks)}"
    )

    # =========================================================
    # PROCESS COMPLETED
    # =========================================================

    print("\n==============================")
    print("===== PROCESS COMPLETED =====")
    print("==============================")


# =============================================================
# PROGRAM ENTRY POINT
# =============================================================

if __name__ == "__main__":
    main()