"""
Day 8 - Resume Section Segmentation

Identifies and separates major resume sections using:
1. Rule-based heading detection
2. NLP-style content classification fallback
3. Experience date-pattern detection
4. Personal information detection
5. Context-based classification
6. Heading-aware block segmentation

Supported sections:
- Personal Information
- Summary
- Work Experience
- Education
- Skills
- Certifications
- Projects
- Other
"""

import re
from typing import Dict, List, Tuple


class ResumeSectionClassifier:
    """
    Classifies resume text into meaningful sections.

    Classification priority:
        1. Personal information detection
        2. Explicit section heading
        3. Experience date pattern
        4. NLP/content classification
        5. Existing section context
        6. Other
    """

    # ============================================================
    # SECTION ALIASES
    # ============================================================

    SECTION_ALIASES = {
        "skills": [
            "skills",
            "technical skills",
            "technical skill",
            "core skills",
            "key skills",
            "professional skills",
            "competencies",
            "technical competencies",
            "core competencies",
            "expertise",
            "areas of expertise",
            "skills & expertise",
            "skills and expertise",
        ],

        "work_experience": [
            "experience",
            "work experience",
            "professional experience",
            "employment history",
            "work history",
            "career history",
            "professional background",
            "employment",
            "career experience",
        ],

        "education": [
            "education",
            "educational background",
            "academic background",
            "academic qualifications",
            "qualifications",
            "academic history",
        ],

        "certifications": [
            "certifications",
            "certificates",
            "professional certifications",
            "licenses and certifications",
            "certification",
        ],

        "projects": [
            "projects",
            "academic projects",
            "personal projects",
            "key projects",
            "project experience",
            "project work",
        ],

        "summary": [
            "summary",
            "professional summary",
            "career summary",
            "profile",
            "professional profile",
            "objective",
            "career objective",
            "about me",
        ],

        "personal_information": [
            "personal information",
            "personal details",
            "contact",
            "contact information",
            "contact details",
        ],
    }

    # ============================================================
    # CONTENT KEYWORDS
    # ============================================================

    CONTENT_KEYWORDS = {
        "skills": {
            "python",
            "java",
            "javascript",
            "typescript",
            "c++",
            "c#",
            "sql",
            "html",
            "css",
            "react",
            "angular",
            "django",
            "flask",
            "fastapi",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "machine learning",
            "deep learning",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "git",
            "github",
            "figma",
            "flutter",
            "excel",
            "power bi",
            "rest api",
            "rest apis",
        },

        "work_experience": {
            "worked",
            "developed",
            "implemented",
            "designed",
            "managed",
            "led",
            "built",
            "created",
            "maintained",
            "optimized",
            "engineered",
            "deployed",
            "responsible",
            "experience",
            "developer",
            "engineer",
            "manager",
            "analyst",
            "intern",
            "consultant",
        },

        "education": {
            "bachelor",
            "master",
            "phd",
            "doctorate",
            "degree",
            "university",
            "college",
            "school",
            "b.sc",
            "m.sc",
            "bca",
            "mca",
            "b.tech",
            "m.tech",
            "computer science",
            "graduated",
            "gpa",
        },

        "certifications": {
            "certified",
            "certification",
            "certificate",
            "license",
            "credential",
            "aws certified",
            "microsoft certified",
            "oracle certified",
            "google certified",
        },

        "projects": {
            "project",
            "developed an application",
            "built an application",
            "github",
            "repository",
            "prototype",
            "capstone",
            "implemented a system",
            "developed a system",
        },

        "summary": {
            "innovative",
            "professional",
            "experienced",
            "motivated",
            "passionate",
            "specialized",
            "expertise",
            "proven track record",
            "career",
        },

        "personal_information": {
            "email",
            "phone",
            "mobile",
            "address",
            "linkedin",
            "github",
            "location",
        },
    }

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self):
        self.section_alias_lookup = self._build_alias_lookup()

    # ============================================================
    # NORMALIZATION
    # ============================================================

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for matching.

        Example:
            'Technical Skills :' -> 'technical skills'
        """

        if not text:
            return ""

        text = text.strip().lower()

        # Replace common separators.
        text = text.replace("&", " and ")
        text = text.replace(":", " ")
        text = text.replace("|", " ")

        # Collapse whitespace.
        text = re.sub(r"\s+", " ", text)

        # Remove surrounding punctuation.
        text = text.strip(" -–—•|:")

        return text.strip()

    # ============================================================
    # TOKENIZATION
    # ============================================================

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Basic NLP-style tokenization.
        """

        if not text:
            return []

        return re.findall(
            r"[a-zA-Z][a-zA-Z0-9+#.-]*",
            text.lower()
        )

    # ============================================================
    # BUILD SECTION ALIAS LOOKUP
    # ============================================================

    def _build_alias_lookup(self) -> Dict[str, str]:
        """
        Create reverse lookup.

        Example:
            technical skills -> skills
            work history -> work_experience
        """

        lookup = {}

        for section, aliases in self.SECTION_ALIASES.items():

            for alias in aliases:

                normalized = self.normalize_text(alias)

                lookup[normalized] = section

        return lookup

    # ============================================================
    # SECTION HEADING DETECTION
    # ============================================================

    def detect_heading(
        self,
        line: str
    ) -> Tuple[str, float]:
        """
        Detect whether a line is a known resume section heading.

        Returns:
            (section_name, confidence)
        """

        normalized = self.normalize_text(line)

        if not normalized:
            return "other", 0.0

        # --------------------------------------------------------
        # Exact heading match
        # --------------------------------------------------------

        if normalized in self.section_alias_lookup:

            return (
                self.section_alias_lookup[normalized],
                1.0
            )

        # --------------------------------------------------------
        # Remove numbering
        # Example:
        # 1. Skills
        # 2) Education
        # 3-Projects
        # --------------------------------------------------------

        cleaned = re.sub(
            r"^\d+[\s.)-]+",
            "",
            normalized
        )

        # --------------------------------------------------------
        # Remove bullets
        # --------------------------------------------------------

        cleaned = re.sub(
            r"^[•*\-]+\s*",
            "",
            cleaned
        )

        # --------------------------------------------------------
        # Check cleaned heading
        # --------------------------------------------------------

        if cleaned in self.section_alias_lookup:

            return (
                self.section_alias_lookup[cleaned],
                0.98
            )

        # --------------------------------------------------------
        # Handle small heading variations
        # --------------------------------------------------------

        for alias, section in self.section_alias_lookup.items():

            if (
                cleaned.startswith(alias + " ")
                or cleaned.endswith(" " + alias)
            ):

                return section, 0.90

        return "other", 0.0

    # ============================================================
    # HEADING HEURISTICS
    # ============================================================

    @staticmethod
    def looks_like_heading(line: str) -> bool:
        """
        Determine whether a line visually looks like a heading.
        """

        if not line:
            return False

        line = line.strip()

        if not line:
            return False

        if len(line) > 60:
            return False

        # Sentence-like text is unlikely to be a heading.
        if line.endswith("."):
            return False

        words = line.split()

        if len(words) > 8:
            return False

        # Title-case words.
        title_case_words = sum(
            1
            for word in words
            if word[:1].isupper()
        )

        if title_case_words >= max(
            1,
            len(words) // 2
        ):

            return True

        # All-uppercase heading.
        if (
            line.upper() == line
            and any(
                char.isalpha()
                for char in line
            )
        ):

            return True

        return False

    # ============================================================
    # PERSONAL INFORMATION DETECTION
    # ============================================================

    @staticmethod
    def contains_personal_information(
        text: str
    ) -> bool:
        """
        Detect common personal/contact information.

        Examples:
            Email address
            Phone number
            LinkedIn
            GitHub
            Address/location
        """

        if not text:
            return False

        normalized = text.lower()

        # --------------------------------------------------------
        # Email
        # --------------------------------------------------------

        if re.search(
            r"[\w\.-]+@[\w\.-]+\.\w+",
            text
        ):

            return True

        # --------------------------------------------------------
        # Phone number
        # --------------------------------------------------------

        if re.search(
            r"\b(?:\+?\d[\d\s().-]{7,}\d)\b",
            text
        ):

            return True

        # --------------------------------------------------------
        # LinkedIn / GitHub
        # --------------------------------------------------------

        if "linkedin.com" in normalized:
            return True

        if "github.com" in normalized:
            return True

        # --------------------------------------------------------
        # Contact keywords
        # --------------------------------------------------------

        contact_keywords = [
            "phone",
            "mobile",
            "email",
            "linkedin",
            "github",
            "address",
        ]

        for keyword in contact_keywords:

            if keyword in normalized:

                return True

        return False

    # ============================================================
    # NLP-STYLE CONTENT CLASSIFICATION
    # ============================================================

    def classify_by_content(
        self,
        text: str
    ) -> Tuple[str, float]:
        """
        Classify a block using keyword/token evidence.

        Returns:
            (section_name, confidence)
        """

        if not text or not text.strip():

            return "other", 0.0

        normalized = text.lower()

        tokens = set(
            self.tokenize(text)
        )

        scores = {}

        # --------------------------------------------------------
        # Calculate score for every section
        # --------------------------------------------------------

        for section, keywords in (
            self.CONTENT_KEYWORDS.items()
        ):

            score = 0.0

            for keyword in keywords:

                keyword_lower = keyword.lower()

                # Multi-word keyword.
                if " " in keyword_lower:

                    if keyword_lower in normalized:

                        score += 2.0

                # Single-word keyword.
                else:

                    if keyword_lower in tokens:

                        score += 1.0

            scores[section] = score

        if not scores:

            return "other", 0.0

        # --------------------------------------------------------
        # Find highest scoring section
        # --------------------------------------------------------

        best_section = max(
            scores,
            key=scores.get
        )

        best_score = scores[best_section]

        if best_score <= 0:

            return "other", 0.0

        # --------------------------------------------------------
        # Convert score to confidence
        # --------------------------------------------------------

        confidence = min(
            best_score / 5.0,
            1.0
        )

        return (
            best_section,
            round(confidence, 2)
        )

    # ============================================================
    # EXPERIENCE DATE DETECTION
    # ============================================================

    @staticmethod
    def contains_experience_date(
        text: str
    ) -> bool:
        """
        Detect common employment date patterns.

        Examples:
            January 2024 - August 2025
            January 2024 to August 2025
            Jan 2022 to Dec 2023
            2020 - 2022
            01/2020 - 12/2022
        """

        if not text:
            return False

        patterns = [

            # January 2024 / Jan 2024
            (
                r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|"
                r"sep|oct|nov|dec)[a-z]*\s+\d{4}\b"
            ),

            # 2020 - 2022
            (
                r"\b\d{4}\s*"
                r"(?:-|–|—|to)"
                r"\s*\d{4}\b"
            ),

            # 01/2020 - 12/2022
            (
                r"\b\d{1,2}/\d{4}\s*"
                r"(?:-|–|—|to)"
                r"\s*\d{1,2}/\d{4}\b"
            ),
        ]

        for pattern in patterns:

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):

                return True

        return False

    # ============================================================
    # HEADING-AWARE BLOCK SEGMENTATION
    # ============================================================

    def split_into_blocks(
        self,
        resume_text: str
    ) -> List[str]:
        """
        Split resume into logical blocks.

        Handles both:

        1. Resumes with blank lines between sections.
        2. DOCX extracted text where headings appear consecutively
           without blank lines.

        Example:

            Sophia Martinez
            Northwood, OH
            email@example.com
            Professional Summary
            ...
            Work History
            ...
            Skills
            ...

        becomes separate logical blocks.
        """

        if not resume_text:
            return []

        # --------------------------------------------------------
        # Preserve non-empty lines.
        # --------------------------------------------------------

        raw_lines = resume_text.splitlines()

        lines = []

        for line in raw_lines:

            cleaned_line = line.strip()

            if cleaned_line:

                lines.append(cleaned_line)

        if not lines:
            return []

        blocks = []

        current_block = []

        for line in lines:

            # ----------------------------------------------------
            # Detect whether this line is a known section heading.
            # ----------------------------------------------------

            section, confidence = self.detect_heading(line)

            # ----------------------------------------------------
            # If heading found:
            #
            # Save previous block first.
            # Then start new block with heading.
            # ----------------------------------------------------

            if section != "other":

                if current_block:

                    blocks.append(
                        "\n".join(
                            current_block
                        ).strip()
                    )

                    current_block = []

                current_block.append(line)

                continue

            # ----------------------------------------------------
            # Normal content line
            # ----------------------------------------------------

            current_block.append(line)

        # --------------------------------------------------------
        # Save final block.
        # --------------------------------------------------------

        if current_block:

            blocks.append(
                "\n".join(
                    current_block
                ).strip()
            )

        return blocks

    # ============================================================
    # MAIN SECTION SEGMENTATION
    # ============================================================

    def segment(
        self,
        resume_text: str
    ) -> Dict[str, List[str]]:
        """
        Segment resume into structured sections.

        Priority:
            1. Personal information
            2. Explicit section heading
            3. Experience date pattern
            4. NLP/content classification
            5. Existing section context
            6. Other
        """

        sections = {
            "personal_information": [],
            "summary": [],
            "work_experience": [],
            "education": [],
            "skills": [],
            "certifications": [],
            "projects": [],
            "other": [],
        }

        blocks = self.split_into_blocks(
            resume_text
        )

        current_section = "other"

        for index, block in enumerate(blocks):

            lines = block.splitlines()

            if not lines:
                continue

            first_line = lines[0].strip()

            # ====================================================
            # STEP 1 - PERSONAL INFORMATION
            # ====================================================

            # The first block of a resume usually contains
            # candidate information.

            if (
                index == 0
                and self.contains_personal_information(block)
            ):

                sections[
                    "personal_information"
                ].append(block)

                current_section = (
                    "personal_information"
                )

                continue

            # ====================================================
            # STEP 2 - EXPLICIT HEADING
            # ====================================================

            (
                heading_section,
                heading_confidence
            ) = self.detect_heading(
                first_line
            )

            if heading_section != "other":

                current_section = heading_section

                remaining_lines = lines[1:]

                if remaining_lines:

                    content = "\n".join(
                        remaining_lines
                    ).strip()

                    if content:

                        sections[
                            current_section
                        ].append(content)

                continue

            # ====================================================
            # STEP 3 - EXPERIENCE DATE DETECTION
            # ====================================================

            if self.contains_experience_date(
                block
            ):

                sections[
                    "work_experience"
                ].append(block)

                current_section = (
                    "work_experience"
                )

                continue

            # ====================================================
            # STEP 4 - NLP CONTENT CLASSIFICATION
            # ====================================================

            (
                detected_section,
                confidence
            ) = self.classify_by_content(
                block
            )

            if confidence >= 0.40:

                sections[
                    detected_section
                ].append(block)

                # Strong classification updates context.
                if confidence >= 0.60:

                    current_section = (
                        detected_section
                    )

                continue

            # ====================================================
            # STEP 5 - CONTEXT CLASSIFICATION
            # ====================================================

            if current_section != "other":

                sections[
                    current_section
                ].append(block)

            else:

                sections[
                    "other"
                ].append(block)

        return sections

    # ============================================================
    # DETAILED BLOCK CLASSIFICATION
    # ============================================================

    def classify_blocks(
        self,
        resume_text: str
    ) -> List[Dict]:
        """
        Return detailed classification information
        for every resume block.

        Classification priority:
            1. Personal information
            2. Explicit heading
            3. Experience date pattern
            4. NLP fallback
            5. Context
        """

        results = []

        blocks = self.split_into_blocks(
            resume_text
        )

        current_section = "other"

        for index, block in enumerate(
            blocks
        ):

            lines = block.splitlines()

            if not lines:
                continue

            first_line = lines[0].strip()

            # ====================================================
            # STEP 1 - PERSONAL INFORMATION
            # ====================================================

            if (
                index == 0
                and self.contains_personal_information(
                    block
                )
            ):

                current_section = (
                    "personal_information"
                )

                results.append({
                    "block_id": index + 1,
                    "text": block,
                    "section": (
                        "personal_information"
                    ),
                    "method": "personal-info",
                    "confidence": 0.95,
                })

                continue

            # ====================================================
            # STEP 2 - EXPLICIT HEADING
            # ====================================================

            (
                heading_section,
                heading_confidence
            ) = self.detect_heading(
                first_line
            )

            if heading_section != "other":

                current_section = (
                    heading_section
                )

                results.append({
                    "block_id": index + 1,
                    "text": block,
                    "section": heading_section,
                    "method": "rule-based",
                    "confidence": heading_confidence,
                })

                continue

            # ====================================================
            # STEP 3 - EXPERIENCE DATE DETECTION
            # ====================================================

            if self.contains_experience_date(
                block
            ):

                current_section = (
                    "work_experience"
                )

                results.append({
                    "block_id": index + 1,
                    "text": block,
                    "section": (
                        "work_experience"
                    ),
                    "method": "date-pattern",
                    "confidence": 0.95,
                })

                continue

            # ====================================================
            # STEP 4 - NLP FALLBACK
            # ====================================================

            (
                detected_section,
                confidence
            ) = self.classify_by_content(
                block
            )

            if confidence >= 0.40:

                if confidence >= 0.60:

                    current_section = (
                        detected_section
                    )

                results.append({
                    "block_id": index + 1,
                    "text": block,
                    "section": detected_section,
                    "method": "nlp-fallback",
                    "confidence": confidence,
                })

                continue

            # ====================================================
            # STEP 5 - CONTEXT
            # ====================================================

            results.append({
                "block_id": index + 1,
                "text": block,
                "section": current_section,
                "method": "context",
                "confidence": 0.60,
            })

        return results

    # ============================================================
    # DISPLAY SEGMENTED SECTIONS
    # ============================================================

    def print_sections(
        self,
        sections: Dict[str, List[str]]
    ) -> None:
        """
        Print segmented resume in a clean format.
        """

        display_names = {
            "personal_information":
                "PERSONAL INFORMATION",

            "summary":
                "SUMMARY",

            "work_experience":
                "WORK EXPERIENCE",

            "education":
                "EDUCATION",

            "skills":
                "SKILLS",

            "certifications":
                "CERTIFICATIONS",

            "projects":
                "PROJECTS",

            "other":
                "OTHER",
        }

        print(
            "\n========================================"
        )

        print(
            "===== RESUME SECTION SEGMENTATION ====="
        )

        print(
            "========================================"
        )

        for section, contents in (
            sections.items()
        ):

            print(
                f"\n===== "
                f"{display_names[section]}"
                f" ====="
            )

            if not contents:

                print(
                    "(No content detected)"
                )

                continue

            for item in contents:

                print(item)

                print(
                    "----------------------------------------"
                )

    # ============================================================
    # DISPLAY DETAILED CLASSIFICATION
    # ============================================================

    def print_detailed_classification(
        self,
        classifications: List[Dict]
    ) -> None:
        """
        Print detailed block classification.
        """

        print(
            "\n========================================"
        )

        print(
            "===== DETAILED BLOCK CLASSIFICATION ====="
        )

        print(
            "========================================"
        )

        for item in classifications:

            print(
                f"\nBlock {item['block_id']}"
            )

            print(
                f"Section    : "
                f"{item['section']}"
            )

            print(
                f"Method     : "
                f"{item['method']}"
            )

            print(
                f"Confidence : "
                f"{item['confidence']}"
            )

            print(
                "Text       : "
                f"{item['text'][:500]}"
            )

    # ============================================================
    # SECTION SUMMARY
    # ============================================================

    def print_section_summary(
        self,
        sections: Dict[str, List[str]]
    ) -> None:
        """
        Print number of detected blocks
        for every section.
        """

        print(
            "\n========================================"
        )

        print(
            "===== SECTION SUMMARY ====="
        )

        print(
            "========================================"
        )

        for section, contents in (
            sections.items()
        ):

            print(
                f"{section:<25}: "
                f"{len(contents)} block(s)"
            )


# ================================================================
# OPTIONAL STANDALONE TEST
# ================================================================

if __name__ == "__main__":

    sample_resume = """
Sophia Martinez
Northwood, OH 43623
(555)555-5555
Sophia.Martinez@example.com

Professional Summary
Innovative AI Software Developer with expertise in machine learning, utilizing Python and TensorFlow.

Work History
AI Software Developer
January 2024 to August 2025
DeepTech Innovations
Developed AI algorithms and optimized neural networks.

Machine Learning Engineer
January 2022 to December 2023
Quantum AI Systems
Designed machine learning models.

Skills
Python
TensorFlow
Machine Learning
Artificial Intelligence

Certifications
Certified AI Practitioner
Machine Learning Specialist

Education
Master of Science: Computer Science
Stanford University

Bachelor of Science: Data Science
University of California, Berkeley

Projects
AI Resume Screening System
Developed a Python-based resume analysis application.
"""

    classifier = ResumeSectionClassifier()

    sections = classifier.segment(
        sample_resume
    )

    detailed_blocks = classifier.classify_blocks(
        sample_resume
    )

    classifier.print_sections(
        sections
    )

    classifier.print_detailed_classification(
        detailed_blocks
    )

    classifier.print_section_summary(
        sections
    )