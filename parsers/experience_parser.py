from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class ExperienceParser:
    """
    Day 10 - Resume Experience Parser

    Supported structures:

        TITLE
        DATE
        COMPANY

        DATE
        TITLE
        COMPANY

        DATE
        COMPANY
        TITLE

        COMPANY
        TITLE

        COMPANY
        RESPONSIBILITY

    The parser never invents missing years, titles, or dates.
    """

    EXPERIENCE_HEADINGS = {
        "experience",
        "work experience",
        "professional experience",
        "relevant experience",
        "employment",
        "employment history",
        "work history",
        "career history",
        "professional history",
    }

    OTHER_HEADINGS = {
        "education",
        "skills",
        "key skills",
        "technical skills",
        "additional skills",
        "certifications",
        "projects",
        "personal information",
        "contact",
        "objective",
        "resume objective",
        "summary",
        "profile",
        "awards",
        "achievements",
        "languages",
        "interests",
        "hobbies",
        "references",
        "additional information",
    }

    ALL_HEADINGS = EXPERIENCE_HEADINGS | OTHER_HEADINGS

    MONTHS = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }

    MONTH_PATTERN = (
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
    )

    TITLE_KEYWORDS = (
        "intern",
        "developer",
        "engineer",
        "designer",
        "analyst",
        "scientist",
        "manager",
        "assistant",
        "associate",
        "specialist",
        "administrator",
        "consultant",
        "coordinator",
        "officer",
        "director",
        "architect",
        "lead",
        "president",
        "volunteer",
        "researcher",
        "accountant",
        "writer",
        "strategist",
        "executive",
        "marketing",
        "programmer",
        "technician",
        "developer",
    )

    ACTION_WORDS = (
        "developed",
        "develop",
        "created",
        "creating",
        "worked",
        "collaborated",
        "assisted",
        "participated",
        "conducted",
        "prepared",
        "contributed",
        "implemented",
        "researched",
        "identified",
        "designed",
        "managed",
        "increased",
        "reduced",
        "resulting",
        "leading",
        "using",
        "built",
        "build",
        "supported",
        "maintained",
        "performed",
        "reconciled",
        "educated",
        "represented",
        "co-developed",
    )

    # ======================================================================
    # BASIC HELPERS
    # ======================================================================

    @staticmethod
    def normalize_line(value: Any) -> str:
        text = str(value)

        text = text.replace("\u2014", "–")
        text = text.replace("\u2212", "-")
        text = text.replace("\xa0", " ")

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    @staticmethod
    def key(value: Any) -> str:
        text = ExperienceParser.normalize_line(value)

        text = re.sub(
            r"[^a-zA-Z ]",
            " ",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip().lower()

    # ======================================================================
    # HEADINGS
    # ======================================================================

    def is_heading(self, line: str) -> bool:
        value = self.key(line)

        return value in {
            self.key(item)
            for item in self.ALL_HEADINGS
        }

    def is_experience_heading(self, line: str) -> bool:
        value = self.key(line)

        return value in {
            self.key(item)
            for item in self.EXPERIENCE_HEADINGS
        }

    # ======================================================================
    # DATE DETECTION
    # ======================================================================

    def is_date_line(self, line: str) -> bool:
        """
        Recognizes the actual date styles present in the resume set.
        """

        text = self.normalize_line(line)

        patterns = [

            # May 20xx – September 20xx
            rf"^{self.MONTH_PATTERN}\s+20xx\s*"
            rf"(?:-|–|to)\s*"
            rf"{self.MONTH_PATTERN}\s+20xx$",

            # May – September 20xx
            rf"^{self.MONTH_PATTERN}\s*"
            rf"(?:-|–|to)\s*"
            rf"{self.MONTH_PATTERN}\s+20xx$",

            # September 20xx – Present
            rf"^{self.MONTH_PATTERN}\s+20xx\s*"
            rf"(?:-|–|to)\s*present$",

            # May 2020 – September 2021
            rf"^{self.MONTH_PATTERN}\s+"
            r"(?:19|20)\d{2}\s*"
            rf"(?:-|–|to)\s*"
            rf"{self.MONTH_PATTERN}\s+"
            r"(?:19|20)\d{2}$",

            # May 2020 – Present
            rf"^{self.MONTH_PATTERN}\s+"
            r"(?:19|20)\d{2}\s*"
            rf"(?:-|–|to)\s*present$",

            # 2020 – 2024
            r"^(?:19|20)\d{2}\s*"
            r"(?:-|–|to)\s*"
            r"(?:19|20)\d{2}$",

            # 2020 – Present
            r"^(?:19|20)\d{2}\s*"
            r"(?:-|–|to)\s*present$",

            # Summer 20XX
            r"^summer\s+20xx$",

            # Summer 2020
            r"^summer\s+(?:19|20)\d{2}$",

            # May 2020
            rf"^{self.MONTH_PATTERN}\s+"
            r"(?:19|20)\d{2}$",

            # 2020
            r"^(?:19|20)\d{2}$",
        ]

        return any(
            re.fullmatch(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
            for pattern in patterns
        )

    # ======================================================================
    # DATE PARSING
    # ======================================================================

    def parse_date_range(
        self,
        line: str,
    ) -> Dict[str, Any]:

        text = self.normalize_line(line)

        result = {
            "start_date": None,
            "end_date": None,
            "start_date_text": None,
            "end_date_text": None,
            "date_precision": "unknown",
        }

        # --------------------------------------------------------------
        # May 20xx – September 20xx
        # --------------------------------------------------------------
        match = re.fullmatch(
            rf"({self.MONTH_PATTERN})\s+20xx\s*"
            rf"(?:-|–|to)\s*"
            rf"({self.MONTH_PATTERN})\s+20xx",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            result["start_date_text"] = (
                f"{match.group(1)} 20xx"
            )
            result["end_date_text"] = (
                f"{match.group(2)} 20xx"
            )
            result["date_precision"] = "placeholder"

            return result

        # --------------------------------------------------------------
        # June – September 20XX
        # --------------------------------------------------------------
        match = re.fullmatch(
            rf"({self.MONTH_PATTERN})\s*"
            rf"(?:-|–|to)\s*"
            rf"({self.MONTH_PATTERN})\s+20xx",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            result["start_date_text"] = (
                match.group(1)
            )
            result["end_date_text"] = (
                f"{match.group(2)} 20xx"
            )
            result["date_precision"] = "placeholder"

            return result

        # --------------------------------------------------------------
        # September 20XX – Present
        # --------------------------------------------------------------
        match = re.fullmatch(
            rf"({self.MONTH_PATTERN})\s+20xx\s*"
            rf"(?:-|–|to)\s*present",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            result["start_date_text"] = (
                f"{match.group(1)} 20xx"
            )
            result["end_date_text"] = "Present"
            result["date_precision"] = "placeholder"

            return result

        # --------------------------------------------------------------
        # Month YYYY – Month YYYY
        # --------------------------------------------------------------
        match = re.fullmatch(
            rf"({self.MONTH_PATTERN})\s+"
            r"((?:19|20)\d{2})\s*"
            rf"(?:-|–|to)\s*"
            rf"({self.MONTH_PATTERN})\s+"
            r"((?:19|20)\d{2})",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            start_month = match.group(1).lower()
            start_year = int(match.group(2))

            end_month = match.group(3).lower()
            end_year = int(match.group(4))

            result["start_date"] = datetime(
                start_year,
                self.MONTHS[start_month],
                1,
            )

            result["end_date"] = datetime(
                end_year,
                self.MONTHS[end_month],
                1,
            )

            result["start_date_text"] = (
                f"{match.group(1)} {match.group(2)}"
            )

            result["end_date_text"] = (
                f"{match.group(3)} {match.group(4)}"
            )

            result["date_precision"] = "exact_month"

            return result

        # --------------------------------------------------------------
        # Month YYYY – Present
        # --------------------------------------------------------------
        match = re.fullmatch(
            rf"({self.MONTH_PATTERN})\s+"
            r"((?:19|20)\d{2})\s*"
            rf"(?:-|–|to)\s*present",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            result["start_date"] = datetime(
                int(match.group(2)),
                self.MONTHS[
                    match.group(1).lower()
                ],
                1,
            )

            result["start_date_text"] = (
                f"{match.group(1)} {match.group(2)}"
            )

            result["end_date_text"] = "Present"
            result["date_precision"] = "exact_month"

            return result

        # --------------------------------------------------------------
        # YYYY – YYYY
        # --------------------------------------------------------------
        match = re.fullmatch(
            r"((?:19|20)\d{2})\s*"
            r"(?:-|–|to)\s*"
            r"((?:19|20)\d{2})",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            result["start_date"] = datetime(
                int(match.group(1)),
                1,
                1,
            )

            result["end_date"] = datetime(
                int(match.group(2)),
                12,
                1,
            )

            result["start_date_text"] = match.group(1)
            result["end_date_text"] = match.group(2)
            result["date_precision"] = "exact_year"

            return result

        # --------------------------------------------------------------
        # YYYY – Present
        # --------------------------------------------------------------
        match = re.fullmatch(
            r"((?:19|20)\d{2})\s*"
            r"(?:-|–|to)\s*present",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            result["start_date"] = datetime(
                int(match.group(1)),
                1,
                1,
            )

            result["start_date_text"] = match.group(1)
            result["end_date_text"] = "Present"
            result["date_precision"] = "exact_year"

            return result

        # --------------------------------------------------------------
        # Summer 20XX
        # --------------------------------------------------------------
        if re.fullmatch(
            r"summer\s+20xx",
            text,
            flags=re.IGNORECASE,
        ):
            result["start_date_text"] = text
            result["date_precision"] = "placeholder"

            return result

        # --------------------------------------------------------------
        # Summer 2020
        # --------------------------------------------------------------
        match = re.fullmatch(
            r"summer\s+((?:19|20)\d{2})",
            text,
            flags=re.IGNORECASE,
        )

        if match:
            result["start_date"] = datetime(
                int(match.group(1)),
                6,
                1,
            )

            result["start_date_text"] = text
            result["date_precision"] = "exact_year"

            return result

        return result

    # ======================================================================
    # TITLE DETECTION
    # ======================================================================

    def looks_like_title(
        self,
        line: str,
    ) -> bool:

        text = self.normalize_line(line)

        if not text:
            return False

        if len(text) > 100:
            return False

        if self.is_heading(text):
            return False

        if self.is_date_line(text):
            return False

        lower = text.lower()

        # Responsibilities are usually action-led.
        if any(
            lower.startswith(word)
            for word in self.ACTION_WORDS
        ):
            return False

        # A location is not a title.
        if re.fullmatch(
            r"[A-Za-z .'-]+,\s*[A-Z]{2}",
            text,
        ):
            return False

        # A strong title keyword is enough.
        return any(
            keyword in lower
            for keyword in self.TITLE_KEYWORDS
        )

    # ======================================================================
    # COMPANY DETECTION
    # ======================================================================

    def looks_like_company(
        self,
        line: str,
    ) -> bool:

        text = self.normalize_line(line)

        if not text:
            return False

        if len(text) > 120:
            return False

        if self.is_heading(text):
            return False

        if self.is_date_line(text):
            return False

        lower = text.lower()

        if any(
            lower.startswith(word)
            for word in self.ACTION_WORDS
        ):
            return False

        # Pure location.
        if re.fullmatch(
            r"[A-Za-z .'-]+,\s*[A-Z]{2}",
            text,
        ):
            return False

        indicators = (
            "inc",
            "corp",
            "corporation",
            "company",
            "co.",
            "llc",
            "ltd",
            "systems",
            "solutions",
            "technologies",
            "university",
            "college",
            "agency",
            "group",
            "organization",
            "society",
            "institute",
        )

        if any(
            indicator in lower
            for indicator in indicators
        ):
            return True

        # Company - City, ST
        if re.search(
            r"[–-]\s*[A-Za-z .'-]+,\s*[A-Z]{2}$",
            text,
        ):
            return True

        return False

    # ======================================================================
    # COMPANY / LOCATION
    # ======================================================================

    def split_company_location(
        self,
        line: str,
    ) -> Tuple[str, Optional[str]]:

        text = self.normalize_line(line)

        # Company – City, ST
        match = re.fullmatch(
            r"(.*?)\s*[–-]\s*"
            r"([A-Za-z .'-]+,\s*[A-Z]{2})",
            text,
        )

        if match:
            return (
                match.group(1).strip(),
                match.group(2).strip(),
            )

        # Company, City, ST
        match = re.fullmatch(
            r"(.*?),\s*"
            r"([A-Za-z .'-]+,\s*[A-Z]{2})",
            text,
        )

        if match:
            return (
                match.group(1).strip(),
                match.group(2).strip(),
            )

        return text, None

    # ======================================================================
    # EXPERIENCE SECTION
    # ======================================================================

    def extract_experience_lines(
        self,
        text: str,
    ) -> List[str]:

        lines = [
            self.normalize_line(line)
            for line in text.splitlines()
            if self.normalize_line(line)
        ]

        start = None

        for index, line in enumerate(lines):

            if self.is_experience_heading(line):

                start = index + 1
                break

        if start is None:
            return []

        result = []

        for line in lines[start:]:

            if self.is_heading(line):
                break

            result.append(line)

        return result

    # ======================================================================
    # RESPONSIBILITIES
    # ======================================================================

    def collect_responsibilities(
        self,
        lines: List[str],
        start_index: int,
    ) -> Tuple[List[str], int]:
        """
        Collect responsibility lines until the next clear role boundary.
        """

        responsibilities: List[str] = []

        index = start_index

        while index < len(lines):

            line = self.normalize_line(
                lines[index]
            )

            if not line:
                index += 1
                continue

            # ----------------------------------------------------------
            # DATE = next role.
            # ----------------------------------------------------------
            if self.is_date_line(line):
                break

            # ----------------------------------------------------------
            # SECTION = stop.
            # ----------------------------------------------------------
            if self.is_heading(line):
                break

            # ----------------------------------------------------------
            # TITLE followed by DATE = next role.
            # ----------------------------------------------------------
            if self.looks_like_title(line):

                if (
                    index + 1 < len(lines)
                    and self.is_date_line(
                        lines[index + 1]
                    )
                ):
                    break

            # ----------------------------------------------------------
            # COMPANY followed by TITLE = next role.
            # ----------------------------------------------------------
            if self.looks_like_company(line):

                if index + 1 < len(lines):

                    next_line = self.normalize_line(
                        lines[index + 1]
                    )

                    if self.looks_like_title(
                        next_line
                    ):
                        break

                    # Company followed by an action sentence.
                    #
                    # This is the incomplete Pineapple Systems case.
                    if any(
                        next_line.lower().startswith(
                            word
                        )
                        for word in self.ACTION_WORDS
                    ):
                        break

            responsibilities.append(line)

            index += 1

        return responsibilities, index

    # ======================================================================
    # RECORD FACTORY
    # ======================================================================

    def make_record(
        self,
        title: Optional[str],
        company: Optional[str],
        location: Optional[str],
        date_info: Dict[str, Any],
        responsibilities: List[str],
    ) -> Dict[str, Any]:

        start = date_info.get(
            "start_date"
        )

        end = date_info.get(
            "end_date"
        )

        duration = None

        if start is not None and end is not None:

            if end >= start:

                duration = max(
                    1,
                    (
                        (end.year - start.year) * 12
                        + (end.month - start.month)
                        + 1
                    ),
                )

        return {
            "job_title": title,
            "company": company,
            "location": location,
            "start_date": start,
            "end_date": end,
            "start_date_text": date_info.get(
                "start_date_text"
            ),
            "end_date_text": date_info.get(
                "end_date_text"
            ),
            "date_precision": date_info.get(
                "date_precision",
                "unknown",
            ),
            "duration_months": duration,
            "responsibilities": responsibilities,
        }

    # ======================================================================
    # MAIN STRUCTURAL PARSER
    # ======================================================================

    def parse_records(
        self,
        lines: List[str],
    ) -> List[Dict[str, Any]]:

        records: List[Dict[str, Any]] = []

        index = 0

        while index < len(lines):

            line = self.normalize_line(
                lines[index]
            )

            # ==========================================================
            # CASE 1
            #
            # TITLE
            # DATE
            # COMPANY
            #
            # Marketing
            # ==========================================================

            if self.looks_like_title(line):

                if (
                    index + 2 < len(lines)
                    and self.is_date_line(
                        lines[index + 1]
                    )
                ):

                    company_line = self.normalize_line(
                        lines[index + 2]
                    )

                    # The company is contextual here. It does not need
                    # to pass the generic company heuristic.
                    if (
                        not self.is_date_line(
                            company_line
                        )
                        and not self.is_heading(
                            company_line
                        )
                        and not any(
                            company_line.lower().startswith(
                                word
                            )
                            for word in self.ACTION_WORDS
                        )
                    ):

                        date_info = self.parse_date_range(
                            lines[index + 1]
                        )

                        company, location = (
                            self.split_company_location(
                                company_line
                            )
                        )

                        # A standalone location following the company.
                        if (
                            location is None
                            and index + 3 < len(lines)
                        ):

                            possible_location = (
                                self.normalize_line(
                                    lines[index + 3]
                                )
                            )

                            if re.fullmatch(
                                r"[A-Za-z .'-]+,\s*[A-Z]{2}",
                                possible_location,
                            ):

                                location = (
                                    possible_location
                                )

                                responsibility_start = (
                                    index + 4
                                )

                            else:

                                responsibility_start = (
                                    index + 3
                                )

                        else:

                            responsibility_start = (
                                index + 3
                            )

                        responsibilities, next_index = (
                            self.collect_responsibilities(
                                lines,
                                responsibility_start,
                            )
                        )

                        records.append(
                            self.make_record(
                                line,
                                company,
                                location,
                                date_info,
                                responsibilities,
                            )
                        )

                        index = next_index
                        continue

            # ==========================================================
            # CASE 2
            #
            # DATE
            # TITLE
            # COMPANY
            #
            # Tax
            # ==========================================================

            if self.is_date_line(line):

                date_info = self.parse_date_range(
                    line
                )

                if (
                    index + 2 < len(lines)
                    and self.looks_like_title(
                        lines[index + 1]
                    )
                ):

                    title = self.normalize_line(
                        lines[index + 1]
                    )

                    company_line = self.normalize_line(
                        lines[index + 2]
                    )

                    if (
                        not self.is_date_line(
                            company_line
                        )
                        and not self.is_heading(
                            company_line
                        )
                    ):

                        company, location = (
                            self.split_company_location(
                                company_line
                            )
                        )

                        responsibility_start = (
                            index + 3
                        )

                        # Standalone location after company.
                        if (
                            location is None
                            and responsibility_start
                            < len(lines)
                        ):

                            possible_location = (
                                self.normalize_line(
                                    lines[
                                        responsibility_start
                                    ]
                                )
                            )

                            if re.fullmatch(
                                r"[A-Za-z .'-]+,\s*[A-Z]{2}",
                                possible_location,
                            ):

                                location = (
                                    possible_location
                                )

                                responsibility_start += 1

                        responsibilities, next_index = (
                            self.collect_responsibilities(
                                lines,
                                responsibility_start,
                            )
                        )

                        records.append(
                            self.make_record(
                                title,
                                company,
                                location,
                                date_info,
                                responsibilities,
                            )
                        )

                        index = next_index
                        continue

                # ======================================================
                # DATE -> COMPANY -> TITLE
                #
                # Software
                # ======================================================

                if (
                    index + 2 < len(lines)
                    and not self.is_date_line(
                        lines[index + 1]
                    )
                    and not self.is_heading(
                        lines[index + 1]
                    )
                    and self.looks_like_title(
                        lines[index + 2]
                    )
                ):

                    company_line = self.normalize_line(
                        lines[index + 1]
                    )

                    title = self.normalize_line(
                        lines[index + 2]
                    )

                    company, location = (
                        self.split_company_location(
                            company_line
                        )
                    )

                    responsibility_start = (
                        index + 3
                    )

                    # If company did not include location,
                    # inspect the following line.
                    if (
                        location is None
                        and responsibility_start
                        < len(lines)
                    ):

                        possible_location = (
                            self.normalize_line(
                                lines[
                                    responsibility_start
                                ]
                            )
                        )

                        if re.fullmatch(
                            r"[A-Za-z .'-]+,\s*[A-Z]{2}",
                            possible_location,
                        ):

                            location = possible_location
                            responsibility_start += 1

                    responsibilities, next_index = (
                        self.collect_responsibilities(
                            lines,
                            responsibility_start,
                        )
                    )

                    records.append(
                        self.make_record(
                            title,
                            company,
                            location,
                            date_info,
                            responsibilities,
                        )
                    )

                    index = next_index
                    continue

            # ==========================================================
            # CASE 3
            #
            # COMPANY
            # TITLE
            #
            # Date missing.
            # ==========================================================

            if self.looks_like_company(line):

                if (
                    index + 1 < len(lines)
                    and self.looks_like_title(
                        lines[index + 1]
                    )
                ):

                    company, location = (
                        self.split_company_location(
                            line
                        )
                    )

                    empty_date = {
                        "start_date": None,
                        "end_date": None,
                        "start_date_text": None,
                        "end_date_text": None,
                        "date_precision": "unknown",
                    }

                    responsibilities, next_index = (
                        self.collect_responsibilities(
                            lines,
                            index + 2,
                        )
                    )

                    records.append(
                        self.make_record(
                            lines[index + 1],
                            company,
                            location,
                            empty_date,
                            responsibilities,
                        )
                    )

                    index = next_index
                    continue

            # ==========================================================
            # CASE 4
            #
            # COMPANY
            # RESPONSIBILITY
            #
            # Title/date missing.
            #
            # Software second role.
            # ==========================================================

            if self.looks_like_company(line):

                if index + 1 < len(lines):

                    next_line = self.normalize_line(
                        lines[index + 1]
                    )

                    if any(
                        next_line.lower().startswith(
                            word
                        )
                        for word in self.ACTION_WORDS
                    ):

                        company, location = (
                            self.split_company_location(
                                line
                            )
                        )

                        empty_date = {
                            "start_date": None,
                            "end_date": None,
                            "start_date_text": None,
                            "end_date_text": None,
                            "date_precision": "unknown",
                        }

                        responsibilities, next_index = (
                            self.collect_responsibilities(
                                lines,
                                index + 1,
                            )
                        )

                        records.append(
                            self.make_record(
                                None,
                                company,
                                location,
                                empty_date,
                                responsibilities,
                            )
                        )

                        index = next_index
                        continue

            index += 1

        return records

    # ======================================================================
    # DEDUPLICATION
    # ======================================================================

    def deduplicate_records(
        self,
        records: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        result = []
        seen = set()

        for record in records:

            key = (
                self.key(
                    record.get(
                        "job_title",
                        "",
                    )
                    or ""
                ),
                self.key(
                    record.get(
                        "company",
                        "",
                    )
                    or ""
                ),
                self.key(
                    record.get(
                        "start_date_text",
                        "",
                    )
                    or ""
                ),
                self.key(
                    record.get(
                        "end_date_text",
                        "",
                    )
                    or ""
                ),
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(record)

        return result

    # ======================================================================
    # GAPS
    # ======================================================================

    def detect_gaps(
        self,
        records: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        dated = [
            record
            for record in records
            if record.get("start_date") is not None
            and record.get("end_date") is not None
        ]

        dated.sort(
            key=lambda record: record["start_date"]
        )

        gaps = []

        for first, second in zip(
            dated,
            dated[1:],
        ):

            if second["start_date"] > first["end_date"]:

                months = (
                    (
                        second["start_date"].year
                        - first["end_date"].year
                    ) * 12
                    + (
                        second["start_date"].month
                        - first["end_date"].month
                    )
                    - 1
                )

                if months > 0:

                    gaps.append(
                        {
                            "from": first["end_date"],
                            "to": second["start_date"],
                            "months": months,
                        }
                    )

        return gaps

    # ======================================================================
    # OVERLAPS
    # ======================================================================

    def detect_overlaps(
        self,
        records: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        dated = [
            record
            for record in records
            if record.get("start_date") is not None
            and record.get("end_date") is not None
        ]

        dated.sort(
            key=lambda record: record["start_date"]
        )

        overlaps = []

        for i in range(len(dated)):

            for j in range(i + 1, len(dated)):

                first = dated[i]
                second = dated[j]

                if (
                    second["start_date"]
                    <= first["end_date"]
                ):

                    overlaps.append(
                        {
                            "experience_1": (
                                first["job_title"]
                            ),
                            "experience_2": (
                                second["job_title"]
                            ),
                            "from": second["start_date"],
                            "to": min(
                                first["end_date"],
                                second["end_date"],
                            ),
                        }
                    )

        return overlaps

    # ======================================================================
    # TOTAL EXPERIENCE
    # ======================================================================

    def calculate_total_experience(
        self,
        records: List[Dict[str, Any]],
    ) -> int:

        intervals = []

        for record in records:

            start = record.get(
                "start_date"
            )

            end = record.get(
                "end_date"
            )

            if start is None or end is None:
                continue

            if end < start:
                continue

            intervals.append(
                (start, end)
            )

        if not intervals:
            return 0

        intervals.sort(
            key=lambda item: item[0]
        )

        merged: List[List[datetime]] = []

        for start, end in intervals:

            if not merged:

                merged.append(
                    [start, end]
                )

                continue

            previous_start, previous_end = (
                merged[-1]
            )

            if start <= previous_end:

                if end > previous_end:
                    merged[-1][1] = end

            else:

                merged.append(
                    [start, end]
                )

        total = 0

        for start, end in merged:

            total += (
                (end.year - start.year) * 12
                + (end.month - start.month)
                + 1
            )

        return total

    # ======================================================================
    # PUBLIC API
    # ======================================================================

    def parse_experience(
        self,
        text_or_sections: Any,
    ) -> Dict[str, Any]:

        if isinstance(
            text_or_sections,
            dict,
        ):

            parts: List[str] = []

            for section_name, content in (
                text_or_sections.items()
            ):

                section_key = self.key(
                    section_name
                )

                if (
                    section_key in {
                        "work experience",
                        "professional experience",
                        "relevant experience",
                        "experience",
                    }
                    or "experience" in section_key
                ):

                    if isinstance(
                        content,
                        list,
                    ):

                        parts.extend(
                            str(value)
                            for value in content
                        )

                    else:

                        parts.append(
                            str(content)
                        )

            text = "\n".join(parts)

        else:

            text = str(
                text_or_sections
            )

        lines = self.extract_experience_lines(
            text
        )

        records = self.parse_records(
            lines
        )

        records = self.deduplicate_records(
            records
        )

        total_months = (
            self.calculate_total_experience(
                records
            )
        )

        return {
            "experiences": records,
            "total_experience_months": total_months,
            "total_experience_years": round(
                total_months / 12,
                2,
            ),
            "gaps": self.detect_gaps(
                records
            ),
            "overlaps": self.detect_overlaps(
                records
            ),
        }


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def parse_experience(
    text_or_sections: Any,
) -> Dict[str, Any]:

    return ExperienceParser().parse_experience(
        text_or_sections
    )


# ============================================================================
# CLI OUTPUT
# ============================================================================

def print_results(
    result: Dict[str, Any],
) -> None:

    experiences = result.get(
        "experiences",
        [],
    )

    print("\n" + "=" * 70)
    print("DAY 10 EXPERIENCE PARSER")
    print("=" * 70)

    print(
        f"\nExperience records found: "
        f"{len(experiences)}"
    )

    for index, experience in enumerate(
        experiences,
        start=1,
    ):

        print("\n" + "-" * 70)
        print(f"EXPERIENCE {index}")
        print("-" * 70)

        print(
            f"Job Title : "
            f"{experience.get('job_title')}"
        )

        print(
            f"Company   : "
            f"{experience.get('company')}"
        )

        print(
            f"Location  : "
            f"{experience.get('location')}"
        )

        print(
            f"Start     : "
            f"{experience.get('start_date')}"
        )

        print(
            f"End       : "
            f"{experience.get('end_date')}"
        )

        print(
            f"Start Text: "
            f"{experience.get('start_date_text')}"
        )

        print(
            f"End Text  : "
            f"{experience.get('end_date_text')}"
        )

        print(
            f"Precision : "
            f"{experience.get('date_precision')}"
        )

        print(
            f"Duration  : "
            f"{experience.get('duration_months')} months"
        )

        responsibilities = experience.get(
            "responsibilities",
            [],
        )

        print(
            f"Responsibilities: "
            f"{len(responsibilities)}"
        )

        for responsibility in responsibilities:

            print(
                f"  - {responsibility}"
            )

    print("\n" + "=" * 70)
    print("TOTAL EXPERIENCE")
    print("=" * 70)

    print(
        f"Months : "
        f"{result.get('total_experience_months', 0)}"
    )

    print(
        f"Years  : "
        f"{result.get('total_experience_years', 0.0):.2f}"
    )

    print("\n" + "=" * 70)
    print("GAPS")
    print("=" * 70)

    gaps = result.get(
        "gaps",
        [],
    )

    if gaps:

        for gap in gaps:

            print(
                f"{gap['from']} -> "
                f"{gap['to']} "
                f"({gap['months']} months)"
            )

    else:

        print("No gaps detected.")

    print("\n" + "=" * 70)
    print("OVERLAPS")
    print("=" * 70)

    overlaps = result.get(
        "overlaps",
        [],
    )

    if overlaps:

        for overlap in overlaps:

            print(
                f"{overlap['experience_1']} "
                f"overlaps with "
                f"{overlap['experience_2']}"
            )

    else:

        print("No overlaps detected.")


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) != 2:

        print(
            "Usage:\n"
            "  python parsers/experience_parser.py "
            "<resume-file>"
        )

        raise SystemExit(1)

    from parsers.resume_text_extractor import (
        extract_resume_text,
    )

    file_path = sys.argv[1]

    resume_text = extract_resume_text(
        file_path
    )

    result = ExperienceParser().parse_experience(
        resume_text
    )

    print_results(result)