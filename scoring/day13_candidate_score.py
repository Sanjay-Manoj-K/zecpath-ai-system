"""
Zecpath AI System
Day 13 - Candidate ATS Score Generator

Integrates:

Day 9  -> Skill Extraction
Day 10 -> Experience Relevance
Day 11 -> Education & Certification
Day 12 -> Semantic Matching
Day 13 -> Weighted ATS Scoring

Usage:

python -m scoring.day13_candidate_score ^
    data/resumes/ai-developer-resume.docx ^
    data/job_descriptions/python_developer.txt
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from parsers.resume_text_extractor import extract_resume_text
from parsers.resume_parser import parse_resume_text
from parsers.jd_parser import (
    read_job_description,
    parse_job_description,
)
from parsers.skill_extraction_engine import (
    SkillExtractionEngine,
)
from parsers.experience_parser import (
    ExperienceParser,
)
from parsers.education_certification_parser import (
    EducationCertificationParser,
)
from scoring.experience_relevance import (
    ExperienceRelevanceScorer,
)
from scoring.semantic_matching import (
    SemanticMatchingEngine,
)
from scoring.ats_scoring_engine import (
    ATSScoringEngine,
)
from ats_engine.ats_engine.job_requirement import (
    JobRequirement,
)


# ============================================================================
# BASIC TEXT NORMALIZATION
# ============================================================================

def normalize_text(value: str) -> str:
    """
    Normalize text for matching and heading detection.
    """

    if not value:
        return ""

    value = value.lower()

    value = re.sub(
        r"[^a-z0-9+#.\s]",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


# ============================================================================
# SKILL CANONICALIZATION
# ============================================================================

def canonicalize_skill(skill: str) -> str:
    """
    Convert common skill variants into one canonical representation.

    Examples:

        REST API
        REST APIs
        RESTful API

    become:

        rest apis

    Also maps:

        AI
        Artificial Intelligence

    to:

        artificial intelligence
    """

    normalized = normalize_text(
        skill
    )

    if not normalized:
        return ""

    aliases = {
        "rest api": "rest apis",
        "rest apis": "rest apis",
        "restful api": "rest apis",
        "restful apis": "rest apis",

        "version control": "git",
        "git version control": "git",
        "git/version control": "git",

        "ai": "artificial intelligence",
        "artificial intelligence":
            "artificial intelligence",
    }

    return aliases.get(
        normalized,
        normalized,
    )


# ============================================================================
# SKILL MATCH
# ============================================================================

def calculate_skill_match(
    candidate_skills: list[str],
    required_skills: list[str],
) -> float | None:
    """
    Calculate:

        matched required skills
        -----------------------
        total unique required skills

    Returns None when the JD contains no usable skill requirement.
    """

    if not required_skills:
        return None

    candidate_set = {
        canonicalize_skill(skill)
        for skill in candidate_skills
        if skill
    }

    required_set = {
        canonicalize_skill(skill)
        for skill in required_skills
        if skill
    }

    candidate_set.discard("")
    required_set.discard("")

    if not required_set:
        return None

    matched = (
        candidate_set
        & required_set
    )

    score = (
        len(matched)
        / len(required_set)
    )

    return round(
        score,
        4,
    )


# ============================================================================
# WORK EXPERIENCE SECTION EXTRACTION
# ============================================================================

def extract_work_experience_text(
    resume_text: str,
) -> str:
    """
    Extract the employment section from the raw resume.

    IMPORTANT:
    The existing resume parser flattens its experience section into
    one string. Day 10's ExperienceParser needs the original line
    structure, so this function extracts the section directly from
    raw resume text and preserves line breaks.
    """

    if not resume_text:
        return ""

    lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]

    if not lines:
        return ""

    start_headings = {
        "work history",
        "work experience",
        "professional experience",
        "relevant experience",
        "experience",
        "employment",
        "employment history",
        "professional history",
    }

    stop_headings = {
        "skills",
        "technical skills",
        "key skills",
        "additional skills",
        "core skills",

        "education",
        "academic background",
        "academic qualifications",
        "educational background",
        "academic history",

        "certifications",
        "certification",
        "certificates",
        "professional certifications",

        "projects",
        "academic projects",
        "relevant projects",

        "languages",
        "interests",
        "hobbies & interests",
        "references",

        "awards",
        "awards & recognition",
        "achievements",

        "additional information",
        "memberships",
    }

    start_index = -1

    for index, line in enumerate(lines):

        normalized = normalize_text(
            line
        )

        if normalized in start_headings:
            start_index = index
            break

    if start_index == -1:
        return ""

    end_index = len(lines)

    for index in range(
        start_index + 1,
        len(lines),
    ):

        normalized = normalize_text(
            lines[index]
        )

        if normalized in stop_headings:
            end_index = index
            break

    section_lines = lines[
        start_index + 1:
        end_index
    ]

    return "\n".join(
        section_lines
    ).strip()


# ============================================================================
# EXPERIENCE DATE DETECTION
# ============================================================================

MONTH_PATTERN = (
    r"(?:"
    r"January|February|March|April|May|June|July|August|"
    r"September|October|November|December|"
    r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
    r")"
)


def looks_like_experience_date(
    line: str,
) -> bool:
    """
    Recognize common employment date formats.
    """

    if not line:
        return False

    patterns = [

        # January 2024 to August 2025
        rf"(?i)\b{MONTH_PATTERN}\s+\d{{4}}"
        rf"\s*(?:to|-|–|—)\s*"
        rf"{MONTH_PATTERN}\s+\d{{4}}\b",

        # 01/2024 - 08/2025
        r"(?i)\b\d{1,2}/\d{4}"
        r"\s*(?:to|-|–|—)\s*"
        r"\d{1,2}/\d{4}\b",

        # 2024 - 2025
        r"(?i)\b\d{4}"
        r"\s*(?:to|-|–|—)\s*"
        r"\d{4}\b",
    ]

    for pattern in patterns:

        if re.search(
            pattern,
            line,
        ):
            return True

    return False


# ============================================================================
# MONTH CONVERSION
# ============================================================================

MONTH_LOOKUP = {
    "january": 1,
    "jan": 1,

    "february": 2,
    "feb": 2,

    "march": 3,
    "mar": 3,

    "april": 4,
    "apr": 4,

    "may": 5,

    "june": 6,
    "jun": 6,

    "july": 7,
    "jul": 7,

    "august": 8,
    "aug": 8,

    "september": 9,
    "sep": 9,
    "sept": 9,

    "october": 10,
    "oct": 10,

    "november": 11,
    "nov": 11,

    "december": 12,
    "dec": 12,
}


# ============================================================================
# DATE RANGE MONTH CALCULATION
# ============================================================================

def calculate_months_from_date_range(
    date_text: str,
) -> int:
    """
    Calculate the number of inclusive months represented by a date range.

    Example:

        January 2024 to August 2025

    = 20 months
    """

    if not date_text:
        return 0

    month_year_matches = re.findall(
        r"(?i)\b("
        + "|".join(
            MONTH_LOOKUP.keys()
        )
        + r")\s+(\d{4})\b",
        date_text,
    )

    if len(month_year_matches) >= 2:

        start_month_name = (
            month_year_matches[0][0]
        )

        start_year = int(
            month_year_matches[0][1]
        )

        end_month_name = (
            month_year_matches[1][0]
        )

        end_year = int(
            month_year_matches[1][1]
        )

        start_month = MONTH_LOOKUP[
            start_month_name.lower()
        ]

        end_month = MONTH_LOOKUP[
            end_month_name.lower()
        ]

        months = (
            (end_year - start_year) * 12
            + (end_month - start_month)
            + 1
        )

        return max(
            months,
            0,
        )

    # 01/2024 - 08/2025
    numeric_matches = re.findall(
        r"\b(\d{1,2})/(\d{4})\b",
        date_text,
    )

    if len(numeric_matches) >= 2:

        start_month = int(
            numeric_matches[0][0]
        )

        start_year = int(
            numeric_matches[0][1]
        )

        end_month = int(
            numeric_matches[1][0]
        )

        end_year = int(
            numeric_matches[1][1]
        )

        months = (
            (end_year - start_year) * 12
            + (end_month - start_month)
            + 1
        )

        return max(
            months,
            0,
        )

    # 2024 - 2025
    year_matches = re.findall(
        r"\b(19\d{2}|20\d{2})\b",
        date_text,
    )

    if len(year_matches) >= 2:

        start_year = int(
            year_matches[0]
        )

        end_year = int(
            year_matches[1]
        )

        months = (
            (end_year - start_year) * 12
            + 1
        )

        return max(
            months,
            0,
        )

    return 0


# ============================================================================
# FALLBACK EXPERIENCE PARSER
# ============================================================================

def parse_experience_fallback(
    work_experience_text: str,
) -> dict:
    """
    Conservative fallback parser for employment sections.

    Expected structure:

        Job Title
        Date Range
        Company
        Responsibility
        Responsibility

        Next Job Title
        Date Range
        Company
        Responsibility

    This parser does not invent missing information.
    """

    lines = [
        line.strip()
        for line in work_experience_text.splitlines()
        if line.strip()
    ]

    if not lines:
        return {
            "experiences": [],
            "total_experience_years": 0.0,
            "gaps": [],
            "overlaps": [],
        }

    date_indexes = []

    for index, line in enumerate(lines):

        if looks_like_experience_date(
            line
        ):
            date_indexes.append(
                index
            )

    experiences = []

    for position, date_index in enumerate(
        date_indexes
    ):

        # Date should normally have a title immediately before it.
        if date_index <= 0:
            continue

        job_title = lines[
            date_index - 1
        ].strip()

        if not job_title:
            continue

        # Company normally follows the date.
        company = ""

        if date_index + 1 < len(lines):
            company = lines[
                date_index + 1
            ].strip()

        # Everything after company belongs to this job until
        # the next employment date.
        if position + 1 < len(date_indexes):

            next_date_index = date_indexes[
                position + 1
            ]

        else:

            next_date_index = len(lines)

        responsibilities = []

        responsibility_start = (
            date_index + 2
        )

        for index in range(
            responsibility_start,
            next_date_index,
        ):

            value = lines[index].strip()

            if not value:
                continue

            # The line immediately before the next date is
            # normally the next job title.
            if (
                position + 1 < len(date_indexes)
                and index == next_date_index - 1
            ):
                continue

            value = value.lstrip(
                "-•● "
            ).strip()

            if value:
                responsibilities.append(
                    value
                )

        raw_end = next_date_index

        raw_text = "\n".join(
            lines[
                date_index - 1:
                raw_end
            ]
        )

        experiences.append(
            {
                "job_title":
                    job_title,

                "company":
                    company,

                "responsibilities":
                    responsibilities,

                "start_date":
                    lines[date_index],

                "end_date":
                    "",

                "raw_text":
                    raw_text,
            }
        )

    # ------------------------------------------------------------------------
    # Total experience
    # ------------------------------------------------------------------------

    total_months = 0

    for experience in experiences:

        total_months += (
            calculate_months_from_date_range(
                experience.get(
                    "start_date",
                    "",
                )
            )
        )

    total_experience_years = round(
        total_months / 12,
        2,
    )

    return {
        "experiences":
            experiences,

        "total_experience_years":
            total_experience_years,

        "gaps":
            [],

        "overlaps":
            [],
    }


# ============================================================================
# EXPERIENCE RECORD NORMALIZATION
# ============================================================================

def normalize_experience_records(
    experiences: list,
) -> list[dict]:
    """
    Normalize experience objects into dictionaries.
    """

    records = []

    for experience in experiences:

        if isinstance(
            experience,
            dict,
        ):

            records.append(
                experience
            )

            continue

        record = {}

        for field_name in (
            "job_title",
            "company",
            "responsibilities",
            "start_date",
            "end_date",
            "raw_text",
        ):

            if hasattr(
                experience,
                field_name,
            ):

                record[field_name] = getattr(
                    experience,
                    field_name,
                )

        if record:
            records.append(
                record
            )

    return records


# ============================================================================
# EXPERIENCE RELEVANCE
# ============================================================================

def calculate_experience_relevance(
    experience_parser: ExperienceParser,
    experience_scorer: ExperienceRelevanceScorer,
    work_experience_text: str,
    job_requirement: JobRequirement,
) -> tuple[float | None, dict]:
    """
    Parse candidate experience and calculate Day 10 relevance.

    Flow:

        Raw work section
              |
              v
        Day 10 ExperienceParser
              |
              | if no records
              v
        Conservative fallback parser
              |
              v
        ExperienceRelevanceScorer
    """

    if not work_experience_text.strip():

        return (
            None,
            {
                "experiences": [],
                "overall_relevance_score": None,
                "overall_relevance_percent": None,
                "total_experience_years": 0.0,
                "gaps": [],
                "overlaps": [],
            },
        )

    # ------------------------------------------------------------------------
    # First attempt: official Day 10 parser
    # ------------------------------------------------------------------------

    parsed_experience = None

    try:

        parsed_experience = (
            experience_parser.parse_experience(
                work_experience_text
            )
        )

    except Exception as exc:

        print(
            "\nDay 10 parser warning:"
        )

        print(
            f"  {exc}"
        )

    raw_experiences = []

    if isinstance(
        parsed_experience,
        dict,
    ):

        raw_experiences = (
            parsed_experience.get(
                "experiences",
                [],
            )
            or []
        )

    # ------------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------------

    if not raw_experiences:

        print(
            "\nDay 10 parser returned "
            "no structured experience records."
        )

        print(
            "Using conservative fallback "
            "experience parser..."
        )

        parsed_experience = (
            parse_experience_fallback(
                work_experience_text
            )
        )

        raw_experiences = (
            parsed_experience.get(
                "experiences",
                [],
            )
        )

    experiences = (
        normalize_experience_records(
            raw_experiences
        )
    )

    if not experiences:

        return (
            None,
            {
                "experiences": [],
                "overall_relevance_score": None,
                "overall_relevance_percent": None,
                "total_experience_years":
                    parsed_experience.get(
                        "total_experience_years",
                        0.0,
                    ),
                "gaps":
                    parsed_experience.get(
                        "gaps",
                        [],
                    ),
                "overlaps":
                    parsed_experience.get(
                        "overlaps",
                        [],
                    ),
            },
        )

    # ------------------------------------------------------------------------
    # Day 10 scoring
    # ------------------------------------------------------------------------

    experience_result = (
        experience_scorer.score_experiences(
            experiences,
            job_requirement,
        )
    )

    # ------------------------------------------------------------------------
    # Preserve timeline information
    # ------------------------------------------------------------------------

    if isinstance(
        parsed_experience,
        dict,
    ):

        experience_result[
            "total_experience_years"
        ] = parsed_experience.get(
            "total_experience_years",
            0.0,
        )

        experience_result[
            "gaps"
        ] = parsed_experience.get(
            "gaps",
            [],
        )

        experience_result[
            "overlaps"
        ] = parsed_experience.get(
            "overlaps",
            [],
        )

    overall_score = (
        experience_result.get(
            "overall_relevance_score"
        )
    )

    if overall_score is None:

        return (
            None,
            experience_result,
        )

    return (
        float(
            overall_score
        ),
        experience_result,
    )


# ============================================================================
# EDUCATION DEGREE DETECTION
# ============================================================================

def detect_required_degree_level(
    education_requirement: str,
) -> str | None:
    """
    Detect the minimum degree level requested by the JD.
    """

    if not education_requirement:
        return None

    value = normalize_text(
        education_requirement
    )

    # Highest level first.

    doctorate_patterns = [
        "phd",
        "ph d",
        "doctorate",
        "doctor of philosophy",
        "doctor of",
    ]

    masters_patterns = [
        "master",
        "masters",
        "mca",
        "mba",
        "master of science",
        "master of arts",
        "master of computer applications",
        "master of business administration",
    ]

    bachelors_patterns = [
        "bachelor",
        "bachelors",
        "bachelor of science",
        "bachelor of arts",
        "bachelor of computer applications",
        "bachelor of business administration",
        "bca",
        "bba",
        "bsc",
        "b sc",
        "ba",
    ]

    for pattern in doctorate_patterns:

        if pattern in value:
            return "doctorate"

    for pattern in masters_patterns:

        if pattern in value:
            return "masters"

    for pattern in bachelors_patterns:

        if pattern in value:
            return "bachelors"

    if "associate" in value:
        return "associate"

    if "diploma" in value:
        return "diploma"

    return None


# ============================================================================
# DEGREE RANKING
# ============================================================================

DEGREE_LEVEL_RANK = {
    "none": 0,
    "certificate": 0,
    "diploma": 1,
    "associate": 2,
    "bachelors": 3,
    "masters": 4,
    "doctorate": 5,
}


# ============================================================================
# EDUCATION FIELD DETECTION
# ============================================================================

def detect_required_education_fields(
    education_requirement: str,
) -> list[str]:
    """
    Detect recognizable education fields from the JD.
    """

    if not education_requirement:
        return []

    value = normalize_text(
        education_requirement
    )

    field_aliases = {
        "computer science": [
            "computer science",
        ],

        "computer applications": [
            "computer applications",
            "computer application",
        ],

        "information technology": [
            "information technology",
        ],

        "information systems": [
            "information systems",
        ],

        "data science": [
            "data science",
        ],

        "artificial intelligence": [
            "artificial intelligence",
            "artificial intelligence",
        ],

        "machine learning": [
            "machine learning",
        ],

        "software engineering": [
            "software engineering",
        ],

        "business administration": [
            "business administration",
        ],

        "finance": [
            "finance",
        ],

        "accounting": [
            "accounting",
        ],

        "marketing": [
            "marketing",
        ],

        "mechanical engineering": [
            "mechanical engineering",
        ],

        "electrical engineering": [
            "electrical engineering",
        ],

        "electronics": [
            "electronics",
        ],

        "civil engineering": [
            "civil engineering",
        ],

        "physics": [
            "physics",
        ],

        "mathematics": [
            "mathematics",
        ],

        "statistics": [
            "statistics",
        ],
    }

    detected = []

    for canonical, aliases in (
        field_aliases.items()
    ):

        for alias in aliases:

            if alias in value:

                detected.append(
                    canonical
                )

                break

    return list(
        dict.fromkeys(
            detected
        )
    )


# ============================================================================
# EDUCATION FIELD NORMALIZATION
# ============================================================================

def normalize_education_field(
    field: str,
) -> str:
    """
    Normalize candidate education fields.
    """

    if not field:
        return ""

    value = normalize_text(
        field
    )

    aliases = {
        "computer science":
            "computer science",

        "computer applications":
            "computer applications",

        "computer application":
            "computer applications",

        "information technology":
            "information technology",

        "information systems":
            "information systems",

        "data science":
            "data science",

        "artificial intelligence":
            "artificial intelligence",

        "machine learning":
            "machine learning",

        "software engineering":
            "software engineering",

        "business administration":
            "business administration",

        "finance":
            "finance",

        "accounting":
            "accounting",

        "marketing":
            "marketing",
    }

    return aliases.get(
        value,
        value,
    )


# ============================================================================
# EDUCATION ALIGNMENT
# ============================================================================

def calculate_education_alignment(
    academic_profile,
    education_requirement: str,
) -> float | None:
    """
    Calculate transparent education alignment.

    1.0 = degree + field aligned
    0.5 = degree OR field aligned
    0.0 = explicit requirement exists but no alignment
    None = insufficient evidence
    """

    if academic_profile is None:
        return None

    if not education_requirement:
        return None

    candidate_education = getattr(
        academic_profile,
        "education",
        [],
    )

    candidate_level = getattr(
        academic_profile,
        "highest_degree_level",
        None,
    )

    candidate_fields = getattr(
        academic_profile,
        "fields_of_study",
        [],
    ) or []

    if not candidate_education and not candidate_level:
        return None

    required_level = (
        detect_required_degree_level(
            education_requirement
        )
    )

    required_fields = (
        detect_required_education_fields(
            education_requirement
        )
    )

    degree_match = False

    field_match = False

    # ------------------------------------------------------------------------
    # Degree
    # ------------------------------------------------------------------------

    if required_level and candidate_level:

        required_rank = DEGREE_LEVEL_RANK.get(
            required_level,
            0,
        )

        candidate_rank = DEGREE_LEVEL_RANK.get(
            candidate_level,
            0,
        )

        candidate_degree_is_sufficient = (
            candidate_rank
            >= required_rank
        )

        degree_match = (
            candidate_degree_is_sufficient
        )

    # ------------------------------------------------------------------------
    # Field
    # ------------------------------------------------------------------------

    candidate_fields_normalized = {
        normalize_education_field(
            field
        )
        for field in candidate_fields
        if field
    }

    if required_fields:

        for field in required_fields:

            if field in candidate_fields_normalized:

                field_match = True
                break

    # ------------------------------------------------------------------------
    # Final result
    # ------------------------------------------------------------------------

    if degree_match and field_match:
        return 1.0

    if degree_match:
        return 0.5

    if field_match:
        return 0.5

    if required_level or required_fields:
        return 0.0

    return None


# ============================================================================
# PRINT HELPERS
# ============================================================================

def print_separator(
    title: str,
) -> None:
    """
    Print a standardized console section.
    """

    print(
        "\n" + "-" * 70
    )

    print(
        title
    )

    print(
        "-" * 70
    )


def format_score(
    score,
) -> str:
    """
    Format score as decimal + percentage.
    """

    if score is None:
        return "Unavailable"

    return (
        f"{score:.4f} "
        f"({score * 100:.2f}%)"
    )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """
    Execute the complete Day 13 candidate scoring pipeline.
    """

    # ------------------------------------------------------------------------
    # Arguments
    # ------------------------------------------------------------------------

    if len(sys.argv) != 3:

        print(
            "\nUsage:"
        )

        print(
            "python -m scoring.day13_candidate_score "
            "<resume_path> <jd_path>"
        )

        sys.exit(1)

    resume_path = Path(
        sys.argv[1]
    )

    jd_path = Path(
        sys.argv[2]
    )

    if not resume_path.exists():

        print(
            f"\nERROR: Resume file not found: "
            f"{resume_path}"
        )

        sys.exit(1)

    if not jd_path.exists():

        print(
            f"\nERROR: Job description file not found: "
            f"{jd_path}"
        )

        sys.exit(1)

    print(
        "\n" + "=" * 70
    )

    print(
        "ZECPATH AI SYSTEM - DAY 13 CANDIDATE SCORING"
    )

    print(
        "=" * 70
    )

    # ------------------------------------------------------------------------
    # Resume extraction
    # ------------------------------------------------------------------------

    print(
        f"\nResume file: "
        f"{resume_path}"
    )

    resume_text = extract_resume_text(
        str(resume_path)
    )

    if not resume_text.strip():

        print(
            "\nERROR: Resume text is empty."
        )

        sys.exit(1)

    # ------------------------------------------------------------------------
    # Resume parsing
    # ------------------------------------------------------------------------

    candidate = parse_resume_text(
        resume_text
    )

    # ------------------------------------------------------------------------
    # JD parsing
    # ------------------------------------------------------------------------

    print(
        f"\nJob description file: "
        f"{jd_path}"
    )

    jd_text = read_job_description(
        str(jd_path)
    )

    job = parse_job_description(
        jd_text
    )

    # ------------------------------------------------------------------------
    # Pydantic JD validation
    # ------------------------------------------------------------------------

    try:

        job_requirement = JobRequirement(
            **job
        )

    except Exception as exc:

        print(
            "\nERROR: JobRequirement validation failed."
        )

        print(
            f"Details: {exc}"
        )

        sys.exit(1)

    # ------------------------------------------------------------------------
    # Basic information
    # ------------------------------------------------------------------------

    print(
        "\nCandidate:"
    )

    print(
        f"  Name: "
        f"{candidate.get('name', '')}"
    )

    print(
        "\nJob:"
    )

    print(
        f"  Role: "
        f"{job_requirement.role}"
    )

    # ------------------------------------------------------------------------
    # DAY 9 - SKILLS
    # ------------------------------------------------------------------------

    print_separator(
        "DAY 9 - SKILL EXTRACTION"
    )

    skill_engine = (
        SkillExtractionEngine()
    )

    skill_result = (
        skill_engine.extract_skills(
            resume_text,
            source_section="resume",
        )
    )

    candidate_skills = []

    for skill in skill_result.get(
        "skills",
        [],
    ):

        canonical = skill.get(
            "canonical",
            "",
        )

        if canonical:
            candidate_skills.append(
                canonical
            )

    candidate_skills = list(
        dict.fromkeys(
            candidate_skills
        )
    )

    required_skills = list(
        job_requirement.required_skills
    )

    print(
        "\nCandidate Skills:"
    )

    if candidate_skills:

        for skill in candidate_skills:

            print(
                f"  - {skill}"
            )

    else:

        print(
            "  None detected"
        )

    print(
        "\nJD Required Skills:"
    )

    if required_skills:

        for skill in required_skills:

            print(
                f"  - {skill}"
            )

    else:

        print(
            "  None specified"
        )

    skill_match = (
        calculate_skill_match(
            candidate_skills,
            required_skills,
        )
    )

    print(
        f"\nSkill Match: "
        f"{format_score(skill_match)}"
    )

    # ------------------------------------------------------------------------
    # DAY 10 - EXPERIENCE
    # ------------------------------------------------------------------------

    print_separator(
        "DAY 10 - EXPERIENCE RELEVANCE"
    )

    work_experience_text = (
        extract_work_experience_text(
            resume_text
        )
    )

    print(
        f"\nWork Experience Text Length : "
        f"{len(work_experience_text)}"
    )

    if work_experience_text:

        print(
            "Work Experience Section     : FOUND"
        )

    else:

        print(
            "Work Experience Section     : NOT FOUND"
        )

    experience_parser = (
        ExperienceParser()
    )

    experience_scorer = (
        ExperienceRelevanceScorer(
            skill_engine=skill_engine
        )
    )

    (
        experience_relevance,
        experience_result,
    ) = calculate_experience_relevance(
        experience_parser,
        experience_scorer,
        work_experience_text,
        job_requirement,
    )

    experience_records = (
        experience_result.get(
            "experiences",
            [],
        )
    )

    total_experience_years = (
        experience_result.get(
            "total_experience_years",
            0.0,
        )
    )

    print(
        f"\nExperience Records : "
        f"{len(experience_records)}"
    )

    print(
        f"Total Experience   : "
        f"{total_experience_years} years"
    )

    print(
        f"Experience Relevance: "
        f"{format_score(experience_relevance)}"
    )

    if experience_records:

        print(
            "\nExperience Details:"
        )

        for index, experience in enumerate(
            experience_records,
            start=1,
        ):

            print(
                f"\n  Experience {index}"
            )

            print(
                f"    Role      : "
                f"{experience.get('job_title', '')}"
            )

            print(
                f"    Company   : "
                f"{experience.get('company', '')}"
            )

            print(
                f"    Start     : "
                f"{experience.get('start_date', '')}"
            )

            relevance = experience.get(
                "relevance_percent"
            )

            if relevance is not None:

                print(
                    f"    Relevance : "
                    f"{relevance:.2f}%"
                )

            matched_skills = experience.get(
                "matched_skills",
                [],
            )

            if matched_skills:

                print(
                    "    Matched Skills: "
                    + ", ".join(
                        matched_skills
                    )
                )

    # ------------------------------------------------------------------------
    # DAY 11 - EDUCATION
    # ------------------------------------------------------------------------

    print_separator(
        "DAY 11 - EDUCATION ALIGNMENT"
    )

    education_parser = (
        EducationCertificationParser()
    )

    academic_profile = (
        education_parser.parse(
            resume_text
        )
    )

    education_alignment = (
        calculate_education_alignment(
            academic_profile,
            job_requirement.education,
        )
    )

    highest_degree = getattr(
        academic_profile,
        "highest_degree",
        None,
    )

    highest_degree_level = getattr(
        academic_profile,
        "highest_degree_level",
        None,
    )

    fields_of_study = getattr(
        academic_profile,
        "fields_of_study",
        [],
    ) or []

    print(
        "\nCandidate Education:"
    )

    print(
        f"  Highest Degree : "
        f"{highest_degree or 'Unavailable'}"
    )

    print(
        f"  Degree Level   : "
        f"{highest_degree_level or 'Unavailable'}"
    )

    print(
        f"  Fields         : "
        f"{', '.join(fields_of_study) if fields_of_study else 'Unavailable'}"
    )

    print(
        "\nJD Education Requirement:"
    )

    print(
        f"  {job_requirement.education or 'Not specified'}"
    )

    print(
        f"\nEducation Alignment: "
        f"{format_score(education_alignment)}"
    )

    # ------------------------------------------------------------------------
    # DAY 12 - SEMANTIC MATCHING
    # ------------------------------------------------------------------------

    print_separator(
        "DAY 12 - SEMANTIC MATCHING"
    )

    semantic_engine = (
        SemanticMatchingEngine()
    )

    # Use the preserved Work Experience section.
    semantic_experience_text = (
        work_experience_text
        or candidate.get(
            "experience",
            "",
        )
    )

    semantic_result = (
        semantic_engine.match(
            " ".join(
                candidate_skills
            ),
            " ".join(
                required_skills
            ),
            semantic_experience_text,
            job_requirement.experience,
            resume_text,
            "\n".join(
                job_requirement.responsibilities
            ),
        )
    )

    semantic_similarity = (
        semantic_result.overall_similarity
    )

    print(
        f"\nOverall Semantic Similarity : "
        f"{semantic_similarity:.4f} "
        f"({semantic_similarity * 100:.2f}%)"
    )

    print(
        f"Experience Similarity        : "
        f"{semantic_result.experience_similarity:.4f}"
    )

    print(
        f"Semantic Match               : "
        f"{semantic_result.matched}"
    )

    # ------------------------------------------------------------------------
    # DAY 13 - ATS SCORE
    # ------------------------------------------------------------------------

    print_separator(
        "DAY 13 - WEIGHTED ATS SCORING"
    )

    ats_engine = (
        ATSScoringEngine()
    )

    signals = {
        "skill_match":
            skill_match,

        "experience_relevance":
            experience_relevance,

        "education_alignment":
            education_alignment,

        "semantic_similarity":
            semantic_similarity,
    }

    result = (
        ats_engine.generate_candidate_score(
            candidate_id=(
                candidate.get(
                    "name",
                    "",
                )
                or "candidate"
            ),
            role=job_requirement.role,
            signals=signals,
        )
    )

    # ------------------------------------------------------------------------
    # Final ATS output
    # ------------------------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "FINAL ATS SCORE"
    )

    print(
        "=" * 70
    )

    final_score = result.get(
        "final_score"
    )

    if final_score is not None:

        print(
            f"\nFinal Score        : "
            f"{final_score * 100:.2f}%"
        )

    else:

        print(
            "\nFinal Score        : "
            "Unavailable"
        )

    print(
        f"Candidate          : "
        f"{result.get('candidate_id', candidate.get('name', 'candidate'))}"
    )

    print(
        f"Role               : "
        f"{result.get('role', job_requirement.role)}"
    )

    print(
        f"Normalized Role    : "
        f"{result.get('normalized_role', 'unknown')}"
    )

    # ------------------------------------------------------------------------
    # Available signals
    # ------------------------------------------------------------------------

    available_signals = result.get(
        "available_signals",
        [],
    )

    missing_signals = result.get(
        "missing_signals",
        [],
    )

    print(
        "\nAvailable Signals:"
    )

    if available_signals:

        for signal in available_signals:

            print(
                f"  - {signal}"
            )

    else:

        print(
            "  None"
        )

    print(
        "\nMissing Signals:"
    )

    if missing_signals:

        for signal in missing_signals:

            print(
                f"  - {signal}"
            )

    else:

        print(
            "  None"
        )

    # ------------------------------------------------------------------------
    # Component breakdown
    # ------------------------------------------------------------------------

    print(
        "\nComponent Breakdown:"
    )

    component_breakdown = result.get(
        "component_breakdown",
        {},
    )

    if component_breakdown:

        for name, component in (
            component_breakdown.items()
        ):

            score = component.get(
                "score"
            )

            base_weight = component.get(
                "base_weight",
                0.0,
            )

            effective_weight = component.get(
                "effective_weight",
                0.0,
            )

            contribution = component.get(
                "contribution",
                0.0,
            )

            if score is None:

                score_text = (
                    "Unavailable"
                )

            else:

                score_text = (
                    f"{score:.4f}"
                )

            print(
                f"  {name:<25}"
                f"score={score_text:>12} "
                f"base={base_weight:.4f} "
                f"effective={effective_weight:.4f} "
                f"contribution={contribution:.4f}"
            )

    # ------------------------------------------------------------------------
    # Signal summary
    # ------------------------------------------------------------------------

    print(
        "\nSignal Summary:"
    )

    print(
        f"  Skill Match          : "
        f"{format_score(skill_match)}"
    )

    print(
        f"  Experience Relevance : "
        f"{format_score(experience_relevance)}"
    )

    print(
        f"  Education Alignment  : "
        f"{format_score(education_alignment)}"
    )

    print(
        f"  Semantic Similarity  : "
        f"{format_score(semantic_similarity)}"
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "DAY 13 CANDIDATE SCORING COMPLETE"
    )

    print(
        "=" * 70
    )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()