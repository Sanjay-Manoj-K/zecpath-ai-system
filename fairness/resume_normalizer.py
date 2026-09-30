"""
Day 15 - Resume Normalization

Purpose:
    Convert different resume structures into a standard,
    ATS-friendly representation.

Design principles:
    - Preserve job-relevant information.
    - Use a consistent schema.
    - Avoid inventing missing information.
    - Keep normalization separate from ATS scoring.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional


# ============================================================================
# STANDARD RESUME MODEL
# ============================================================================


@dataclass
class NormalizedResume:
    """
    Standard representation of a resume.

    Missing information is represented by an empty value rather than
    fabricated content.
    """

    name: str = ""
    summary: str = ""

    skills: List[str] | None = None

    experience: List[Dict[str, Any]] | None = None

    education: List[Dict[str, Any]] | None = None

    certifications: List[str] | None = None

    projects: List[Dict[str, Any]] | None = None

    other: List[str] | None = None

    def __post_init__(self) -> None:
        self.skills = self.skills or []
        self.experience = self.experience or []
        self.education = self.education or []
        self.certifications = self.certifications or []
        self.projects = self.projects or []
        self.other = self.other or []

    def to_dict(self) -> Dict[str, Any]:
        """Return normalized resume as a dictionary."""

        return asdict(self)


# ============================================================================
# TEXT NORMALIZATION
# ============================================================================


def clean_text(value: Any) -> str:
    """
    Normalize whitespace while preserving the actual content.
    """

    if value is None:
        return ""

    text = str(value)

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize repeated spaces/tabs.
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize_string_list(
    values: Optional[Iterable[Any]],
) -> List[str]:
    """
    Normalize a list of strings.

    Empty values are removed and duplicates are eliminated while
    preserving the original order.
    """

    if not values:
        return []

    normalized: List[str] = []
    seen: set[str] = set()

    for value in values:

        cleaned = clean_text(value)

        if not cleaned:
            continue

        identity = cleaned.casefold()

        if identity in seen:
            continue

        seen.add(identity)
        normalized.append(cleaned)

    return normalized


# ============================================================================
# EXPERIENCE NORMALIZATION
# ============================================================================


def normalize_experience(
    experiences: Optional[Iterable[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """
    Normalize work-experience records into a consistent structure.

    No new information is created.
    """

    if not experiences:
        return []

    normalized: List[Dict[str, Any]] = []

    for item in experiences:

        if not isinstance(item, dict):
            continue

        record = {
            "job_title": clean_text(
                item.get("job_title")
                or item.get("title")
                or ""
            ),
            "company": clean_text(
                item.get("company")
                or item.get("organization")
                or ""
            ),
            "start_date": clean_text(
                item.get("start_date")
                or ""
            ),
            "end_date": clean_text(
                item.get("end_date")
                or ""
            ),
            "description": clean_text(
                item.get("description")
                or item.get("responsibilities")
                or ""
            ),
        }

        # Preserve existing relevance information when available.
        for key in (
            "relevance_score",
            "relevance_percent",
            "matched_skills",
            "candidate_role_family",
            "target_role_family",
        ):
            if key in item:
                record[key] = item[key]

        # Keep records that contain at least some useful information.
        if any(
            value
            for value in (
                record["job_title"],
                record["company"],
                record["description"],
            )
        ):
            normalized.append(record)

    return normalized


# ============================================================================
# EDUCATION NORMALIZATION
# ============================================================================


def normalize_education(
    education: Optional[Iterable[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """
    Normalize education records.
    """

    if not education:
        return []

    normalized: List[Dict[str, Any]] = []

    for item in education:

        if not isinstance(item, dict):
            continue

        record = {
            "degree": clean_text(
                item.get("degree")
                or item.get("qualification")
                or ""
            ),
            "field_of_study": clean_text(
                item.get("field_of_study")
                or item.get("field")
                or ""
            ),
            "institution": clean_text(
                item.get("institution")
                or item.get("college")
                or item.get("university")
                or ""
            ),
            "start_date": clean_text(
                item.get("start_date")
                or ""
            ),
            "end_date": clean_text(
                item.get("end_date")
                or ""
            ),
        }

        if any(record.values()):
            normalized.append(record)

    return normalized


# ============================================================================
# PROJECT NORMALIZATION
# ============================================================================


def normalize_projects(
    projects: Optional[Iterable[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """
    Normalize project records.
    """

    if not projects:
        return []

    normalized: List[Dict[str, Any]] = []

    for item in projects:

        if not isinstance(item, dict):
            continue

        record = {
            "name": clean_text(
                item.get("name")
                or item.get("title")
                or ""
            ),
            "description": clean_text(
                item.get("description")
                or ""
            ),
            "technologies": normalize_string_list(
                item.get("technologies")
                or item.get("skills")
                or []
            ),
        }

        if any(
            (
                record["name"],
                record["description"],
                record["technologies"],
            )
        ):
            normalized.append(record)

    return normalized


# ============================================================================
# GENERIC EXPERIENCE CONVERSION
# ============================================================================


def normalize_generic_experience(
    experience: Any,
) -> List[Dict[str, Any]]:
    """
    Convert simple text/string experience data into the standard format
    without attempting to infer facts that are not explicitly present.
    """

    if not experience:
        return []

    if isinstance(experience, dict):
        return normalize_experience([experience])

    if isinstance(experience, (list, tuple)):
        if all(
            isinstance(item, dict)
            for item in experience
        ):
            return normalize_experience(experience)

        return [
            {
                "job_title": "",
                "company": "",
                "start_date": "",
                "end_date": "",
                "description": clean_text(item),
            }
            for item in experience
            if clean_text(item)
        ]

    return [
        {
            "job_title": "",
            "company": "",
            "start_date": "",
            "end_date": "",
            "description": clean_text(experience),
        }
    ]


# ============================================================================
# RESUME NORMALIZER
# ============================================================================


class ResumeNormalizer:
    """
    Normalize a parsed resume into a standard ATS representation.
    """

    SECTION_ALIASES = {
        "summary": {
            "summary",
            "profile",
            "professional summary",
            "career summary",
            "objective",
            "career objective",
        },
        "skills": {
            "skills",
            "technical skills",
            "core skills",
            "key skills",
            "technical competencies",
        },
        "experience": {
            "experience",
            "work experience",
            "professional experience",
            "employment",
            "employment history",
            "work history",
        },
        "education": {
            "education",
            "academic background",
            "academic qualifications",
            "qualifications",
        },
        "certifications": {
            "certifications",
            "certificates",
            "licenses",
        },
        "projects": {
            "projects",
            "academic projects",
            "personal projects",
            "key projects",
        },
    }

    def normalize(
        self,
        resume: Optional[Dict[str, Any]],
    ) -> NormalizedResume:
        """
        Normalize a parsed resume dictionary.

        Important:
            This function does not invent missing information.
        """

        if resume is None:
            resume = {}

        if not isinstance(resume, dict):
            raise TypeError(
                "resume must be a dictionary."
            )

        # --------------------------------------------------------------
        # Name
        # --------------------------------------------------------------

        name = clean_text(
            resume.get("name")
            or resume.get("candidate_name")
            or ""
        )

        # --------------------------------------------------------------
        # Summary
        # --------------------------------------------------------------

        summary = clean_text(
            resume.get("summary")
            or resume.get("profile")
            or resume.get("objective")
            or ""
        )

        # --------------------------------------------------------------
        # Skills
        # --------------------------------------------------------------

        raw_skills = (
            resume.get("skills")
            or resume.get("technical_skills")
            or []
        )

        if isinstance(raw_skills, str):
            raw_skills = re.split(
                r"[,;|\n]+",
                raw_skills,
            )

        skills = normalize_string_list(
            raw_skills
        )

        # --------------------------------------------------------------
        # Experience
        # --------------------------------------------------------------

        experience = normalize_experience(
            resume.get("experience")
        )

        if not experience:
            experience = normalize_generic_experience(
                resume.get("work_experience")
            )

        # --------------------------------------------------------------
        # Education
        # --------------------------------------------------------------

        education = normalize_education(
            resume.get("education")
        )

        # --------------------------------------------------------------
        # Certifications
        # --------------------------------------------------------------

        certifications = normalize_string_list(
            resume.get("certifications")
            or resume.get("certificates")
            or []
        )

        # --------------------------------------------------------------
        # Projects
        # --------------------------------------------------------------

        projects = normalize_projects(
            resume.get("projects")
        )

        # --------------------------------------------------------------
        # Other
        # --------------------------------------------------------------

        other_values = resume.get(
            "other",
            [],
        )

        if isinstance(other_values, str):
            other_values = [other_values]

        other = normalize_string_list(
            other_values
        )

        return NormalizedResume(
            name=name,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            certifications=certifications,
            projects=projects,
            other=other,
        )


# ============================================================================
# FLAT TEXT STANDARDIZATION
# ============================================================================


def normalize_resume_text(
    resume_text: str,
) -> str:
    """
    Standardize raw resume text before downstream parsing.

    This function intentionally performs only structural cleanup:
        - line-ending normalization
        - whitespace normalization
        - blank-line reduction

    It does NOT remove qualifications or rewrite candidate content.
    """

    text = clean_text(resume_text)

    if not text:
        return ""

    lines = text.splitlines()

    normalized_lines: List[str] = []

    for line in lines:

        cleaned = clean_text(line)

        if cleaned:
            normalized_lines.append(
                cleaned
            )

    return "\n".join(
        normalized_lines
    )