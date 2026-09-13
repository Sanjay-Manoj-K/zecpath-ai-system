"""
Zecpath AI System
Education & Certification Parser

Conservative rule-based extraction of:
- degree type
- field of study
- institution
- graduation year / graduation text
- certifications
- certification issuer
- certification relevance category

The parser intentionally leaves ambiguous information as None rather than
inventing values.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass
class EducationRecord:
    degree_type: Optional[str] = None
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    graduation_year_text: Optional[str] = None
    location: Optional[str] = None
    normalized_degree: Optional[str] = None
    normalized_field: Optional[str] = None
    raw_text: Optional[str] = None


@dataclass
class CertificationRecord:
    name: str
    normalized_name: Optional[str] = None
    issuer: Optional[str] = None
    year: Optional[int] = None
    year_text: Optional[str] = None
    relevance_category: str = "general"
    raw_text: Optional[str] = None


@dataclass
class AcademicProfile:
    education: List[EducationRecord] = field(default_factory=list)
    certifications: List[CertificationRecord] = field(default_factory=list)
    highest_degree: Optional[str] = None
    highest_degree_level: Optional[str] = None
    fields_of_study: List[str] = field(default_factory=list)
    institutions: List[str] = field(default_factory=list)
    certification_categories: Dict[str, List[str]] = field(default_factory=dict)


# =============================================================================
# PARSER
# =============================================================================


class EducationCertificationParser:
    """Conservative rule-based education and certification parser."""

    EDUCATION_HEADINGS = {
        "education",
        "academic background",
        "academic qualifications",
        "educational background",
        "academic history",
        "education & qualifications",
        "education and qualifications",
        "qualifications",
    }

    CERTIFICATION_HEADINGS = {
        "certifications",
        "certification",
        "certificates",
        "professional certifications",
        "licenses & certifications",
        "licenses and certifications",
        "licenses",
    }

    STOP_HEADINGS = {
        "experience",
        "professional experience",
        "work experience",
        "relevant experience",
        "employment",
        "work history",
        "professional history",
        "skills",
        "technical skills",
        "key skills",
        "additional skills",
        "core skills",
        "projects",
        "academic projects",
        "relevant projects",
        "certifications",
        "certification",
        "certificates",
        "professional certifications",
        "licenses & certifications",
        "licenses and certifications",
        "relevant coursework",
        "coursework",
        "awards",
        "awards & recognition",
        "achievements",
        "languages",
        "interests",
        "hobbies & interests",
        "references",
        "objective",
        "summary",
        "professional summary",
        "additional information",
        "memberships",
    }

    # Ordered from specific to generic.
    DEGREE_PATTERNS = [
        (r"\bdoctor of philosophy\b", "PhD", "doctorate"),
        (r"\bph\.?d\.?\b", "PhD", "doctorate"),
        (r"\bj\.?d\.?\b", "Juris Doctor", "doctorate"),
        (r"\bjuris doctor\b", "Juris Doctor", "doctorate"),
        (r"\bdoctor of\b", "Doctorate", "doctorate"),
        (r"\bmaster(?:'s)?\s+of\s+computer\s+applications\b", "Master of Computer Applications", "masters"),
        (r"\bmaster(?:'s)?\s+of\s+business\s+administration\b", "Master of Business Administration", "masters"),
        (r"\bmaster(?:'s)?\s+of\s+science\b", "Master of Science", "masters"),
        (r"\bmaster(?:'s)?\s+of\s+arts\b", "Master of Arts", "masters"),
        (r"\bmaster(?:'s)?\s+degree\b", "Master's Degree", "masters"),
        (r"\bm\.?c\.?a\.?\b", "Master of Computer Applications", "masters"),
        (r"\bm\.?b\.?a\.?\b", "Master of Business Administration", "masters"),
        (r"\bm\.?s\.?\b", "Master of Science", "masters"),
        (r"\bm\.?a\.?\b", "Master of Arts", "masters"),
        (r"\bbachelor(?:'s)?\s+of\s+computer\s+applications\b", "Bachelor of Computer Applications", "bachelors"),
        (r"\bbachelor(?:'s)?\s+of\s+business\s+administration\b", "Bachelor of Business Administration", "bachelors"),
        (r"\bbachelor(?:'s)?\s+of\s+science\b", "Bachelor of Science", "bachelors"),
        (r"\bbachelor(?:'s)?\s+of\s+arts\b", "Bachelor of Arts", "bachelors"),
        (r"\bbachelor(?:'s)?\s+degree\b", "Bachelor's Degree", "bachelors"),
        (r"(?<![A-Za-z])b\.?\s*c\.?\s*a\.?(?![A-Za-z])", "Bachelor of Computer Applications", "bachelors"),
        (r"(?<![A-Za-z])b\.?\s*b\.?\s*a\.?(?![A-Za-z])", "Bachelor of Business Administration", "bachelors"),
        (r"(?<![A-Za-z])b\.?\s*s\.?(?![A-Za-z])", "Bachelor of Science", "bachelors"),
        (r"(?<![A-Za-z])b\.?\s*a\.?(?![A-Za-z])", "Bachelor of Arts", "bachelors"),
        (r"\bassociate(?:'s)?\s+degree\b", "Associate Degree", "associate"),
        (r"(?<![A-Za-z])a\.?\s*s\.?(?![A-Za-z])", "Associate Degree", "associate"),
        (r"\badvanced diploma\b", "Advanced Diploma", "diploma"),
        (r"\bdiploma\b", "Diploma", "diploma"),
    ]

    CERTIFICATION_CATEGORY_KEYWORDS = {
        "technology": {
            "aws", "azure", "gcp", "google cloud", "microsoft azure", "cloud",
            "python", "java", "javascript", "oracle", "sql", "database",
            "cisco", "comptia", "cybersecurity", "security", "network", "linux",
            "kubernetes", "docker", "devops", "machine learning",
            "artificial intelligence", "data science", "data analytics",
        },
        "management": {
            "pmp", "project management", "scrum", "agile", "product management",
            "management", "leadership",
        },
        "finance": {
            "cfa", "acca", "cpa", "finance", "accounting", "quickbooks",
            "financial", "tax",
        },
        "design": {
            "adobe", "photoshop", "figma", "ux", "ui", "user experience",
            "user interface", "graphic design",
        },
        "marketing": {
            "marketing", "digital marketing", "seo", "sem", "google ads",
            "analytics", "content marketing",
        },
        "language": {
            "ielts", "toefl", "language proficiency", "english proficiency",
            "french", "german", "spanish",
        },
        "general": {
            "first aid", "safety", "communication", "soft skills",
        },
    }

    CERTIFICATION_HINTS = (
        "certification",
        "certificate",
        "certified",
        "professional certificate",
        "credential",
        "license",
    )

    CERTIFICATION_PREFIXES = (
        "aws ",
        "microsoft certified",
        "google certified",
        "google cloud",
        "oracle certified",
        "cisco certified",
        "comptia ",
        "pmp",
        "cfa ",
        "acca",
        "cpa",
        "scrum",
    )

    def __init__(self) -> None:
        self.degree_patterns = [
            (re.compile(pattern, re.IGNORECASE), normalized, level)
            for pattern, normalized, level in self.DEGREE_PATTERNS
        ]

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def parse(
        self,
        text: str,
        sections: Optional[Dict[str, str]] = None,
    ) -> AcademicProfile:
        if not text and not sections:
            return AcademicProfile()

        education_text = ""
        certification_text = ""

        if sections:
            education_text = self._get_section_text(sections, "education")
            certification_text = self._get_section_text(sections, "certifications")

        if not education_text:
            education_text = self.extract_section(text, self.EDUCATION_HEADINGS)

        if not certification_text:
            certification_text = self.extract_section(text, self.CERTIFICATION_HEADINGS)

        education = self.parse_education(education_text)
        certifications = self.parse_certifications(certification_text)

        # Some PDF/DOCX extractors do not preserve certification headings.
        # Fall back to scanning the document, but only for strong certificate
        # signals and never for headings or a lone word such as "Certificate".
        if not certifications and text:
            certifications = self._scan_certifications_from_text(text)

        return self.build_profile(education, certifications)

    # =========================================================================
    # SECTION EXTRACTION
    # =========================================================================

    def extract_section(
        self,
        text: str,
        target_headings: Iterable[str],
    ) -> str:
        lines = self._prepare_lines(text)
        if not lines:
            return ""

        targets = {self._normalize_heading(value) for value in target_headings}
        stops = {self._normalize_heading(value) for value in self.STOP_HEADINGS}

        for index, line in enumerate(lines):
            if self._normalize_heading(line) not in targets:
                continue

            result: List[str] = []
            for candidate in lines[index + 1 :]:
                normalized = self._normalize_heading(candidate)
                if normalized in stops:
                    break
                result.append(candidate)
            return "\n".join(result).strip()

        return ""

    # =========================================================================
    # EDUCATION
    # =========================================================================

    def parse_education(self, section_text: str) -> List[EducationRecord]:
        if not section_text:
            return []

        lines = self._prepare_lines(section_text)
        degree_indices = [i for i, line in enumerate(lines) if self._detect_degree(line)]

        if not degree_indices:
            return self._fallback_education_parse(lines)

        records: List[EducationRecord] = []

        # Critical fix: each degree owns text only until the NEXT degree.
        # This prevents one degree from inheriting another degree's institution
        # and graduation year.
        for position, degree_index in enumerate(degree_indices):
            next_degree_index = degree_indices[position + 1] if position + 1 < len(degree_indices) else len(lines)

            # Include a small amount of pre-degree context ONLY for the first
            # detected degree. This captures layouts such as:
            #   UNIVERSITY NAME
            #   Bachelor of Science ...
            # but prevents later degrees from inheriting the first degree's
            # institution or graduation data.
            if position == 0:
                block_start = max(0, degree_index - 4)
            else:
                block_start = degree_index

            block = lines[block_start:next_degree_index]
            degree_line = lines[degree_index]
            degree_index_in_block = degree_index - block_start

            degree_info = self._detect_degree(degree_line)
            if not degree_info:
                continue

            degree_type, degree_level = degree_info
            field = self._extract_field_of_study_from_block(block, degree_type)
            institution = self._find_institution(block, degree_index_in_block=degree_index_in_block)
            graduation_text, graduation_year = self._extract_graduation_year(block)
            location = self._extract_location(block, institution=institution)

            records.append(
                EducationRecord(
                    degree_type=degree_type,
                    field_of_study=field,
                    institution=institution,
                    graduation_year=graduation_year,
                    graduation_year_text=graduation_text,
                    location=location,
                    normalized_degree=self._normalize_degree(degree_type, degree_level),
                    normalized_field=self._normalize_field(field),
                    raw_text=" | ".join(block),
                )
            )

        return self._deduplicate_education(records)

    def _fallback_education_parse(self, lines: Sequence[str]) -> List[EducationRecord]:
        # Kept deliberately conservative. This path is used only when an
        # education heading is absent but degree evidence is present.
        records: List[EducationRecord] = []
        degree_indices = [i for i, line in enumerate(lines) if self._detect_degree(line)]

        for position, index in enumerate(degree_indices):
            next_index = degree_indices[position + 1] if position + 1 < len(degree_indices) else len(lines)
            block = lines[index:next_index]
            info = self._detect_degree(lines[index])
            if not info:
                continue
            degree_type, level = info
            field = self._extract_field_of_study_from_block(block, degree_type)
            institution = self._find_institution(block, degree_index_in_block=degree_index_in_block)
            graduation_text, graduation_year = self._extract_graduation_year(block)
            location = self._extract_location(block, institution=institution)

            records.append(
                EducationRecord(
                    degree_type=degree_type,
                    field_of_study=field,
                    institution=institution,
                    graduation_year=graduation_year,
                    graduation_year_text=graduation_text,
                    location=location,
                    normalized_degree=self._normalize_degree(degree_type, level),
                    normalized_field=self._normalize_field(field),
                    raw_text=" | ".join(block),
                )
            )

        return self._deduplicate_education(records)

    # =========================================================================
    # DEGREE / FIELD
    # =========================================================================

    def _detect_degree(self, text: str) -> Optional[Tuple[str, str]]:
        value = self._clean_line(text)
        for pattern, normalized, level in self.degree_patterns:
            if pattern.search(value):
                return normalized, level
        return None

    def _is_degree_line(self, text: str) -> bool:
        return self._detect_degree(text) is not None

    def _extract_field_of_study_from_block(
        self,
        block: Sequence[str],
        degree_type: str,
    ) -> Optional[str]:
        # First inspect the degree line itself.
        degree_line_index = next(
            (i for i, line in enumerate(block) if self._is_degree_line(line)),
            0,
        )
        field = self._extract_field_from_line(block[degree_line_index], degree_type)

        # PDF extraction may split the field across lines:
        # "Bachelor of Science in Data" + "Science".
        if field and degree_line_index + 1 < len(block):
            continuation = self._clean_line(block[degree_line_index + 1])
            if self._looks_like_field_fragment(continuation):
                joined = self._clean_field(field + " " + continuation)
                if self._valid_field(joined):
                    return joined
            return field

        if field:
            return field

        for i in range(degree_line_index + 1, min(len(block), degree_line_index + 5)):
            current = self._clean_line(block[i])
            if self._is_non_field_line(current):
                continue
            if self._is_heading(current) or self._looks_like_status_text(current):
                continue
            if self._looks_like_date_or_year(current) or self._looks_like_location(current):
                continue

            # Do not grab institution names as fields.
            if self._looks_like_institution(current):
                continue

            # If the previous degree line ended with a plausible field fragment,
            # join it with the next short alphabetic line.
            previous = self._clean_line(block[i - 1])
            if self._looks_like_field_fragment(current) and self._looks_like_field_fragment(previous):
                joined = self._clean_field(previous + " " + current)
                joined = self._remove_degree_prefix(joined, degree_type)
                if self._valid_field(joined):
                    return joined

        # Another common layout has "Major:" on its own line.
        for line in block[:5]:
            match = re.search(r"\bmajor(?:ing)?\s*(?:in|:)\s*(.+)$", line, re.IGNORECASE)
            if match:
                value = self._clean_field(match.group(1))
                if self._valid_field(value):
                    return value

        return None

    def _extract_field_from_line(self, line: str, degree_type: str) -> Optional[str]:
        value = self._clean_line(line)

        # Remove date/status suffixes before field extraction.
        value = re.sub(
            r",?\s*(?:candidate,?\s*)?expected\s+graduation\s*:?\s*.*$",
            "",
            value,
            flags=re.IGNORECASE,
        )
        value = re.sub(r"\b(?:in progress|current|present)\b", "", value, flags=re.IGNORECASE)

        patterns = (
            r"\bin\s+(.+?)(?=\s*\(|\s*,\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(?:19|20)(?:\d{2}|xx)\b|\s*,\s*(?:19|20)(?:\d{2}|xx)\b|$)",
            r"\bmajor(?:ing)?\s*(?:in|:)\s*(.+?)(?=\s*\(|\s*,|$)",
            r":\s*(.+?)(?=\s*\(|\s*,|$)",
        )

        for pattern in patterns:
            match = re.search(pattern, value, re.IGNORECASE)
            if match:
                candidate = self._clean_field(match.group(1))
                candidate = self._remove_date_suffix(candidate)
                if self._valid_field(candidate):
                    return candidate

        parenthetical = re.search(r"\(([^)]{2,100})\)", value)
        if parenthetical:
            candidate = re.sub(r"\bconcentration\s*:\s*", "", parenthetical.group(1), flags=re.IGNORECASE)
            candidate = self._clean_field(candidate)
            if self._valid_field(candidate):
                return candidate

        return None

    def _remove_degree_prefix(self, value: str, degree_type: str) -> str:
        value = self._clean_field(value)
        prefix_patterns = [
            re.escape(degree_type),
            r"bachelor(?:'s)?\s+of\s+(?:science|arts|business administration|computer applications)",
            r"master(?:'s)?\s+of\s+(?:science|arts|business administration|computer applications)",
        ]
        for pattern in prefix_patterns:
            value = re.sub(rf"^{pattern}\s*(?::|-|in)?\s*", "", value, flags=re.IGNORECASE)
        return self._clean_field(value)

    def _remove_date_suffix(self, value: str) -> str:
        value = re.sub(r",?\s*(?:19|20)\d{2}\b.*$", "", value, flags=re.IGNORECASE)
        value = re.sub(r",?\s*(?:19|20)xx\b.*$", "", value, flags=re.IGNORECASE)
        value = re.sub(r",?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(?:19|20)\d{2}$", "", value, flags=re.IGNORECASE)
        return self._clean_field(value)

    def _valid_field(self, value: Optional[str]) -> bool:
        if not value:
            return False
        value = self._clean_field(value)
        if not value or len(value) < 2:
            return False
        if self._looks_like_status_text(value):
            return False
        if self._looks_like_date_or_year(value):
            return False
        if self._looks_like_location(value):
            return False
        if self._is_heading(value):
            return False
        if self._looks_like_institution(value):
            return False
        if re.fullmatch(r"(?:19|20)xx", value, re.IGNORECASE):
            return False
        return True

    def _looks_like_field_fragment(self, value: str) -> bool:
        value = self._clean_field(value)
        if not value or len(value) > 60:
            return False
        if self._is_heading(value) or self._looks_like_status_text(value):
            return False
        if self._looks_like_date_or_year(value) or self._looks_like_location(value):
            return False
        if self._looks_like_institution(value):
            return False
        return bool(re.fullmatch(r"[A-Za-z][A-Za-z &/'-]*", value))

    # =========================================================================
    # INSTITUTION / LOCATION
    # =========================================================================

    def _find_institution(
        self,
        block: Sequence[str],
        degree_index_in_block: int = 0,
    ) -> Optional[str]:
        institution_keywords = (
            "university",
            "college",
            "institute",
            "school",
            "academy",
        )

        scored: List[Tuple[int, int, str]] = []

        for index, raw in enumerate(block):
            value = self._strip_bullet(raw)
            if not value or index == degree_index_in_block:
                continue

            lower = value.lower()

            if self._is_heading(value):
                continue
            if self._is_degree_line(value):
                continue
            if self._looks_like_gpa(value) or self._looks_like_status_text(value):
                continue
            if self._looks_like_contact(value) or self._looks_like_coursework(value):
                continue
            if self._looks_like_skill_line(value):
                continue

            keyword_hit = any(keyword in lower for keyword in institution_keywords)
            if not keyword_hit:
                # A standalone institution can occasionally be missing the word
                # university/college; accept only title-like all-caps names.
                if not (value.isupper() and 2 <= len(value.split()) <= 10):
                    continue

            score = 0
            score += 30 if keyword_hit else 8
            score += 8 if value.isupper() else 0
            score -= abs(index - degree_index_in_block)
            if self._looks_like_location(value):
                score += 5 if keyword_hit else -5

            cleaned = self._clean_institution(value)
            if not cleaned:
                continue

            scored.append((score, index, cleaned))

        if not scored:
            return None

        scored.sort(key=lambda item: (-item[0], item[1]))
        return scored[0][2]

    def _clean_institution(self, value: str) -> str:
        value = self._clean_line(value)
        value = re.sub(r"\s+[–—-]\s+[^|]+$", "", value).strip()
        value = re.sub(r",\s*[A-Z]{2}(?:\s+\d{5}(?:-\d{4})?)?$", "", value)
        return self._clean_field(value)

    def _extract_location(
        self,
        block: Sequence[str],
        institution: Optional[str] = None,
    ) -> Optional[str]:
        for line in block:
            value = self._clean_line(line)
            if self._looks_like_location(value):
                if institution and self._clean_line(value).lower() == self._clean_line(institution).lower():
                    continue
                return value
            if institution and institution.lower() in value.lower():
                match = re.search(r"(?:,\s*)?([A-Za-z .'-]+,\s*[A-Z]{2}(?:\s+\d{5}(?:-\d{4})?)?)$", value)
                if match:
                    return match.group(1).strip()
        return None

    # =========================================================================
    # GRADUATION
    # =========================================================================

    def _extract_graduation_year(
        self,
        block: Sequence[str],
    ) -> Tuple[Optional[str], Optional[int]]:
        # Priority 1: explicit graduation/expected-graduation text.
        for line in block:
            lower = line.lower()
            if "graduat" in lower or "expected" in lower:
                year = self._extract_explicit_year(line)
                if year is not None:
                    return line, year
                placeholder = self._extract_placeholder_year(line)
                if placeholder:
                    return line, None

        # Priority 2: a degree line with an explicit month/year, e.g.
        # "Bachelor of Science: Data Science, June 2018".
        for line in block:
            if self._is_degree_line(line):
                year = self._extract_explicit_year(line)
                if year is not None:
                    return line, year
                placeholder = self._extract_placeholder_year(line)
                if placeholder:
                    return line, None

        # Priority 3: a bare year, but only if the block contains one degree.
        # For date ranges such as 01/2023 - 01/2026, do not invent a graduation
        # year because the semantics are ambiguous.
        for line in block:
            if re.search(r"\b\d{1,2}/(?:19|20)\d{2}\s*[-–—]\s*\d{1,2}/(?:19|20)\d{2}\b", line):
                continue
            year = self._extract_explicit_year(line)
            if year is not None:
                return line, year

            placeholder = self._extract_placeholder_year(line)
            if placeholder:
                return line, None

        return None, None

    def _extract_explicit_year(self, text: str) -> Optional[int]:
        match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
        return int(match.group(1)) if match else None

    def _extract_placeholder_year(self, text: str) -> Optional[str]:
        match = re.search(r"\b(?:19|20)xx\b", text, flags=re.IGNORECASE)
        return match.group(0) if match else None

    # =========================================================================
    # CERTIFICATIONS
    # =========================================================================

    def parse_certifications(self, section_text: str) -> List[CertificationRecord]:
        if not section_text:
            return []

        lines = self._prepare_lines(section_text)
        records: List[CertificationRecord] = []

        for line in lines:
            value = self._strip_bullet(line)
            if not value:
                continue
            if self._is_certification_heading(value):
                continue
            if not self._looks_like_certification(value):
                continue
            record = self._make_certification_record(value)
            if record:
                records.append(record)

        return self._deduplicate_certifications(records)

    def _scan_certifications_from_text(self, text: str) -> List[CertificationRecord]:
        records: List[CertificationRecord] = []
        for line in self._prepare_lines(text):
            value = self._strip_bullet(line)
            if not value or self._is_heading(value):
                continue
            if value.lower() in {"certificate", "certification", "certifications", "certificates"}:
                continue
            if not self._looks_like_certification(value):
                continue
            record = self._make_certification_record(value)
            if record:
                records.append(record)
        return self._deduplicate_certifications(records)

    def _make_certification_record(self, value: str) -> Optional[CertificationRecord]:
        name, issuer = self._split_certification(value)
        name = self._clean_certification_name(name)
        if not self._valid_certification_name(name):
            return None

        year_text, year = self._extract_year(value)
        normalized_name = self._normalize_certification_name(name)
        category = self._categorize_certification(normalized_name)

        return CertificationRecord(
            name=name,
            normalized_name=normalized_name,
            issuer=issuer,
            year=year,
            year_text=year_text,
            relevance_category=category,
            raw_text=value,
        )

    def _looks_like_certification(self, text: str) -> bool:
        lower = text.lower().strip()
        if self._is_certification_heading(text):
            return False
        if lower in {"certificate", "certification", "certifications", "certificates"}:
            return False

        # Strong explicit certification signals.
        if any(hint in lower for hint in self.CERTIFICATION_HINTS):
            # A generic phrase such as "certificate" alone is rejected above.
            return len(re.sub(r"[^a-z]", "", lower)) > 15

        return lower.startswith(self.CERTIFICATION_PREFIXES)

    def _is_certification_heading(self, text: str) -> bool:
        normalized = self._normalize_heading(text)
        return normalized in {self._normalize_heading(v) for v in self.CERTIFICATION_HEADINGS}

    def _split_certification(self, text: str) -> Tuple[str, Optional[str]]:
        for separator in (r"\s+-\s+", r"\s+–\s+", r"\s+—\s+", r"\s+\|\s+"):
            parts = re.split(separator, text, maxsplit=1)
            if len(parts) != 2:
                continue
            left, right = parts[0].strip(), parts[1].strip()
            if self._looks_like_issuer(right):
                return left, right
        return text, None

    def _looks_like_issuer(self, text: str) -> bool:
        lower = text.lower()
        issuer_terms = (
            "amazon web services", "aws", "microsoft", "google", "oracle", "cisco",
            "comptia", "institute", "university", "college", "academy", "association",
            "organization", "board", "pmi", "certification institute", "certification board",
        )
        return any(term in lower for term in issuer_terms)

    def _clean_certification_name(self, value: str) -> str:
        value = self._clean_line(value)
        value = re.sub(r"\s+\((?:19|20)\d{2}\)\s*$", "", value)
        value = re.sub(r"\s*[-–—|]\s*$", "", value)
        return value.strip(" .,:;-–—|")

    def _valid_certification_name(self, value: str) -> bool:
        lower = value.lower().strip()
        if not lower or lower in {"certificate", "certification", "certifications", "certificates"}:
            return False
        if len(re.sub(r"[^a-z]", "", lower)) < 8:
            return False
        return True

    # =========================================================================
    # NORMALIZATION / RELEVANCE
    # =========================================================================

    def _normalize_degree(self, value: str, level: str) -> str:
        mapping = {
            "Juris Doctor": "Juris Doctor",
            "Master of Science": "Master of Science",
            "Master of Arts": "Master of Arts",
            "Master of Business Administration": "Master of Business Administration",
            "Master of Computer Applications": "Master of Computer Applications",
            "Master's Degree": "Master's Degree",
            "Bachelor of Science": "Bachelor of Science",
            "Bachelor of Arts": "Bachelor of Arts",
            "Bachelor of Business Administration": "Bachelor of Business Administration",
            "Bachelor of Computer Applications": "Bachelor of Computer Applications",
            "Bachelor's Degree": "Bachelor's Degree",
            "Associate Degree": "Associate Degree",
            "Advanced Diploma": "Advanced Diploma",
            "Diploma": "Diploma",
            "PhD": "PhD",
            "Doctorate": "Doctorate",
        }
        return mapping.get(value, value.strip())

    def _normalize_field(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        value = self._clean_field(value)
        mapping = {
            "computer science": "Computer Science",
            "computer applications": "Computer Applications",
            "computer application": "Computer Applications",
            "information technology": "Information Technology",
            "information systems": "Information Systems",
            "data science": "Data Science",
            "artificial intelligence": "Artificial Intelligence",
            "machine learning": "Machine Learning",
            "business administration": "Business Administration",
            "finance": "Finance",
            "accounting": "Accounting",
            "marketing": "Marketing",
            "political science": "Political Science",
        }
        return mapping.get(value.lower(), value)

    def _normalize_certification_name(self, value: str) -> str:
        value = self._clean_line(value)
        mapping = {
            "aws certified cloud practitioner": "AWS Certified Cloud Practitioner",
            "aws cloud practitioner": "AWS Certified Cloud Practitioner",
            "microsoft certified azure fundamentals": "Microsoft Azure Fundamentals",
            "azure fundamentals": "Microsoft Azure Fundamentals",
            "google cloud digital leader": "Google Cloud Digital Leader",
            "comptia security+": "CompTIA Security+",
            "pmp": "Project Management Professional (PMP)",
        }
        return mapping.get(value.lower(), value)

    def _categorize_certification(self, name: Optional[str]) -> str:
        if not name:
            return "general"
        lower = name.lower()
        scores: Dict[str, int] = {}
        for category, keywords in self.CERTIFICATION_CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in lower)
            if score:
                scores[category] = score
        if not scores:
            return "general"
        return max(scores, key=scores.get)

    # =========================================================================
    # PROFILE
    # =========================================================================

    def build_profile(
        self,
        education: List[EducationRecord],
        certifications: List[CertificationRecord],
    ) -> AcademicProfile:
        degree_ranking = {
            "none": 0,
            "certificate": 0,
            "diploma": 1,
            "associate": 2,
            "bachelors": 3,
            "masters": 4,
            "doctorate": 5,
        }

        highest_record: Optional[EducationRecord] = None
        highest_level = "none"
        for record in education:
            level = self._degree_level(record.normalized_degree)
            if degree_ranking.get(level, 0) > degree_ranking.get(highest_level, 0):
                highest_record = record
                highest_level = level

        fields = self._unique_values(
            record.normalized_field for record in education if record.normalized_field
        )
        institutions = self._unique_values(
            record.institution for record in education if record.institution
        )

        categories: Dict[str, List[str]] = {}
        for certification in certifications:
            categories.setdefault(certification.relevance_category, [])
            if certification.normalized_name:
                categories[certification.relevance_category].append(certification.normalized_name)
        for category in categories:
            categories[category] = self._unique_values(categories[category])

        return AcademicProfile(
            education=education,
            certifications=certifications,
            highest_degree=highest_record.normalized_degree if highest_record else None,
            highest_degree_level=highest_level if highest_record else None,
            fields_of_study=fields,
            institutions=institutions,
            certification_categories=categories,
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _prepare_lines(self, text: str) -> List[str]:
        lines: List[str] = []
        for raw_line in text.splitlines():
            value = self._clean_line(raw_line)
            if value:
                lines.append(value)
        return lines

    def _clean_line(self, value: str) -> str:
        value = value.replace("\xa0", " ")
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    def _clean_field(self, value: str) -> str:
        value = self._clean_line(value)
        return value.strip(" .,:;-–—|•")

    def _strip_bullet(self, value: str) -> str:
        return re.sub(r"^[\u2022\u25cf\u25a0\u25aa\-*]+\s*", "", value).strip()

    def _normalize_heading(self, value: str) -> str:
        value = self._clean_line(value).lower()
        value = value.replace("&", "and")
        value = re.sub(r"[^a-z0-9\s]", " ", value)
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    def _get_section_text(self, sections: Dict[str, str], name: str) -> str:
        if name in sections and isinstance(sections[name], str):
            return sections[name]
        target = self._normalize_heading(name)
        for key, value in sections.items():
            if self._normalize_heading(key) == target and isinstance(value, str):
                return value
        return ""

    def _degree_level(self, degree: Optional[str]) -> str:
        if not degree:
            return "none"
        lower = degree.lower()
        if "phd" in lower or "doctor" in lower:
            return "doctorate"
        if "master" in lower:
            return "masters"
        if "bachelor" in lower:
            return "bachelors"
        if "associate" in lower:
            return "associate"
        if "diploma" in lower:
            return "diploma"
        if "certificate" in lower:
            return "certificate"
        return "none"

    def _looks_like_gpa(self, text: str) -> bool:
        return bool(re.search(r"\bgpa\b", text, re.IGNORECASE))

    def _looks_like_status_text(self, text: str) -> bool:
        lower = text.lower()
        terms = (
            "expected graduation",
            "graduation date",
            "graduated",
            "summa cum laude",
            "magna cum laude",
            "cum laude",
            "in progress",
            "candidate",
            "honors",
            "expected",
            "present",
        )
        return any(term in lower for term in terms)

    def _looks_like_coursework(self, text: str) -> bool:
        lower = text.lower()
        return lower.startswith("relevant coursework") or lower.startswith("coursework")

    def _looks_like_contact(self, text: str) -> bool:
        lower = text.lower()
        return (
            "@" in lower
            or bool(re.search(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b", lower))
            or "linkedin.com" in lower
            or "github.com" in lower
        )

    def _is_heading(self, text: str) -> bool:
        normalized = self._normalize_heading(text)
        headings = {
            self._normalize_heading(value)
            for value in (self.EDUCATION_HEADINGS | self.CERTIFICATION_HEADINGS | self.STOP_HEADINGS)
        }
        return normalized in headings

    def _looks_like_location(self, text: str) -> bool:
        value = self._clean_line(text)
        if re.search(r",\s*[A-Z]{2}(?:\s+\d{5}(?:-\d{4})?)?$", value):
            return True
        if re.search(r"\b\d{5}(?:-\d{4})?\b", value):
            return True
        return False

    def _looks_like_date_or_year(self, text: str) -> bool:
        value = self._clean_line(text)
        return bool(
            re.search(r"\b(?:19|20)\d{2}\b", value)
            or re.search(r"\b(?:19|20)xx\b", value, re.IGNORECASE)
            or re.search(r"\b\d{1,2}/(?:19|20)\d{2}\b", value)
            or re.search(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(?:19|20)\d{2}\b", value, re.IGNORECASE)
        )

    def _looks_like_institution(self, text: str) -> bool:
        lower = text.lower()
        return any(word in lower for word in ("university", "college", "institute", "school", "academy"))

    def _looks_like_skill_line(self, text: str) -> bool:
        lower = text.lower()
        prefixes = (
            "programming languages:",
            "software development tools:",
            "web development:",
            "skills:",
            "technical skills:",
            "data structures",
        )
        return lower.startswith(prefixes)

    def _is_non_field_line(self, text: str) -> bool:
        return (
            self._is_heading(text)
            or self._looks_like_contact(text)
            or self._looks_like_gpa(text)
            or self._looks_like_coursework(text)
            or self._looks_like_skill_line(text)
        )

    def _extract_year(self, text: str) -> Tuple[Optional[str], Optional[int]]:
        match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
        if match:
            return match.group(1), int(match.group(1))
        placeholder = re.search(r"\b(?:19|20)xx\b", text, flags=re.IGNORECASE)
        if placeholder:
            return placeholder.group(0), None
        return None, None

    def _unique_values(self, values: Iterable[str]) -> List[str]:
        result: List[str] = []
        seen = set()
        for value in values:
            cleaned = self._clean_line(value)
            if not cleaned:
                continue
            key = cleaned.lower()
            if key not in seen:
                seen.add(key)
                result.append(cleaned)
        return result

    def _deduplicate_education(self, records: List[EducationRecord]) -> List[EducationRecord]:
        result: List[EducationRecord] = []
        seen = set()
        for record in records:
            key = (
                (record.normalized_degree or "").lower(),
                (record.normalized_field or "").lower(),
                (record.institution or "").lower(),
                record.graduation_year,
                (record.graduation_year_text or "").lower(),
            )
            if key not in seen:
                seen.add(key)
                result.append(record)
        return result

    def _deduplicate_certifications(self, records: List[CertificationRecord]) -> List[CertificationRecord]:
        result: List[CertificationRecord] = []
        seen = set()
        for record in records:
            key = (
                (record.normalized_name or record.name).lower(),
                (record.issuer or "").lower(),
                record.year,
            )
            if key not in seen:
                seen.add(key)
                result.append(record)
        return result

    @staticmethod
    def to_dict(profile: AcademicProfile) -> Dict:
        return asdict(profile)


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================


def parse_education_certifications(
    text: str,
    sections: Optional[Dict[str, str]] = None,
) -> Dict:
    return EducationCertificationParser().to_dict(
        EducationCertificationParser().parse(text=text, sections=sections)
    )


# =============================================================================
# MANUAL TEST
# =============================================================================

if __name__ == "__main__":
    sample_text = """EDUCATION
Texas Tech University
Bachelor of Business Administration in Finance (in progress)
GPA: 3.9/4.0
Lubbock, TX
Expected graduation:
May 20XX
CERTIFICATIONS
AWS Certified Cloud Practitioner - Amazon Web Services
"""

    parser = EducationCertificationParser()
    profile = parser.parse(sample_text)

    print("\n=== EDUCATION ===")
    for item in profile.education:
        print(asdict(item))

    print("\n=== CERTIFICATIONS ===")
    for item in profile.certifications:
        print(asdict(item))

    print("\n=== ACADEMIC PROFILE ===")
    print(asdict(profile))
