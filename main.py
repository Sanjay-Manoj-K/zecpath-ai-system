# Day 5 - Resume Text Extraction
# Day 6 - Job Description Reading
# Candidate Profile + Job Requirement Validation

from parsers.resume_text_extractor import extract_resume_text
from parsers.resume_parser import parse_resume_text
from parsers.jd_parser import read_job_description, parse_job_description

from ats_engine.ats_engine.candidate_profile import CandidateProfile
from ats_engine.ats_engine.job_requirement import JobRequirement


def main():

    # =========================================================
    # DAY 5 - RESUME TEXT EXTRACTION
    # =========================================================

    resume_file_path = "data/resumes/ai-developer-resume.docx"

    # Extract text from resume
    resume_text = extract_resume_text(resume_file_path)

    print("\n==============================")
    print("===== EXTRACTED RESUME =====")
    print("==============================\n")

    print(resume_text)

    # =========================================================
    # RESUME PARSING
    # =========================================================

    candidate_data = parse_resume_text(resume_text)

    # Validate candidate data using Pydantic
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

    # Read job description
    jd_text = read_job_description(jd_file_path)

    print("\n==============================")
    print("===== JOB DESCRIPTION =====")
    print("==============================\n")

    print(jd_text)

    # =========================================================
    # JOB DESCRIPTION PARSING
    # =========================================================

    job_requirements = parse_job_description(jd_text)

    # =========================================================
    # PYDANTIC JOB REQUIREMENT VALIDATION
    # =========================================================

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
    # PROCESS COMPLETED
    # =========================================================

    print("\n==============================")
    print("===== PARSING COMPLETED =====")
    print("==============================")


if __name__ == "__main__":
    main()