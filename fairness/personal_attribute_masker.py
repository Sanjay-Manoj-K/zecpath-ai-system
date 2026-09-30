"""
Day 15 - Personal Attribute Masking

Purpose:
    Remove or mask non-essential personal attributes from resume
    information before fairness-sensitive evaluation.

Important:
    The original resume data is not modified.
    A sanitized copy is returned.
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Dict, List


MASK = "[MASKED]"


class PersonalAttributeMasker:
    """
    Detect and mask commonly found non-essential personal attributes.

    The exact attribute scope is configurable and represents an
    implementation choice for Day 15.
    """

    DEFAULT_FIELDS = {
        "email",
        "phone",
        "date_of_birth",
        "dob",
        "age",
        "gender",
        "sex",
        "marital_status",
        "religion",
        "nationality",
        "caste",
        "community",
        "address",
    }

    # --------------------------------------------------------------
    # Regex patterns
    # --------------------------------------------------------------

    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    PHONE_PATTERN = re.compile(
        r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)"
    )

    DOB_PATTERN = re.compile(
        r"\b(?:"
        r"date\s+of\s+birth"
        r"|dob"
        r")\s*[:\-]\s*"
        r"[A-Za-z0-9,\-/ ]+",
        re.IGNORECASE,
    )

    AGE_PATTERN = re.compile(
        r"\bage\s*[:\-]?\s*\d{1,3}\s*(?:years?|yrs?)?\b",
        re.IGNORECASE,
    )

    GENDER_PATTERN = re.compile(
        r"\b(?:gender|sex)\s*[:\-]\s*"
        r"(?:male|female|other|non-binary|nonbinary)\b",
        re.IGNORECASE,
    )

    MARITAL_PATTERN = re.compile(
        r"\bmarital\s+status\s*[:\-]\s*"
        r"(?:single|married|divorced|widowed|separated)\b",
        re.IGNORECASE,
    )

    RELIGION_PATTERN = re.compile(
        r"\breligion\s*[:\-]\s*[A-Za-z][A-Za-z .'-]*",
        re.IGNORECASE,
    )

    NATIONALITY_PATTERN = re.compile(
        r"\bnationality\s*[:\-]\s*[A-Za-z][A-Za-z .'-]*",
        re.IGNORECASE,
    )

    CASTE_PATTERN = re.compile(
        r"\b(?:caste|community)\s*[:\-]\s*[A-Za-z][A-Za-z .'-]*",
        re.IGNORECASE,
    )

    ADDRESS_PATTERN = re.compile(
        r"\b(?:address|residential address|home address)"
        r"\s*[:\-]\s*[^;\n]+",
        re.IGNORECASE,
    )

    URL_PATTERN = re.compile(
        r"\bhttps?://[^\s]+",
        re.IGNORECASE,
    )

    # --------------------------------------------------------------
    # Text masking
    # --------------------------------------------------------------

    @classmethod
    def mask_text(
        cls,
        text: str,
    ) -> str:
        """
        Mask detectable non-essential personal information in text.
        """

        if not text:
            return ""

        masked = str(text)

        patterns = (
            cls.EMAIL_PATTERN,
            cls.PHONE_PATTERN,
            cls.DOB_PATTERN,
            cls.AGE_PATTERN,
            cls.GENDER_PATTERN,
            cls.MARITAL_PATTERN,
            cls.RELIGION_PATTERN,
            cls.NATIONALITY_PATTERN,
            cls.CASTE_PATTERN,
            cls.ADDRESS_PATTERN,
            cls.URL_PATTERN,
        )

        for pattern in patterns:
            masked = pattern.sub(
                MASK,
                masked,
            )

        return masked

    # --------------------------------------------------------------
    # Field masking
    # --------------------------------------------------------------

    @classmethod
    def mask_field(
        cls,
        field_name: str,
        value: Any,
    ) -> Any:
        """
        Mask a structured resume field when it is considered
        non-essential to candidate evaluation.
        """

        normalized_name = (
            field_name
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        if normalized_name in cls.DEFAULT_FIELDS:
            return MASK

        if isinstance(value, str):
            return cls.mask_text(value)

        return value

    # --------------------------------------------------------------
    # Dictionary masking
    # --------------------------------------------------------------

    @classmethod
    def mask_resume_dict(
        cls,
        resume: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Return a sanitized copy of a structured resume.

        Original input remains unchanged.
        """

        if not isinstance(resume, dict):
            raise TypeError(
                "resume must be a dictionary."
            )

        sanitized = deepcopy(resume)

        return cls._mask_nested_dict(
            sanitized
        )

    @classmethod
    def _mask_nested_dict(
        cls,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Recursively sanitize nested dictionaries and lists.
        """

        result: Dict[str, Any] = {}

        for key, value in data.items():

            normalized_name = (
                str(key)
                .strip()
                .lower()
                .replace("-", "_")
                .replace(" ", "_")
            )

            if normalized_name in cls.DEFAULT_FIELDS:
                result[key] = MASK
                continue

            if isinstance(value, dict):
                result[key] = cls._mask_nested_dict(
                    value
                )

            elif isinstance(value, list):

                result[key] = [
                    cls._mask_nested_dict(item)
                    if isinstance(item, dict)
                    else (
                        cls.mask_text(item)
                        if isinstance(item, str)
                        else item
                    )
                    for item in value
                ]

            elif isinstance(value, str):
                result[key] = cls.mask_text(value)

            else:
                result[key] = value

        return result

    # --------------------------------------------------------------
    # Field report
    # --------------------------------------------------------------

    @classmethod
    def detect_attributes(
        cls,
        text: str,
    ) -> List[str]:
        """
        Report which personal-attribute patterns are detected.
        """

        if not text:
            return []

        detected: List[str] = []

        checks = (
            ("email", cls.EMAIL_PATTERN),
            ("phone", cls.PHONE_PATTERN),
            ("date_of_birth", cls.DOB_PATTERN),
            ("age", cls.AGE_PATTERN),
            ("gender", cls.GENDER_PATTERN),
            ("marital_status", cls.MARITAL_PATTERN),
            ("religion", cls.RELIGION_PATTERN),
            ("nationality", cls.NATIONALITY_PATTERN),
            ("caste_or_community", cls.CASTE_PATTERN),
            ("address", cls.ADDRESS_PATTERN),
            ("social_or_web_identifier", cls.URL_PATTERN),
        )

        for name, pattern in checks:

            if pattern.search(text):
                detected.append(name)

        return detected