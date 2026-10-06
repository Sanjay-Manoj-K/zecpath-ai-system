"""
Day 18 - Resume Quality and Entity Detection

Purpose:
    Improve ATS robustness when resume extraction produces noisy or
    inconsistently formatted text.

Capabilities:
    - Unicode normalization
    - Whitespace normalization
    - Separator normalization
    - Safe line cleanup
    - Repeated-line removal
    - Basic candidate entity detection
    - Conservative candidate-name detection

Important:
    This module does not invent missing resume information.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import List, Optional


# ============================================================================
# DATA MODEL
# ============================================================================


@dataclass
class ResumeEntities:
    """
    Basic entities detected from resume text.
    """

    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    urls: List[str] | None = None


# ============================================================================
# TEXT NORMALIZATION
# ============================================================================


def normalize_resume_text(
    text: str,
) -> str:
    """
    Conservatively normalize extracted resume text.

    The underlying resume information is preserved while common
    extraction noise is reduced.
    """

    if not text:
        return ""

    # ------------------------------------------------------------------
    # Unicode normalization
    # ------------------------------------------------------------------

    text = unicodedata.normalize(
        "NFKC",
        text,
    )

    # ------------------------------------------------------------------
    # Remove invisible / non-standard characters
    # ------------------------------------------------------------------

    replacements = {
        "\u00A0": " ",   # non-breaking space
        "\u2007": " ",   # figure space
        "\u202F": " ",   # narrow no-break space
        "\u200B": "",    # zero-width space
        "\u200C": "",    # zero-width non-joiner
        "\u200D": "",    # zero-width joiner
        "\uFEFF": "",    # BOM / zero-width no-break space
        "\u00AD": "",    # soft hyphen
    }

    for old_value, new_value in replacements.items():
        text = text.replace(
            old_value,
            new_value,
        )

    # ------------------------------------------------------------------
    # Normalize line endings
    # ------------------------------------------------------------------

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    # ------------------------------------------------------------------
    # Normalize common typography
    # ------------------------------------------------------------------

    text = (
        text
        .replace("–", "-")
        .replace("—", "-")
        .replace("−", "-")
        .replace("‐", "-")
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
    )

    # ------------------------------------------------------------------
    # Normalize separators
    # ------------------------------------------------------------------

    text = re.sub(
        r"\s*\|\s*",
        " | ",
        text,
    )

    # ------------------------------------------------------------------
    # Normalize repeated whitespace while preserving line structure
    # ------------------------------------------------------------------

    cleaned_lines: List[str] = []

    for line in text.splitlines():

        line = re.sub(
            r"[ \t]+",
            " ",
            line,
        ).strip()

        if not line:
            continue

        cleaned_lines.append(
            line
        )

    # ------------------------------------------------------------------
    # Remove duplicate lines
    # ------------------------------------------------------------------

    result: List[str] = []
    seen = set()

    for line in cleaned_lines:

        key = re.sub(
            r"\s+",
            " ",
            line,
        ).strip().lower()

        if key in seen:
            continue

        seen.add(key)
        result.append(line)

    return "\n".join(
        result
    ).strip()


# ============================================================================
# ENTITY PATTERNS
# ============================================================================


EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9._%+\-]+"
    r"@[A-Z0-9.\-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)


PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+?\d{1,3}[\s.\-]?)?"
    r"(?:\(?\d{2,4}\)?[\s.\-]?)?"
    r"\d{3,4}[\s.\-]?"
    r"\d{3,4}"
    r"(?!\d)"
)


URL_PATTERN = re.compile(
    r"\b(?:https?://|www\.)[^\s|]+",
    re.IGNORECASE,
)


NAME_STOP_WORDS = {
    "resume",
    "curriculum",
    "vitae",
    "cv",
    "profile",
    "summary",
    "objective",
    "experience",
    "work",
    "history",
    "education",
    "skills",
    "technical",
    "certifications",
    "projects",
    "contact",
    "phone",
    "email",
    "linkedin",
    "github",
    "portfolio",
}


# ============================================================================
# ENTITY HELPERS
# ============================================================================


def _clean_entity_value(
    value: str,
) -> str:
    """
    Clean an entity without changing its meaning.
    """

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip(
        " |,;:-"
    )


def detect_email(
    text: str,
) -> Optional[str]:
    """
    Detect the first email address.
    """

    match = EMAIL_PATTERN.search(
        text
    )

    if not match:
        return None

    return match.group(
        0
    ).strip()


def detect_phone(
    text: str,
) -> Optional[str]:
    """
    Detect the first plausible phone number.

    The detector requires a realistic digit count to avoid
    interpreting ordinary short numbers as phone values.
    """

    for match in PHONE_PATTERN.finditer(
        text
    ):

        value = _clean_entity_value(
            match.group(
                0
            )
        )

        digits = re.sub(
            r"\D",
            "",
            value,
        )

        if not 7 <= len(digits) <= 15:
            continue

        # Avoid treating a plain year or date fragment as a phone.
        if re.fullmatch(
            r"\d{4}",
            digits,
        ):
            continue

        return value

    return None


def detect_urls(
    text: str,
) -> List[str]:
    """
    Detect unique URLs from resume text.
    """

    urls: List[str] = []

    for match in URL_PATTERN.findall(
        text
    ):

        value = match.rstrip(
            ".,);"
        )

        if value and value not in urls:
            urls.append(
                value
            )

    return urls


# ============================================================================
# CANDIDATE NAME DETECTION
# ============================================================================


def _looks_like_name_candidate(
    line: str,
) -> bool:
    """
    Determine whether a line plausibly contains a person's name.
    """

    value = _clean_entity_value(
        line
    )

    if not value:
        return False

    if len(value) > 60:
        return False

    # Contact information is not a candidate name.
    if EMAIL_PATTERN.search(value):
        return False

    if URL_PATTERN.search(value):
        return False

    # Phone-like values are not names.
    digits = re.sub(
        r"\D",
        "",
        value,
    )

    if len(digits) >= 7:
        return False

    # Keep only alphabetic name characters for validation.
    normalized = re.sub(
        r"[^a-zA-Z\s'.-]",
        " ",
        value,
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    ).strip()

    if not normalized:
        return False

    words = normalized.split()

    if not 2 <= len(words) <= 5:
        return False

    if any(
        word.lower() in NAME_STOP_WORDS
        for word in words
    ):
        return False

    alphabetic_words = [
        word
        for word in words
        if any(
            char.isalpha()
            for char in word
        )
    ]

    if len(alphabetic_words) < 2:
        return False

    return True


def detect_candidate_name(
    text: str,
) -> Optional[str]:
    """
    Detect a candidate name from the first meaningful lines.

    Searching only the upper section helps prevent job titles,
    company names, and later content from being mistaken for a name.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Candidate identity normally occurs near the top.
    for line in lines[:12]:

        candidate = _clean_entity_value(
            line
        )

        # ----------------------------------------------------------
        # Labeled name
        # ----------------------------------------------------------

        candidate = re.sub(
            r"^(?:name|candidate)\s*:\s*",
            "",
            candidate,
            flags=re.IGNORECASE,
        )

        # ----------------------------------------------------------
        # Pipe-separated contact header
        # ----------------------------------------------------------

        if "|" in candidate:

            first_part = candidate.split(
                "|",
                1,
            )[0].strip()

            if _looks_like_name_candidate(
                first_part
            ):
                return first_part

        # ----------------------------------------------------------
        # Plain name line
        # ----------------------------------------------------------

        if _looks_like_name_candidate(
            candidate
        ):
            return candidate

    return None


# ============================================================================
# COMPLETE ENTITY DETECTION
# ============================================================================


def detect_entities(
    text: str,
) -> ResumeEntities:
    """
    Detect basic entities from normalized resume text.
    """

    normalized_text = normalize_resume_text(
        text
    )

    return ResumeEntities(
        candidate_name=detect_candidate_name(
            normalized_text
        ),
        email=detect_email(
            normalized_text
        ),
        phone=detect_phone(
            normalized_text
        ),
        urls=detect_urls(
            normalized_text
        ),
    )


# ============================================================================
# PUBLIC QUALITY PIPELINE
# ============================================================================


def prepare_resume(
    text: str,
) -> tuple[str, ResumeEntities]:
    """
    Normalize resume text and detect basic resume entities.
    """

    normalized_text = normalize_resume_text(
        text
    )

    entities = detect_entities(
        normalized_text
    )

    return (
        normalized_text,
        entities,
    )