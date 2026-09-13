"""Zecpath AI System - Day 11 Education & Certification Parser."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


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


class EducationCertificationParser:
    """Conservative, rule-based resume education/certification parser."""

    EDUCATION_HEADINGS = {
        "education", "academic background", "academic qualifications",
        "educational background", "academic history", "education & qualifications",
        "education and qualifications", "education qualifications", "academic credentials",
    }

    CERTIFICATION_HEADINGS = {
        "certifications", "certification", "certificates", "professional certifications",
        "professional certification", "professional certificates", "licenses & certifications",
        "licenses and certifications",
    }

    STOP_HEADINGS = {
        "experience", "professional experience", "work experience", "relevant experience",
        "employment", "work history", "professional history", "skills", "technical skills",
        "key skills", "additional skills", "core skills", "projects", "academic projects",
        "relevant projects", "certifications", "certification", "certificates",
        "professional certifications", "professional certification", "professional certificates",
        "licenses & certifications", "licenses and certifications", "relevant coursework",
        "coursework", "awards", "awards & recognition", "achievements", "languages",
        "interests", "hobbies & interests", "references", "objective", "summary",
        "professional summary", "additional information", "memberships", "activities",
    }

    DEGREE_PATTERNS = [
        (r"\bdoctor\s+of\s+philosophy\b", "PhD", "doctorate"),
        (r"\bph\.?\s*d\.?\b", "PhD", "doctorate"),
        (r"\bjuris\s+doctor\b", "Juris Doctor", "doctorate"),
        (r"(?<![A-Za-z0-9])J\.?\s*D\.?(?![A-Za-z0-9])", "Juris Doctor", "doctorate"),
        (r"\bdoctor(?:ate)?\b", "Doctorate", "doctorate"),
        (r"\bmaster(?:'s)?\s+of\s+computer\s+applications\b", "Master of Computer Applications", "masters"),
        (r"\bmaster(?:'s)?\s+of\s+business\s+administration\b", "Master of Business Administration", "masters"),
        (r"\bmaster(?:'s)?\s+of\s+science\b", "Master of Science", "masters"),
        (r"\bmaster(?:'s)?\s+of\s+arts\b", "Master of Arts", "masters"),
        (r"\bmaster(?:'s)?\s+degree\b", "Master's Degree", "masters"),
        (r"\bmaster(?:'s)?\b", "Master's Degree", "masters"),
        (r"(?<![A-Za-z0-9])M\.?\s*S\.?(?![A-Za-z0-9])", "Master of Science", "masters"),
        (r"(?<![A-Za-z0-9])M\.?\s*A\.?(?![A-Za-z0-9])", "Master of Arts", "masters"),
        (r"(?<![A-Za-z0-9])M\.?\s*B\.?\s*A\.?(?![A-Za-z0-9])", "Master of Business Administration", "masters"),
        (r"(?<![A-Za-z0-9])M\.?\s*C\.?\s*A\.?(?![A-Za-z0-9])", "Master of Computer Applications", "masters"),
        (r"\bbachelor(?:'s)?\s+of\s+computer\s+applications\b", "Bachelor of Computer Applications", "bachelors"),
        (r"\bbachelor(?:'s)?\s+of\s+business\s+administration\b", "Bachelor of Business Administration", "bachelors"),
        (r"\bbachelor(?:'s)?\s+of\s+science\b", "Bachelor of Science", "bachelors"),
        (r"\bbachelor(?:'s)?\s+of\s+arts\b", "Bachelor of Arts", "bachelors"),
        (r"\bbachelor(?:'s)?\s+degree\b", "Bachelor's Degree", "bachelors"),
        (r"\bbachelor(?:'s)?\b", "Bachelor's Degree", "bachelors"),
        (r"(?<![A-Za-z0-9])B\.?\s*S\.?(?![A-Za-z0-9])", "Bachelor of Science", "bachelors"),
        (r"(?<![A-Za-z0-9])B\.?\s*A\.?(?![A-Za-z0-9])", "Bachelor of Arts", "bachelors"),
        (r"(?<![A-Za-z0-9])B\.?\s*B\.?\s*A\.?(?![A-Za-z0-9])", "Bachelor of Business Administration", "bachelors"),
        (r"(?<![A-Za-z0-9])B\.?\s*C\.?\s*A\.?(?![A-Za-z0-9])", "Bachelor of Computer Applications", "bachelors"),
        (r"\bassociate(?:'s)?\s+degree\b", "Associate Degree", "associate"),
        (r"(?<![A-Za-z0-9])A\.?\s*S\.?(?![A-Za-z0-9])", "Associate Degree", "associate"),
        (r"\badvanced\s+diploma\b", "Advanced Diploma", "diploma"),
        (r"\bdiploma\b", "Diploma", "diploma"),
    ]

    CERTIFICATION_CATEGORY_KEYWORDS = {
        "technology": {
            "aws", "azure", "gcp", "google cloud", "microsoft azure", "cloud", "python",
            "java", "javascript", "oracle", "sql", "database", "cisco", "comptia",
            "cybersecurity", "security", "network", "linux", "kubernetes", "docker", "devops",
            "machine learning", "artificial intelligence", "data science", "data analytics",
        },
        "management": {"pmp", "project management", "scrum", "agile", "product management", "management", "leadership"},
        "finance": {"cfa", "acca", "cpa", "finance", "accounting", "quickbooks", "financial", "tax"},
        "design": {"adobe", "photoshop", "figma", "ux", "ui", "user experience", "user interface", "graphic design"},
        "language": {"ielts", "toefl", "language", "english proficiency", "french", "german", "spanish"},
    }

    CERTIFICATION_HINTS = ("certification", "certificate", "certified", "credential", "license")
    GENERIC_CERTIFICATION_TEXT = {
        "certification", "certifications", "certificate", "certificates", "certified",
        "professional certification", "professional certifications", "professional certificate",
        "professional certificates",
    }
    CERTIFICATION_FALSE_POSITIVES = {
        "microsoft office", "microsoft word", "microsoft excel", "microsoft powerpoint",
        "microsoft outlook", "ms office", "office 365",
    }

    def __init__(self) -> None:
        self.degree_patterns = [
            (re.compile(p, re.IGNORECASE), n, l)
            for p, n, l in self.DEGREE_PATTERNS
        ]

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def parse(self, text: str, sections: Optional[Dict[str, str]] = None) -> AcademicProfile:
        if not text and not sections:
            return AcademicProfile()

        education_text = ""
        certification_text = ""

        if sections:
            education_text = self._get_section_text(sections, "education")
            certification_text = self._get_section_text(sections, "certifications")

        if not education_text and text:
            education_text = self.extract_section(text, self.EDUCATION_HEADINGS)
        if not certification_text and text:
            certification_text = self.extract_section(text, self.CERTIFICATION_HEADINGS)

        if not education_text:
            education_text = text

        education = self.parse_education(education_text)

        if certification_text:
            certifications = self.parse_certifications(certification_text)
        else:
            certifications = self.parse_certifications(
                self._find_certification_lines_from_text(text)
            )

        return self.build_profile(education, certifications)

    # -------------------------------------------------------------------------
    # Sections
    # -------------------------------------------------------------------------

    def extract_section(self, text: str, target_headings: Iterable[str]) -> str:
        lines = self._prepare_lines(text)
        targets = {self._normalize_heading(x) for x in target_headings}
        stops = {self._normalize_heading(x) for x in self.STOP_HEADINGS}

        start = None
        for i, line in enumerate(lines):
            if self._normalize_heading(line) in targets:
                start = i + 1
                break

        if start is None:
            return ""

        result = []
        for line in lines[start:]:
            if self._normalize_heading(line) in stops:
                break
            result.append(line)

        return "\n".join(result).strip()

    def _get_section_text(self, sections: Dict[str, str], name: str) -> str:
        if name in sections and isinstance(sections[name], str):
            return sections[name]
        target = self._normalize_heading(name)
        for key, value in sections.items():
            if self._normalize_heading(key) == target and isinstance(value, str):
                return value
        return ""

    # -------------------------------------------------------------------------
    # Education
    # -------------------------------------------------------------------------

    def parse_education(self, section_text: str) -> List[EducationRecord]:
        if not section_text:
            return []

        lines = self._prepare_lines(section_text)
        degree_indices = [
            i for i, line in enumerate(lines)
            if self._detect_degree(line) is not None
        ]

        if not degree_indices:
            return []

        records: List[EducationRecord] = []

        for position, degree_index in enumerate(degree_indices):
            next_degree = (
                degree_indices[position + 1]
                if position + 1 < len(degree_indices)
                else len(lines)
            )

            # Important: later records never look into the previous degree.
            if position == 0:
                block_start = max(0, degree_index - 5)
            else:
                block_start = degree_indices[position - 1] + 1

            block = lines[block_start:next_degree]
            degree_info = self._detect_degree(lines[degree_index])
            if degree_info is None:
                continue

            degree_type, _level = degree_info

            field = self._extract_field_from_record(
                lines, degree_index, next_degree
            )

            institution = self._extract_institution_from_degree_line(
                lines[degree_index]
            )
            if institution is None:
                institution = self._find_institution(
                    block,
                    degree_index - block_start,
                )

            graduation_text, graduation_year = self._extract_graduation_year(
                block
            )

            location = self._extract_location(block)

            records.append(
                EducationRecord(
                    degree_type=degree_type,
                    field_of_study=field,
                    institution=institution,
                    graduation_year=graduation_year,
                    graduation_year_text=graduation_text,
                    location=location,
                    normalized_degree=degree_type,
                    normalized_field=self._normalize_field(field),
                    raw_text=" | ".join(block),
                )
            )

        return self._deduplicate_education(records)

    def _detect_degree(self, text: str) -> Optional[Tuple[str, str]]:
        value = self._clean_line(text)
        for pattern, normalized, level in self.degree_patterns:
            if pattern.search(value):
                return normalized, level
        return None

    def _is_degree_line(self, text: str) -> bool:
        return self._detect_degree(text) is not None

    def _degree_level(self, degree: Optional[str]) -> str:
        if not degree:
            return "none"
        lower = degree.lower()
        if "phd" in lower or "doctor" in lower or lower == "juris doctor":
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

    # -------------------------------------------------------------------------
    # Field
    # -------------------------------------------------------------------------

    def _extract_field_from_record(
        self,
        lines: Sequence[str],
        degree_index: int,
        block_end: int,
    ) -> Optional[str]:
        degree_line = lines[degree_index]
        field = self._extract_field_of_study(degree_line)
        if not field:
            return None

        pieces = [field]
        for i in range(degree_index + 1, min(block_end, degree_index + 3)):
            candidate = self._strip_bullet(lines[i])
            if self._looks_like_field_continuation(candidate):
                pieces.append(candidate)
            else:
                break

        value = self._clean_field(" ".join(pieces))
        value = self._remove_field_date_suffix(value)
        if self._is_invalid_field(value):
            return None
        return self._normalize_field(value)

    def _extract_field_of_study(self, line: str) -> Optional[str]:
        cleaned = self._clean_line(line)

        patterns = (
            r"\bin\s+(.+?)(?=\s*\(|,\s*|$)",
            r"\bmajor(?:ing)?\s+in\s+(.+?)(?=\s*\(|,\s*|$)",
            r":\s*(.+?)(?=\s*\(|,\s*|$)",
        )

        for pattern in patterns:
            match = re.search(pattern, cleaned, re.IGNORECASE)
            if not match:
                continue
            value = self._remove_field_date_suffix(
                self._clean_field(match.group(1))
            )
            if not self._is_invalid_field(value):
                return value

        parenthetical = re.search(r"\(([^)]{2,100})\)", cleaned)
        if parenthetical:
            value = parenthetical.group(1)
            value = re.sub(r"\bconcentration\s*:\s*", "", value, flags=re.IGNORECASE)
            value = re.sub(r"\bmajor\s*:\s*", "", value, flags=re.IGNORECASE)
            value = self._clean_field(value)
            if not self._is_invalid_field(value):
                return value

        return None

    def _looks_like_field_continuation(self, text: str) -> bool:
        value = self._clean_line(text)
        if not value or len(value.split()) > 4:
            return False
        if self._is_heading(value):
            return False
        if self._is_degree_line(value):
            return False
        if self._looks_like_gpa(value):
            return False
        if self._looks_like_status_text(value):
            return False
        if self._looks_like_location(value):
            return False
        if self._looks_like_date_or_year(value):
            return False
        if self._is_institution_candidate(value):
            return False
        return bool(re.fullmatch(r"[A-Za-z][A-Za-z &/'-]{1,40}", value))

    def _remove_field_date_suffix(self, value: str) -> str:
        month = (
            r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
            r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
            r"Nov(?:ember)?|Dec(?:ember)?)"
        )
        value = re.sub(
            rf",\s*{month}(?:\s+\d{{1,2}})?(?:,\s*|\s+)"
            rf"(?:19\d{{2}}|20\d{{2}}|(?:19|20)xx).*$",
            "",
            value,
            flags=re.IGNORECASE,
        )
        value = re.sub(
            r",\s*(?:19\d{2}|20\d{2}|(?:19|20)xx).*$",
            "",
            value,
            flags=re.IGNORECASE,
        )
        return self._clean_field(value)

    def _is_invalid_field(self, value: str) -> bool:
        if not value:
            return True
        lower = value.lower()
        if self._looks_like_status_text(value):
            return True
        if re.fullmatch(r"(?:19\d{2}|20\d{2}|(?:19|20)xx)", lower):
            return True
        if lower in {
            "may 20xx", "june 20xx", "expected", "expected graduation",
            "expected graduation date", "graduation date", "candidate",
        }:
            return True
        return False

    # -------------------------------------------------------------------------
    # Institution
    # -------------------------------------------------------------------------

    def _extract_institution_from_degree_line(self, line: str) -> Optional[str]:
        """Extract an institution that appears on the same line as a degree."""
        value = self._clean_line(line)
        match = re.search(
            r"(?:Ph\.?\s*D\.?|J\.?\s*D\.?|M\.?\s*B\.?\s*A\.?|M\.?\s*C\.?\s*A\.?|M\.?\s*S\.?|M\.?\s*A\.?|B\.?\s*B\.?\s*A\.?|B\.?\s*C\.?\s*A\.?|B\.?\s*S\.?|B\.?\s*A\.?|A\.?\s*S\.?)"
            r"\s+(?:in\s+[^|,]+\s+)?(?:[-:]\s*)?(.*)$",
            value,
            re.IGNORECASE,
        )
        if not match:
            return None
        tail = match.group(1).strip(" |,-")
        if self._is_institution_candidate(tail):
            return self._clean_institution_candidate(tail)
        return None

    def _find_institution(
        self,
        block: Sequence[str],
        degree_index_in_block: int,
    ) -> Optional[str]:
        keywords = ("university", "college", "institute", "school", "academy")
        candidates: List[Tuple[int, str]] = []

        for index, raw_line in enumerate(block):
            if index == degree_index_in_block:
                continue

            original = self._clean_line(self._strip_bullet(raw_line))
            lower = original.lower()

            if not original:
                continue
            if not any(k in lower for k in keywords):
                continue
            if self._is_degree_line(original):
                continue
            if self._looks_like_gpa(original):
                continue
            if self._looks_like_status_text(original):
                continue
            if self._looks_like_coursework(original):
                continue
            if self._looks_like_skill_line(original):
                continue
            if self._is_heading(original):
                continue
            if self._looks_like_date_or_year(original):
                continue

            value = self._clean_institution_candidate(original)
            if not value:
                continue

            score = 100 - abs(index - degree_index_in_block)
            if index > degree_index_in_block:
                score += 5
            if "university" in value.lower():
                score += 20
            if "college" in value.lower():
                score += 15
            if "school" in value.lower():
                score += 10
            if "law school" in value.lower():
                score += 20

            candidates.append((score, value))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    def _clean_institution_candidate(self, value: str) -> Optional[str]:
        value = self._clean_line(self._strip_bullet(value))
        if not value:
            return None
        if re.search(r"\s+[—–-]\s+", value):
            value = re.split(r"\s+[—–-]\s+", value, maxsplit=1)[0].strip()
        # Remove City, ST / ST / ZIP suffixes.
        value = re.sub(r",\s*[A-Za-z .'-]+,\s*[A-Z]{2}(?:\s+\d{5}(?:-\d{4})?)?$", "", value)
        value = re.sub(r",\s*[A-Z]{2}(?:\s+\d{5}(?:-\d{4})?)?$", "", value)
        return self._clean_line(value).strip(" ,;:-") or None

    # -------------------------------------------------------------------------
    # Graduation
    # -------------------------------------------------------------------------

    def _extract_graduation_year(
        self,
        block: Sequence[str],
    ) -> Tuple[Optional[str], Optional[int]]:
        # Explicit labels first.
        for i, line in enumerate(block):
            lower = line.lower()
            if not any(
                x in lower
                for x in (
                    "expected graduation",
                    "expected graduation date",
                    "graduation date",
                    "graduation:",
                    "graduated",
                    "expected",
                )
            ):
                continue

            m = re.search(r"\b(19\d{2}|20\d{2})\b", line)
            if m:
                return line, int(m.group(1))

            placeholder = re.search(r"\b(?:19|20)xx\b", line, re.IGNORECASE)
            if placeholder:
                if i + 1 < len(block):
                    nxt = block[i + 1]
                    if re.search(r"\b(?:19|20)xx\b", nxt, re.IGNORECASE):
                        return f"{line} {nxt}", None
                    if re.search(r"\b(?:19|20)xx\b", nxt, re.IGNORECASE):
                        return f"{line} {nxt}", None
                return line, None

            if i + 1 < len(block):
                nxt = block[i + 1]
                if re.search(r"\b(?:May|June|July|August|September|October|November|December|January|February|March|April)\s+(?:19|20)XX\b", nxt, re.IGNORECASE):
                    return f"{line} {nxt}".replace(": May", ": May"), None
                m2 = re.search(r"\b(19\d{2}|20\d{2})\b", nxt)
                if m2:
                    return f"{line} {nxt}", int(m2.group(1))
                if re.search(r"\b(?:19|20)xx\b", nxt, re.IGNORECASE):
                    return f"{line} {nxt}", None

        # Dates embedded on the degree line, e.g. June 2019.
        for line in block:
            if self._is_ambiguous_date_range(line):
                continue

            m = re.search(
                r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
                r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
                r"Nov(?:ember)?|Dec(?:ember)?)"
                r"(?:\s+\d{1,2})?(?:,\s*|\s+)"
                r"(19\d{2}|20\d{2})\b",
                line,
                re.IGNORECASE,
            )
            if m:
                return line, int(m.group(1))

        # Standalone year only.
        for line in block:
            if re.fullmatch(r"\s*(19\d{2}|20\d{2})\s*", line):
                return line, int(line.strip())

        # Placeholder if nothing more specific exists.
        for line in block:
            if re.search(r"\b(?:19|20)xx\b", line, re.IGNORECASE):
                return line, None

        return None, None

    def _is_ambiguous_date_range(self, text: str) -> bool:
        return bool(
            re.search(
                r"\b\d{1,2}/(?:19\d{2}|20\d{2})\s*[-–—]\s*"
                r"\d{1,2}/(?:19\d{2}|20\d{2})\b",
                text,
            )
            or re.search(
                r"\b(19\d{2}|20\d{2})\s*[-–—]\s*(19\d{2}|20\d{2})\b",
                text,
            )
        )

    # -------------------------------------------------------------------------
    # Certifications
    # -------------------------------------------------------------------------

    def parse_certifications(
        self,
        section_text: str,
    ) -> List[CertificationRecord]:
        if not section_text:
            return []

        records: List[CertificationRecord] = []
        for line in self._prepare_lines(section_text):
            value = self._strip_bullet(line)
            if not value:
                continue
            if self._is_heading(value):
                continue
            if self._is_generic_certification_name(value):
                continue
            if self._is_certification_false_positive(value):
                continue
            if not self._looks_like_certification(value):
                continue

            name, issuer = self._split_certification(value)
            year_text, year = self._extract_certification_year(value)
            normalized_name = self._normalize_certification_name(name)

            if self._is_generic_certification_name(normalized_name):
                continue
            if self._is_certification_false_positive(normalized_name):
                continue

            records.append(
                CertificationRecord(
                    name=name,
                    normalized_name=normalized_name,
                    issuer=issuer,
                    year=year,
                    year_text=year_text,
                    relevance_category=self._categorize_certification(normalized_name),
                    raw_text=value,
                )
            )

        return self._deduplicate_certifications(records)

    def _find_certification_lines_from_text(self, text: str) -> str:
        matches = []
        for line in self._prepare_lines(text):
            value = self._strip_bullet(line)
            if (
                value
                and not self._is_generic_certification_name(value)
                and not self._is_certification_false_positive(value)
                and self._looks_like_certification(value)
            ):
                matches.append(value)
        return "\n".join(matches)

    def _is_generic_certification_name(self, value: str) -> bool:
        normalized = self._normalize_heading(value)
        generic = {self._normalize_heading(x) for x in self.GENERIC_CERTIFICATION_TEXT}
        return normalized in generic

    def _is_certification_false_positive(self, value: str) -> bool:
        normalized = self._normalize_heading(value)
        false_positives = {self._normalize_heading(x) for x in self.CERTIFICATION_FALSE_POSITIVES}
        return normalized in false_positives

    def _looks_like_certification(self, text: str) -> bool:
        value = self._clean_line(text)
        lower = value.lower()

        if not value:
            return False
        if self._is_generic_certification_name(value):
            return False
        if self._is_certification_false_positive(value):
            return False

        if any(x in lower for x in self.CERTIFICATION_HINTS):
            return len(re.findall(r"[A-Za-z0-9+#.-]+", value)) >= 2

        prefixes = (
            "aws certified ", "aws cloud ", "microsoft certified ",
            "google certified ", "google cloud ", "oracle certified ",
            "cisco certified ", "comptia ", "pmp ", "cfa ", "acca ", "cpa ",
        )
        return lower.startswith(prefixes)

    def _split_certification(self, text: str) -> Tuple[str, Optional[str]]:
        for separator in (
            r"\s+-\s+", r"\s+–\s+", r"\s+—\s+", r"\s+\|\s+",
        ):
            parts = re.split(separator, text, maxsplit=1)
            if len(parts) == 2 and self._looks_like_issuer(parts[1].strip()):
                return parts[0].strip(), parts[1].strip()
        return text, None

    def _looks_like_issuer(self, text: str) -> bool:
        lower = text.lower()
        return any(
            x in lower
            for x in (
                "amazon web services", "aws", "microsoft", "google", "oracle",
                "cisco", "comptia", "institute", "university", "college",
                "academy", "association", "organization", "board", "pmi",
            )
        )

    def _extract_certification_year(self, text: str) -> Tuple[Optional[str], Optional[int]]:
        m = re.search(r"\b(19\d{2}|20\d{2})\b", text)
        if m:
            return m.group(1), int(m.group(1))
        p = re.search(r"\b(?:19|20)xx\b", text, re.IGNORECASE)
        if p:
            return p.group(0), None
        return None, None

    # -------------------------------------------------------------------------
    # Normalization / profile
    # -------------------------------------------------------------------------

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
            "data analytics": "Data Analytics",
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
        value = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", value)
        mapping = {
            "aws certified cloud practitioner": "AWS Certified Cloud Practitioner",
            "aws cloud practitioner": "AWS Certified Cloud Practitioner",
            "microsoft certified azure fundamentals": "Microsoft Azure Fundamentals",
            "azure fundamentals": "Microsoft Azure Fundamentals",
            "google cloud digital leader": "Google Cloud Digital Leader",
            "google data analytics certificate": "Google Data Analytics Certificate",
            "comptia security+": "CompTIA Security+",
            "pmp": "Project Management Professional (PMP)",
        }
        return mapping.get(value.lower(), value)

    def _categorize_certification(self, name: Optional[str]) -> str:
        if not name:
            return "general"
        lower = name.lower()
        scores = {}
        for category, keywords in self.CERTIFICATION_CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in lower)
            if score:
                scores[category] = score
        return max(scores, key=scores.get) if scores else "general"

    def build_profile(
        self,
        education: List[EducationRecord],
        certifications: List[CertificationRecord],
    ) -> AcademicProfile:
        ranking = {
            "none": 0,
            "certificate": 0,
            "diploma": 1,
            "associate": 2,
            "bachelors": 3,
            "masters": 4,
            "doctorate": 5,
        }

        highest = None
        highest_level = "none"
        for record in education:
            level = self._degree_level(record.degree_type)
            if ranking.get(level, 0) > ranking.get(highest_level, 0):
                highest = record
                highest_level = level

        fields = self._unique_values(
            record.normalized_field for record in education if record.normalized_field
        )
        institutions = self._unique_values(
            record.institution for record in education if record.institution
        )

        categories: Dict[str, List[str]] = {}
        for cert in certifications:
            if cert.normalized_name:
                categories.setdefault(cert.relevance_category, []).append(
                    cert.normalized_name
                )
        for category in categories:
            categories[category] = self._unique_values(categories[category])

        return AcademicProfile(
            education=education,
            certifications=certifications,
            highest_degree=highest.degree_type if highest else None,
            highest_degree_level=highest_level if highest else None,
            fields_of_study=fields,
            institutions=institutions,
            certification_categories=categories,
        )

    # -------------------------------------------------------------------------
    # Generic helpers
    # -------------------------------------------------------------------------

    def _prepare_lines(self, text: str) -> List[str]:
        if not text:
            return []
        result = []
        for raw in re.split(r"\r?\n|\s*\|\s*", text):
            cleaned = self._clean_line(raw)
            if cleaned:
                result.append(cleaned)
        return result

    def _clean_line(self, value: str) -> str:
        value = value.replace("\xa0", " ").replace("\u200b", "")
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    def _clean_field(self, value: str) -> str:
        return self._clean_line(value).strip(" .,:;-")

    def _strip_bullet(self, value: str) -> str:
        return re.sub(r"^[\u2022\u25cf\u25a0\u25aa\-*]+\s*", "", value).strip()

    def _normalize_heading(self, value: str) -> str:
        value = self._clean_line(value).lower().replace("&", "and")
        value = re.sub(r"[^a-z0-9\s]", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    def _is_heading(self, text: str) -> bool:
        normalized = self._normalize_heading(text)
        headings = {
            self._normalize_heading(x)
            for x in (
                self.EDUCATION_HEADINGS
                | self.CERTIFICATION_HEADINGS
                | self.STOP_HEADINGS
            )
        }
        return normalized in headings

    def _looks_like_gpa(self, text: str) -> bool:
        return bool(re.search(r"\bgpa\b", text, re.IGNORECASE))

    def _looks_like_status_text(self, text: str) -> bool:
        lower = text.lower()
        return any(
            x in lower
            for x in (
                "expected graduation", "graduation date", "graduated",
                "summa cum laude", "magna cum laude", "cum laude",
                "in progress", "candidate", "honors", "expected",
            )
        )

    def _looks_like_coursework(self, text: str) -> bool:
        lower = text.lower()
        return lower.startswith("relevant coursework") or lower.startswith("coursework")

    def _looks_like_skill_line(self, text: str) -> bool:
        lower = text.lower()
        return lower.startswith(
            (
                "programming languages:", "programming language:",
                "software development tools:", "software development tool:",
                "web development:", "technical skills:", "technical skill:",
                "skills:", "tools:", "technologies:", "technology:",
            )
        )

    def _looks_like_contact(self, text: str) -> bool:
        return (
            "@" in text
            or bool(re.search(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b", text))
            or "linkedin.com" in text.lower()
        )

    def _looks_like_location(self, text: str) -> bool:
        return bool(
            re.search(
                r",\s*[A-Z]{2}(?:\s+\d{5}(?:-\d{4})?)?$",
                self._clean_line(text),
            )
        )

    def _looks_like_date_or_year(self, text: str) -> bool:
        value = self._clean_line(text)
        return bool(
            re.fullmatch(r"\s*(19\d{2}|20\d{2})\s*", value)
            or re.fullmatch(r"\s*(?:19|20)xx\s*", value, re.IGNORECASE)
            or re.fullmatch(r"\s*\d{1,2}/(?:19\d{2}|20\d{2})\s*", value)
            or re.fullmatch(
                r"\s*\d{1,2}/(?:19\d{2}|20\d{2})\s*[-–—]\s*"
                r"\d{1,2}/(?:19\d{2}|20\d{2})\s*",
                value,
            )
        )

    def _is_institution_candidate(self, text: str) -> bool:
        lower = text.lower()
        return any(x in lower for x in ("university", "college", "institute", "school", "academy"))

    def _extract_location(self, block: Sequence[str]) -> Optional[str]:
        location_re = re.compile(r"\b([A-Za-z][A-Za-z .'-]+,\s*[A-Z]{2}(?:\s+\d{5}(?:-\d{4})?)?)\b")
        for line in block:
            matches = location_re.findall(line)
            if matches:
                return matches[-1].strip()
        return None

    def _unique_values(self, values: Iterable[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            clean = self._clean_line(value)
            if clean and clean.lower() not in seen:
                seen.add(clean.lower())
                result.append(clean)
        return result

    def _deduplicate_education(self, records: List[EducationRecord]) -> List[EducationRecord]:
        result = []
        seen = set()
        for record in records:
            key = (
                (record.degree_type or "").lower(),
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
        result = []
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
# Convenience function
# =============================================================================


def parse_education_certifications(
    text: str,
    sections: Optional[Dict[str, str]] = None,
) -> Dict:
    parser = EducationCertificationParser()
    return parser.to_dict(parser.parse(text, sections))


# =============================================================================
# Manual test
# =============================================================================


if __name__ == "__main__":
    sample_text = """
    EDUCATION
    Texas Tech University
    Bachelor of Business Administration in Finance (in progress)
    GPA: 3.9/4.0
    Lubbock, TX
    Expected graduation:
    May 20XX

    CERTIFICATIONS
    AWS Certified Cloud Practitioner - Amazon Web Services
    Project Management Professional (PMP) - PMI
    """

    parser = EducationCertificationParser()
    profile = parser.parse(sample_text)

    print("\n=== EDUCATION ===")
    for record in profile.education:
        print(asdict(record))

    print("\n=== CERTIFICATIONS ===")
    for record in profile.certifications:
        print(asdict(record))

    print("\n=== ACADEMIC PROFILE ===")
    print(asdict(profile))
