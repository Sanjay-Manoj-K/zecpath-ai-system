from pathlib import Path
import csv
import json
import re
import sys
import traceback


# ================================================================
# PROJECT IMPORTS
# ================================================================

from parsers.resume_text_extractor import extract_resume_text
from parsers.resume_parser import parse_resume_text
from parsers.jd_parser import parse_job_description
from parsers.resume_section_classifier import ResumeSectionClassifier
from parsers.skill_extraction_engine import SkillExtractionEngine
from parsers.experience_parser import ExperienceParser


# ================================================================
# PROJECT PATHS
# ================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Support both locations used during development.
POSSIBLE_RESUME_DIRECTORIES = [
    PROJECT_ROOT / "sample_resumes",
    PROJECT_ROOT / "data" / "resumes",
]

OUTPUT_DIRECTORY = (
    PROJECT_ROOT / "validation_results"
)

CSV_OUTPUT = (
    OUTPUT_DIRECTORY / "validation_results.csv"
)

JSON_OUTPUT = (
    OUTPUT_DIRECTORY / "validation_results.json"
)


# ================================================================
# TARGET JOB
# ================================================================

TARGET_JOB_DESCRIPTION = """
Python Developer

Required Skills:
Python
Django
REST APIs
SQL
Git

The candidate should have experience in software development,
backend development, APIs, databases, and programming.

Responsibilities:
- Develop Python applications
- Build and maintain backend services
- Create and consume REST APIs
- Work with SQL databases
- Use Git for version control
"""


TARGET_ROLE = "Python Developer"

TARGET_SKILLS = [
    "Python",
    "Django",
    "REST APIs",
    "SQL",
    "Git",
]


# ================================================================
# GENERAL HELPERS
# ================================================================

def normalize_tokens(text):
    """
    Convert text into normalized lowercase tokens.
    """
    if not text:
        return []

    return re.findall(
        r"[a-zA-Z0-9]+",
        str(text).lower(),
    )


def safe_float(value):
    """
    Safely convert a value to float.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def clean_text(value):
    """
    Convert any value to a clean string.
    """
    if value is None:
        return ""

    if isinstance(value, list):
        return ", ".join(
            str(item)
            for item in value
        )

    return str(value).strip()


def find_resume_directory():
    """
    Find the first existing resume directory.
    """
    for directory in POSSIBLE_RESUME_DIRECTORIES:
        if directory.exists():
            return directory

    return None


def get_resume_files(directory):
    """
    Return supported resume files.
    """
    supported = {
        ".docx",
        ".pdf",
        ".txt",
    }

    return sorted(
        [
            file_path
            for file_path in directory.iterdir()
            if file_path.is_file()
            and file_path.suffix.lower()
            in supported
        ]
    )


# ================================================================
# RESULT TEMPLATE
# ================================================================

def create_result(resume_path):
    """
    Create a standard validation record.
    """
    return {
        "resume": resume_path.name,
        "status": "FAILED",

        "extracted_characters": 0,

        "sections_detected": 0,
        "section_names": "",

        "skills_detected": 0,
        "skills": "",

        "experience_records": 0,
        "total_experience_years": 0.0,

        "experience_gaps": 0,
        "experience_overlaps": 0,

        "experience_relevance": 0.0,
        "top_role": "",
        "top_role_score": 0.0,

        "matched_skills": "",
        "missing_skills": "",

        "error": "",
    }


# ================================================================
# SECTION HANDLING
# ================================================================

def run_section_classification(
    resume_text,
    classifier,
):
    """
    Run Day 8 section classification.

    Handles the existing classifier API.
    """
    try:
        sections = classifier.segment(
            resume_text
        )

        if sections is None:
            return {}

        if isinstance(
            sections,
            dict,
        ):
            return sections

        return {}

    except Exception as error:
        print(
            "Section classification error:",
            error,
        )

        return {}


def get_section_names(sections):
    """
    Extract readable section names.
    """
    if not isinstance(
        sections,
        dict,
    ):
        return []

    return [
        str(key)
        for key in sections.keys()
    ]


# ================================================================
# SKILL EXTRACTION
# ================================================================

def extract_unified_skills(
    resume_text,
    sections,
    skill_engine,
    candidate,
):
    """
    Combine Day 9 skills from:

        1. Section-based extraction
        2. Candidate profile extraction

    Returns canonical skill names where possible.
    """
    extracted = []

    # ------------------------------------------------------------
    # Day 9 section extraction
    # ------------------------------------------------------------

    try:
        section_result = (
            skill_engine.extract_from_sections(
                sections
            )
        )
    except Exception:
        section_result = []

    if isinstance(
        section_result,
        dict,
    ):
        section_skills = (
            section_result.get(
                "skills",
                [],
            )
        )

        if not section_skills:
            # Some implementations may use skill names
            # as dictionary keys.
            section_skills = list(
                section_result.keys()
            )
    elif isinstance(
        section_result,
        list,
    ):
        section_skills = section_result
    else:
        section_skills = []

    # ------------------------------------------------------------
    # CandidateProfile skills
    # ------------------------------------------------------------

    candidate_skills = []

    if isinstance(
        candidate,
        dict,
    ):
        candidate_skills = candidate.get(
            "skills",
            [],
        )

    if not isinstance(
        candidate_skills,
        list,
    ):
        candidate_skills = []

    # ------------------------------------------------------------
    # Normalize both sources
    # ------------------------------------------------------------

    for item in (
        section_skills
        + candidate_skills
    ):
        if isinstance(
            item,
            dict,
        ):
            skill_name = (
                item.get("skill")
                or item.get("name")
                or ""
            )
        else:
            skill_name = str(
                item
            )

        skill_name = skill_name.strip()

        if not skill_name:
            continue

        already_exists = any(
            skill_name.lower()
            == existing.lower()
            for existing in extracted
        )

        if not already_exists:
            extracted.append(
                skill_name
            )

    return extracted


# ================================================================
# EXPERIENCE RELEVANCE
# ================================================================

def skill_present_in_role(
    skill,
    role_text,
):
    """
    Determine whether a target skill is present
    in a role's title/responsibilities.
    """
    skill_tokens = set(
        normalize_tokens(skill)
    )

    role_tokens = set(
        normalize_tokens(role_text)
    )

    if not skill_tokens:
        return False

    return skill_tokens.issubset(
        role_tokens
    )


def calculate_title_similarity(
    role_title,
    target_role,
):
    """
    Calculate simple token-based title similarity.
    """
    candidate_tokens = set(
        normalize_tokens(role_title)
    )

    target_tokens = set(
        normalize_tokens(target_role)
    )

    if not candidate_tokens or not target_tokens:
        return 0.0

    intersection = (
        candidate_tokens
        & target_tokens
    )

    return (
        len(intersection)
        / len(target_tokens)
    )


def calculate_role_relevance(
    experience,
    target_role,
    target_skills,
):
    """
    Calculate generic role relevance.

    Components:
        - Title similarity: 40%
        - Skill overlap: 40%
        - Responsibility similarity: 20%
    """
    title = clean_text(
        experience.get(
            "job_title",
            "",
        )
    )

    responsibilities = experience.get(
        "responsibilities",
        [],
    )

    if not isinstance(
        responsibilities,
        list,
    ):
        responsibilities = []

    responsibility_text = " ".join(
        str(item)
        for item in responsibilities
    )

    combined_text = (
        f"{title} "
        f"{responsibility_text}"
    )

    # ------------------------------------------------------------
    # Title similarity
    # ------------------------------------------------------------

    title_similarity = (
        calculate_title_similarity(
            title,
            target_role,
        )
    )

    # ------------------------------------------------------------
    # Skill overlap
    # ------------------------------------------------------------

    matched_skills = []

    for skill in target_skills:
        if skill_present_in_role(
            skill,
            combined_text,
        ):
            matched_skills.append(
                skill
            )

    skill_overlap = (
        len(matched_skills)
        / len(target_skills)
        if target_skills
        else 0.0
    )

    # ------------------------------------------------------------
    # Responsibility similarity
    # ------------------------------------------------------------

    responsibility_tokens = set(
        normalize_tokens(
            responsibility_text
        )
    )

    target_tokens = set(
        normalize_tokens(
            target_role
            + " "
            + " ".join(
                target_skills
            )
        )
    )

    if (
        responsibility_tokens
        and target_tokens
    ):
        responsibility_similarity = (
            len(
                responsibility_tokens
                & target_tokens
            )
            / len(target_tokens)
        )
    else:
        responsibility_similarity = 0.0

    # ------------------------------------------------------------
    # Final relevance
    # ------------------------------------------------------------

    score = (
        title_similarity * 0.40
        + skill_overlap * 0.40
        + responsibility_similarity * 0.20
    )

    return {
        "role": title,
        "company": clean_text(
            experience.get(
                "company",
                "",
            )
        ),
        "title_similarity": round(
            title_similarity * 100,
            2,
        ),
        "skill_overlap": round(
            skill_overlap * 100,
            2,
        ),
        "responsibility_similarity": round(
            responsibility_similarity * 100,
            2,
        ),
        "score": round(
            score * 100,
            2,
        ),
        "matched_skills": matched_skills,
    }


def calculate_experience_relevance(
    experiences,
):
    """
    Score all parsed roles.
    """
    if not experiences:
        return 0.0, []

    ranked = []

    for experience in experiences:
        ranked.append(
            calculate_role_relevance(
                experience=experience,
                target_role=TARGET_ROLE,
                target_skills=TARGET_SKILLS,
            )
        )

    ranked.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    overall = (
        sum(
            item["score"]
            for item in ranked
        )
        / len(ranked)
        if ranked
        else 0.0
    )

    return (
        round(
            overall,
            2,
        ),
        ranked,
    )


# ================================================================
# RESUME VALIDATION
# ================================================================

def validate_resume(
    resume_path,
    classifier,
    skill_engine,
    experience_parser,
):
    """
    Run one resume through the available Day 5-Day 10 pipeline.
    """
    result = create_result(
        resume_path
    )

    print(
        "\n"
        + "=" * 80
    )

    print(
        f"VALIDATING: {resume_path.name}"
    )

    print(
        "=" * 80
    )

    try:
        # --------------------------------------------------------
        # DAY 5 - TEXT EXTRACTION
        # --------------------------------------------------------

        resume_text = extract_resume_text(
            resume_path
        )

        if not resume_text:
            raise ValueError(
                "Text extraction returned empty content."
            )

        result[
            "extracted_characters"
        ] = len(
            resume_text
        )

        print(
            f"Extracted characters: "
            f"{len(resume_text)}"
        )

        # --------------------------------------------------------
        # DAY 6 - RESUME PARSING
        # --------------------------------------------------------

        candidate = parse_resume_text(
            resume_text
        )

        if not isinstance(
            candidate,
            dict,
        ):
            candidate = {}

        # --------------------------------------------------------
        # DAY 6 - JD PARSING
        # --------------------------------------------------------

        job = parse_job_description(
            TARGET_JOB_DESCRIPTION
        )

        if not isinstance(
            job,
            dict,
        ):
            job = {}

        # --------------------------------------------------------
        # DAY 8 - SECTION CLASSIFICATION
        # --------------------------------------------------------

        sections = run_section_classification(
            resume_text,
            classifier,
        )

        section_names = (
            get_section_names(
                sections
            )
        )

        result[
            "sections_detected"
        ] = len(
            section_names
        )

        result[
            "section_names"
        ] = "; ".join(
            section_names
        )

        print(
            f"Sections detected: "
            f"{len(section_names)}"
        )

        # --------------------------------------------------------
        # DAY 9 - SKILL EXTRACTION
        # --------------------------------------------------------

        unified_skills = (
            extract_unified_skills(
                resume_text=resume_text,
                sections=sections,
                skill_engine=skill_engine,
                candidate=candidate,
            )
        )

        result[
            "skills_detected"
        ] = len(
            unified_skills
        )

        result[
            "skills"
        ] = "; ".join(
            unified_skills
        )

        print(
            f"Skills detected: "
            f"{len(unified_skills)}"
        )

        # --------------------------------------------------------
        # TARGET SKILL MATCHING
        # --------------------------------------------------------

        candidate_skill_lower = {
            skill.lower()
            for skill in unified_skills
        }

        matched_skills = [
            skill
            for skill in TARGET_SKILLS
            if skill.lower()
            in candidate_skill_lower
        ]

        missing_skills = [
            skill
            for skill in TARGET_SKILLS
            if skill.lower()
            not in candidate_skill_lower
        ]

        result[
            "matched_skills"
        ] = "; ".join(
            matched_skills
        )

        result[
            "missing_skills"
        ] = "; ".join(
            missing_skills
        )

        # --------------------------------------------------------
        # DAY 10 - EXPERIENCE PARSING
        # --------------------------------------------------------

        experience_result = (
            experience_parser.parse_experience(
                resume_text
            )
        )

        if not isinstance(
            experience_result,
            dict,
        ):
            raise ValueError(
                "ExperienceParser returned an unexpected format."
            )

        experiences = (
            experience_result.get(
                "experiences",
                [],
            )
        )

        result[
            "experience_records"
        ] = len(
            experiences
        )

        result[
            "total_experience_years"
        ] = safe_float(
            experience_result.get(
                "total_experience_years",
                0,
            )
        )

        result[
            "experience_gaps"
        ] = len(
            experience_result.get(
                "gaps",
                [],
            )
        )

        result[
            "experience_overlaps"
        ] = len(
            experience_result.get(
                "overlaps",
                [],
            )
        )

        print(
            f"Experience records: "
            f"{len(experiences)}"
        )

        print(
            f"Total experience: "
            f"{result['total_experience_years']:.2f} years"
        )

        print(
            f"Gaps: "
            f"{result['experience_gaps']}"
        )

        print(
            f"Overlaps: "
            f"{result['experience_overlaps']}"
        )

        # --------------------------------------------------------
        # DAY 10 - EXPERIENCE RELEVANCE
        # --------------------------------------------------------

        relevance, ranked_roles = (
            calculate_experience_relevance(
                experiences
            )
        )

        result[
            "experience_relevance"
        ] = relevance

        if ranked_roles:
            result[
                "top_role"
            ] = ranked_roles[0].get(
                "role",
                "",
            )

            result[
                "top_role_score"
            ] = safe_float(
                ranked_roles[0].get(
                    "score",
                    0,
                )
            )

        print(
            f"Experience relevance: "
            f"{relevance:.2f}%"
        )

        if ranked_roles:
            print(
                f"Top role: "
                f"{result['top_role']} "
                f"({result['top_role_score']:.2f}%)"
            )

        # --------------------------------------------------------
        # PASS
        # --------------------------------------------------------

        result[
            "status"
        ] = "PASSED"

        print(
            "Status: PASSED"
        )

        return result

    except Exception as error:
        result[
            "error"
        ] = (
            f"{type(error).__name__}: "
            f"{error}"
        )

        print(
            f"Status: FAILED"
        )

        print(
            f"Error: "
            f"{result['error']}"
        )

        traceback.print_exc()

        return result


# ================================================================
# SAVE RESULTS
# ================================================================

def save_results(
    results,
):
    """
    Save CSV and JSON validation results.
    """
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------------
    # JSON
    # ------------------------------------------------------------

    with open(
        JSON_OUTPUT,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=4,
            default=str,
        )

    # ------------------------------------------------------------
    # CSV
    # ------------------------------------------------------------

    if results:
        fieldnames = list(
            results[0].keys()
        )

        with open(
            CSV_OUTPUT,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            writer.writerows(
                results
            )


# ================================================================
# SUMMARY
# ================================================================

def print_summary(
    results,
):
    """
    Print compact multi-resume validation summary.
    """
    print(
        "\n"
        + "=" * 120
    )

    print(
        "===== ZECPATH AI SYSTEM - MULTI-RESUME VALIDATION ====="
    )

    print(
        "=" * 120
    )

    print(
        f"{'Resume':35}"
        f"{'Status':10}"
        f"{'Chars':>9}"
        f"{'Sections':>10}"
        f"{'Skills':>8}"
        f"{'Exp':>8}"
        f"{'ATS Rel.':>10}"
    )

    print(
        "-" * 120
    )

    for result in results:
        name = result[
            "resume"
        ]

        if len(name) > 33:
            name = (
                name[:30]
                + "..."
            )

        print(
            f"{name:35}"
            f"{result['status']:10}"
            f"{result['extracted_characters']:>9}"
            f"{result['sections_detected']:>10}"
            f"{result['skills_detected']:>8}"
            f"{result['experience_records']:>8}"
            f"{result['experience_relevance']:>10.2f}"
        )

    passed = sum(
        1
        for result in results
        if result[
            "status"
        ] == "PASSED"
    )

    failed = (
        len(results)
        - passed
    )

    print(
        "\n"
        + "=" * 120
    )

    print(
        f"Total resumes : {len(results)}"
    )

    print(
        f"Passed        : {passed}"
    )

    print(
        f"Failed        : {failed}"
    )

    # ------------------------------------------------------------
    # Failed files
    # ------------------------------------------------------------

    failed_results = [
        result
        for result in results
        if result[
            "status"
        ] != "PASSED"
    ]

    if failed_results:
        print(
            "\n===== FAILED RESUMES ====="
        )

        for result in failed_results:
            print(
                f"- {result['resume']}: "
                f"{result['error']}"
            )

    # ------------------------------------------------------------
    # Output files
    # ------------------------------------------------------------

    print(
        "\nCSV:"
    )

    print(
        CSV_OUTPUT
    )

    print(
        "\nJSON:"
    )

    print(
        JSON_OUTPUT
    )


# ================================================================
# MAIN
# ================================================================

def main():
    """
    Main multi-resume validation runner.
    """
    print(
        "\n"
        + "=" * 120
    )

    print(
        "===== ZECPATH AI SYSTEM - DAY 5 TO DAY 10 VALIDATION ====="
    )

    print(
        "=" * 120
    )

    print(
        f"\nProject root:"
    )

    print(
        PROJECT_ROOT
    )

    # ------------------------------------------------------------
    # Find resume directory
    # ------------------------------------------------------------

    resume_directory = (
        find_resume_directory()
    )

    if resume_directory is None:
        print(
            "\nERROR: Could not find a resume directory."
        )

        print(
            "\nExpected one of:"
        )

        for directory in (
            POSSIBLE_RESUME_DIRECTORIES
        ):
            print(
                f"  {directory}"
            )

        sys.exit(1)

    print(
        f"\nResume directory:"
    )

    print(
        resume_directory
    )

    # ------------------------------------------------------------
    # Find resumes
    # ------------------------------------------------------------

    resume_files = get_resume_files(
        resume_directory
    )

    if not resume_files:
        print(
            "\nERROR: No .docx, .pdf, or .txt resumes found."
        )

        sys.exit(1)

    print(
        f"\nFound "
        f"{len(resume_files)} "
        f"resume(s)."
    )

    # ------------------------------------------------------------
    # Initialize shared engines
    # ------------------------------------------------------------

    classifier = (
        ResumeSectionClassifier()
    )

    skill_engine = (
        SkillExtractionEngine()
    )

    experience_parser = (
        ExperienceParser()
    )

    # ------------------------------------------------------------
    # Validate
    # ------------------------------------------------------------

    results = []

    for resume_path in resume_files:

        result = validate_resume(
            resume_path=resume_path,
            classifier=classifier,
            skill_engine=skill_engine,
            experience_parser=experience_parser,
        )

        results.append(
            result
        )

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    save_results(
        results
    )

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    print_summary(
        results
    )


if __name__ == "__main__":
    main()