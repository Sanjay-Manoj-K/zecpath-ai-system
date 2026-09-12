"""
Day 10 - Experience Relevance Scoring

Analyzes how relevant each candidate experience is
to a target job description.

Features:
1. Job title similarity
2. Candidate experience skill extraction
3. Required skill overlap
4. Responsibility similarity
5. Role-family similarity
6. Role-to-role similarity
7. Per-role relevance scoring
8. Overall relevance scoring
9. Ranking of candidate experiences

Design:
- Reuses Day 9 SkillExtractionEngine
- Uses target JobRequirement as the comparison target
- Does not depend on a particular resume
- Supports technical and non-technical roles
"""

import re
from typing import Dict, List, Set, Tuple


from parsers.skill_extraction_engine import (
    SkillExtractionEngine
)


class ExperienceRelevanceScorer:
    """
    Calculates experience relevance against a target job.

    Relevance components:

        Title similarity        25%
        Skill overlap           40%
        Role-family similarity  20%
        Responsibility overlap 15%
    """

    # ============================================================
    # ROLE FAMILY DEFINITIONS
    # ============================================================

    ROLE_FAMILY_KEYWORDS = {

        "software_engineering": {
            "software developer",
            "software engineer",
            "developer",
            "programmer",
            "backend developer",
            "backend engineer",
            "frontend developer",
            "frontend engineer",
            "full stack developer",
            "full stack engineer",
            "web developer",
            "application developer",
            "application engineer",
            "software development",
            "web development",
        },

        "ai_data": {
            "ai developer",
            "ai engineer",
            "artificial intelligence",
            "machine learning",
            "machine learning engineer",
            "ml engineer",
            "data scientist",
            "data analyst",
            "data science",
            "deep learning",
            "nlp",
            "computer vision",
        },

        "finance": {
            "finance",
            "financial",
            "financial analyst",
            "finance analyst",
            "accountant",
            "accounting",
            "investment",
            "investment analyst",
            "banking",
            "credit analyst",
            "auditor",
            "audit",
            "treasury",
            "financial planning",
        },

        "tax": {
            "tax",
            "tax analyst",
            "tax consultant",
            "tax accountant",
            "taxation",
        },

        "marketing": {
            "marketing",
            "marketing manager",
            "marketing executive",
            "digital marketing",
            "seo",
            "social media",
            "content marketing",
            "brand manager",
            "brand marketing",
            "market research",
        },

        "legal": {
            "legal",
            "lawyer",
            "attorney",
            "legal counsel",
            "counsel",
            "paralegal",
            "law",
            "compliance",
        },

        "human_resources": {
            "human resources",
            "hr",
            "hr manager",
            "hr executive",
            "hr specialist",
            "recruiter",
            "recruitment",
            "talent acquisition",
            "people operations",
        },

        "business_management": {
            "business analyst",
            "business strategist",
            "business strategy",
            "business development",
            "management",
            "manager",
            "project manager",
            "project management",
            "product manager",
            "product management",
            "operations manager",
            "operations",
            "consultant",
            "consulting",
        },

        "design": {
            "designer",
            "graphic designer",
            "ui designer",
            "ux designer",
            "ui ux",
            "ui/ux",
            "product designer",
            "visual designer",
            "graphic design",
            "visual design",
        },

        "engineering": {
            "mechanical engineer",
            "mechanical engineering",
            "civil engineer",
            "civil engineering",
            "electrical engineer",
            "electrical engineering",
            "electronics engineer",
            "electronics engineering",
            "chemical engineer",
            "chemical engineering",
            "industrial engineer",
            "industrial engineering",
        },

        "healthcare": {
            "doctor",
            "physician",
            "nurse",
            "nursing",
            "medical",
            "healthcare",
            "clinical",
            "pharmacist",
            "pharmacy",
        },

        "administration_support": {
            "assistant",
            "administrative assistant",
            "executive assistant",
            "office assistant",
            "administrator",
            "coordinator",
            "report writer",
            "report writing",
            "office manager",
            "secretary",
        },
    }

    # ============================================================
    # RELATED ROLE FAMILIES
    # ============================================================

    """
    Related families prevent unrelated roles from being treated
    exactly like completely unrelated roles.

    Example:

        software_engineering ↔ ai_data
        = moderately/highly related

        software_engineering ↔ finance
        = unrelated
    """

    RELATED_FAMILIES = {

        (
            "software_engineering",
            "ai_data",
        ): 0.70,

        (
            "ai_data",
            "software_engineering",
        ): 0.70,

        (
            "software_engineering",
            "business_management",
        ): 0.35,

        (
            "business_management",
            "software_engineering",
        ): 0.35,

        (
            "finance",
            "tax",
        ): 0.75,

        (
            "tax",
            "finance",
        ): 0.75,

        (
            "finance",
            "business_management",
        ): 0.45,

        (
            "business_management",
            "finance",
        ): 0.45,

        (
            "marketing",
            "business_management",
        ): 0.55,

        (
            "business_management",
            "marketing",
        ): 0.55,

        (
            "legal",
            "business_management",
        ): 0.25,

        (
            "business_management",
            "legal",
        ): 0.25,

        (
            "design",
            "software_engineering",
        ): 0.30,

        (
            "software_engineering",
            "design",
        ): 0.30,

        (
            "engineering",
            "software_engineering",
        ): 0.20,

        (
            "software_engineering",
            "engineering",
        ): 0.20,

        (
            "ai_data",
            "engineering",
        ): 0.25,

        (
            "engineering",
            "ai_data",
        ): 0.25,

        (
            "healthcare",
            "business_management",
        ): 0.20,

        (
            "administration_support",
            "business_management",
        ): 0.25,

        (
            "business_management",
            "administration_support",
        ): 0.25,
    }

    # ============================================================
    # STOP WORDS
    # ============================================================

    STOP_WORDS = {
        "and",
        "or",
        "the",
        "a",
        "an",
        "of",
        "to",
        "for",
        "with",
        "in",
        "on",
        "at",
        "by",
        "from",
        "as",
        "is",
        "are",
        "was",
        "were",
        "this",
        "that",
        "these",
        "those",
        "our",
        "their",
        "your",
        "will",
        "using",
        "use",
        "work",
        "working",
        "responsible",
    }

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(
        self,
        skill_engine: SkillExtractionEngine = None
    ):
        """
        Initialize the relevance scorer.

        A SkillExtractionEngine can be injected for testing,
        otherwise a new Day 9 engine is created.
        """

        if skill_engine is not None:

            self.skill_engine = skill_engine

        else:

            self.skill_engine = (
                SkillExtractionEngine()
            )

    # ============================================================
    # TEXT NORMALIZATION
    # ============================================================

    @staticmethod
    def normalize_text(
        text: str
    ) -> str:
        """
        Normalize text for comparison.
        """

        if not text:
            return ""

        text = text.lower().strip()

        text = text.replace(
            "–",
            "-"
        )

        text = text.replace(
            "—",
            "-"
        )

        text = text.replace(
            "&",
            " and "
        )

        text = re.sub(
            r"[^a-z0-9+#./ -]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # ============================================================
    # TOKENIZATION
    # ============================================================

    @classmethod
    def tokenize(
        cls,
        text: str
    ) -> Set[str]:
        """
        Create normalized comparison tokens.
        """

        normalized = cls.normalize_text(
            text
        )

        tokens = re.findall(
            r"[a-zA-Z0-9+#.]+",
            normalized
        )

        return {
            token.lower()
            for token in tokens
            if token.lower()
            not in cls.STOP_WORDS
        }

    # ============================================================
    # TITLE TOKENIZATION
    # ============================================================

    @classmethod
    def get_title_tokens(
        cls,
        title: str
    ) -> Set[str]:
        """
        Extract meaningful title tokens.
        """

        return cls.tokenize(
            title
        )

    # ============================================================
    # TITLE SIMILARITY
    # ============================================================

    @classmethod
    def calculate_title_similarity(
        cls,
        candidate_title: str,
        target_title: str
    ) -> float:
        """
        Calculate token-based title similarity.

        Uses Jaccard similarity.
        """

        candidate_tokens = (
            cls.get_title_tokens(
                candidate_title
            )
        )

        target_tokens = (
            cls.get_title_tokens(
                target_title
            )
        )

        if (
            not candidate_tokens
            or not target_tokens
        ):
            return 0.0

        intersection = (
            candidate_tokens
            & target_tokens
        )

        union = (
            candidate_tokens
            | target_tokens
        )

        if not union:
            return 0.0

        return round(
            len(intersection)
            / len(union),
            3
        )

    # ============================================================
    # EXPERIENCE TEXT
    # ============================================================

    @staticmethod
    def build_experience_text(
        experience: Dict
    ) -> str:
        """
        Combine title, company and responsibilities.
        """

        parts = []

        title = experience.get(
            "job_title",
            ""
        )

        company = experience.get(
            "company",
            ""
        )

        responsibilities = experience.get(
            "responsibilities",
            []
        )

        if title:
            parts.append(title)

        if company:
            parts.append(company)

        if responsibilities:

            parts.extend(
                responsibilities
            )

        return " ".join(
            parts
        )

    # ============================================================
    # DAY 9 SKILL EXTRACTION FOR EXPERIENCE
    # ============================================================

    def extract_experience_skills(
        self,
        experience: Dict
    ) -> List[str]:
        """
        Use Day 9 SkillExtractionEngine to extract
        normalized skills from one experience.
        """

        text = self.build_experience_text(
            experience
        )

        if not text:
            return []

        result = self.skill_engine.extract_skills(
            text,
            source_section="work_experience"
        )

        return [
            skill["canonical"]
            for skill in result.get(
                "skills",
                []
            )
        ]

    # ============================================================
    # NORMALIZED SKILL SET
    # ============================================================

    def normalize_skill_set(
        self,
        skills: List[str]
    ) -> Set[str]:
        """
        Normalize a list of skills.
        """

        normalized = set()

        for skill in skills:

            if not skill:
                continue

            value = self.normalize_text(
                skill
            )

            if value:
                normalized.add(
                    value
                )

        return normalized

    # ============================================================
    # JOB REQUIRED SKILLS
    # ============================================================

    def extract_job_skills(
        self,
        job_requirement
    ) -> Set[str]:
        """
        Get normalized required skills from the JD.
        """

        required_skills = getattr(
            job_requirement,
            "required_skills",
            []
        )

        return self.normalize_skill_set(
            required_skills
        )

    # ============================================================
    # SKILL CANONICALIZATION
    # ============================================================

    def canonicalize_job_skill(
        self,
        skill: str
    ) -> str:
        """
        Convert a job requirement skill into the
        Day 9 canonical form when available.

        Keeps unknown JD skills unchanged.
        """

        if not skill:
            return ""

        normalized = (
            self.skill_engine.normalize_text(
                skill
            )
        )

        canonical = (
            self.skill_engine.skill_lookup.get(
                normalized
            )
        )

        if canonical:
            return canonical

        # Common JD variants not currently present
        # in the Day 9 dictionary.
        aliases = {
            "rest api": "REST APIs",
            "rest apis": "REST APIs",
            "restful api": "REST APIs",
            "restful apis": "REST APIs",
            "version control": "Git",
            "git/version control": "Git",
        }

        return aliases.get(
            normalized,
            skill.strip()
        )

    # ============================================================
    # CANONICAL JOB SKILLS
    # ============================================================

    def get_canonical_job_skills(
        self,
        job_requirement
    ) -> Set[str]:
        """
        Normalize required JD skills while preserving
        skills not found in Day 9's dictionary.
        """

        result = set()

        required_skills = getattr(
            job_requirement,
            "required_skills",
            []
        )

        for skill in required_skills:

            canonical = (
                self.canonicalize_job_skill(
                    skill
                )
            )

            if canonical:

                result.add(
                    self.normalize_text(
                        canonical
                    )
                )

        return result

    # ============================================================
    # SKILL OVERLAP
    # ============================================================

    def calculate_skill_overlap(
        self,
        experience: Dict,
        job_requirement
    ) -> Tuple[
        float,
        List[str],
        List[str]
    ]:
        """
        Calculate overlap between candidate experience
        skills and required JD skills.

        Returns:
            score,
            matched skills,
            candidate skills
        """

        candidate_skills = (
            self.extract_experience_skills(
                experience
            )
        )

        candidate_normalized = (
            self.normalize_skill_set(
                candidate_skills
            )
        )

        required_normalized = (
            self.get_canonical_job_skills(
                job_requirement
            )
        )

        if not required_normalized:

            return (
                0.0,
                [],
                candidate_skills
            )

        matched = []

        for required in required_normalized:

            if required in candidate_normalized:

                matched.append(
                    required
                )

        score = (
            len(matched)
            / len(required_normalized)
        )

        return (
            round(score, 3),
            sorted(matched),
            sorted(candidate_skills)
        )

    # ============================================================
    # RESPONSIBILITY TEXT
    # ============================================================

    @staticmethod
    def get_experience_responsibilities(
        experience: Dict
    ) -> str:
        """
        Return candidate responsibility text.
        """

        responsibilities = (
            experience.get(
                "responsibilities",
                []
            )
        )

        if not responsibilities:
            return ""

        return " ".join(
            responsibilities
        )

    # ============================================================
    # TARGET JOB RESPONSIBILITIES
    # ============================================================

    @staticmethod
    def get_job_responsibilities(
        job_requirement
    ) -> str:
        """
        Return target job responsibility text.
        """

        responsibilities = getattr(
            job_requirement,
            "responsibilities",
            []
        )

        if not responsibilities:
            return ""

        return " ".join(
            responsibilities
        )

    # ============================================================
    # RESPONSIBILITY SIMILARITY
    # ============================================================

    @classmethod
    def calculate_responsibility_similarity(
        cls,
        experience: Dict,
        job_requirement
    ) -> float:
        """
        Compare responsibility language using token
        overlap after stop-word removal.
        """

        candidate_text = (
            cls.get_experience_responsibilities(
                experience
            )
        )

        target_text = (
            cls.get_job_responsibilities(
                job_requirement
            )
        )

        candidate_tokens = cls.tokenize(
            candidate_text
        )

        target_tokens = cls.tokenize(
            target_text
        )

        if (
            not candidate_tokens
            or not target_tokens
        ):
            return 0.0

        intersection = (
            candidate_tokens
            & target_tokens
        )

        union = (
            candidate_tokens
            | target_tokens
        )

        if not union:
            return 0.0

        return round(
            len(intersection)
            / len(union),
            3
        )

    # ============================================================
    # ROLE FAMILY DETECTION
    # ============================================================

    @classmethod
    def detect_role_family(
        cls,
        role_title: str,
        skills: List[str] = None
    ) -> str:
        """
        Infer a broad professional role family.

        Title evidence is checked first.

        Skills are used only as secondary evidence.
        """

        title = cls.normalize_text(
            role_title
        )

        # --------------------------------------------------------
        # Strong title phrases first
        # --------------------------------------------------------

        strong_matches = []

        for family, keywords in (
            cls.ROLE_FAMILY_KEYWORDS.items()
        ):

            for keyword in keywords:

                normalized_keyword = (
                    cls.normalize_text(
                        keyword
                    )
                )

                if (
                    normalized_keyword
                    and normalized_keyword
                    in title
                ):

                    strong_matches.append(
                        (
                            family,
                            len(
                                normalized_keyword
                            )
                        )
                    )

        if strong_matches:

            strong_matches.sort(
                key=lambda item:
                item[1],
                reverse=True
            )

            return strong_matches[0][0]

        # --------------------------------------------------------
        # Secondary skill evidence
        # --------------------------------------------------------

        if skills:

            skill_text = cls.normalize_text(
                " ".join(skills)
            )

            family_scores = {}

            for family, keywords in (
                cls.ROLE_FAMILY_KEYWORDS.items()
            ):

                score = 0

                for keyword in keywords:

                    normalized_keyword = (
                        cls.normalize_text(
                            keyword
                        )
                    )

                    if (
                        normalized_keyword
                        in skill_text
                    ):

                        score += 1

                family_scores[family] = score

            if family_scores:

                best_family = max(
                    family_scores,
                    key=family_scores.get
                )

                if (
                    family_scores[
                        best_family
                    ] > 0
                ):

                    return best_family

        return "general"

    # ============================================================
    # ROLE FAMILY SIMILARITY
    # ============================================================

    @classmethod
    def calculate_role_family_similarity(
        cls,
        candidate_role: str,
        target_role: str,
        candidate_skills: List[str] = None
    ) -> Tuple[float, str, str]:
        """
        Compare broad professional role families.
        """

        candidate_family = (
            cls.detect_role_family(
                candidate_role,
                candidate_skills
            )
        )

        target_family = (
            cls.detect_role_family(
                target_role
            )
        )

        if candidate_family == target_family:

            return (
                1.0,
                candidate_family,
                target_family
            )

        related_score = (
            cls.RELATED_FAMILIES.get(
                (
                    candidate_family,
                    target_family
                ),
                0.0
            )
        )

        return (
            round(
                related_score,
                3
            ),
            candidate_family,
            target_family
        )

    # ============================================================
    # ROLE-TO-ROLE SIMILARITY
    # ============================================================

    @classmethod
    def calculate_role_similarity(
        cls,
        candidate_role: str,
        target_role: str,
        candidate_skills: List[str] = None
    ) -> float:
        """
        Calculate role-to-role similarity.

        Combines:

            60% title similarity
            40% role-family similarity
        """

        title_score = (
            cls.calculate_title_similarity(
                candidate_role,
                target_role
            )
        )

        family_score, _, _ = (
            cls.calculate_role_family_similarity(
                candidate_role,
                target_role,
                candidate_skills
            )
        )

        score = (
            title_score * 0.60
            + family_score * 0.40
        )

        return round(
            score,
            3
        )

    # ============================================================
    # RELEVANCE SCORE
    # ============================================================

    def calculate_relevance_score(
        self,
        experience: Dict,
        job_requirement
    ) -> Dict:
        """
        Calculate relevance of one role.

        Weights:

            Title similarity        25%
            Skill overlap           40%
            Role-family similarity  20%
            Responsibility overlap 15%
        """

        candidate_role = experience.get(
            "job_title",
            ""
        )

        target_role = getattr(
            job_requirement,
            "role",
            ""
        )

        # --------------------------------------------------------
        # Candidate skills through Day 9
        # --------------------------------------------------------

        skill_overlap, matched_skills, candidate_skills = (
            self.calculate_skill_overlap(
                experience,
                job_requirement
            )
        )

        # --------------------------------------------------------
        # Title similarity
        # --------------------------------------------------------

        title_score = (
            self.calculate_title_similarity(
                candidate_role,
                target_role
            )
        )

        # --------------------------------------------------------
        # Role family
        # --------------------------------------------------------

        (
            family_score,
            candidate_family,
            target_family,
        ) = self.calculate_role_family_similarity(
            candidate_role,
            target_role,
            candidate_skills
        )

        # --------------------------------------------------------
        # Responsibility similarity
        # --------------------------------------------------------

        responsibility_score = (
            self.calculate_responsibility_similarity(
                experience,
                job_requirement
            )
        )

        # --------------------------------------------------------
        # Overall
        # --------------------------------------------------------

        overall_score = (
            title_score * 0.25
            + skill_overlap * 0.40
            + family_score * 0.20
            + responsibility_score * 0.15
        )

        return {
            "job_title":
                candidate_role,

            "company":
                experience.get(
                    "company",
                    ""
                ),

            "title_similarity":
                round(
                    title_score,
                    3
                ),

            "skill_overlap_score":
                round(
                    skill_overlap,
                    3
                ),

            "role_family_score":
                round(
                    family_score,
                    3
                ),

            "responsibility_similarity":
                round(
                    responsibility_score,
                    3
                ),

            "relevance_score":
                round(
                    overall_score,
                    3
                ),

            "relevance_percent":
                round(
                    overall_score * 100,
                    2
                ),

            "candidate_skills":
                candidate_skills,

            "matched_skills":
                matched_skills,

            "candidate_role_family":
                candidate_family,

            "target_role_family":
                target_family,
        }

    # ============================================================
    # SCORE ALL EXPERIENCES
    # ============================================================

    def score_experiences(
        self,
        experiences: List[Dict],
        job_requirement
    ) -> Dict:
        """
        Score every candidate experience and rank
        the roles from most relevant to least relevant.
        """

        results = []

        for experience in experiences:

            result = (
                self.calculate_relevance_score(
                    experience,
                    job_requirement
                )
            )

            results.append(
                result
            )

        # --------------------------------------------------------
        # Rank highest relevance first
        # --------------------------------------------------------

        results.sort(
            key=lambda item:
            item["relevance_score"],
            reverse=True
        )

        # --------------------------------------------------------
        # Overall experience relevance
        # --------------------------------------------------------

        if results:

            overall_score = (
                sum(
                    item["relevance_score"]
                    for item in results
                )
                / len(results)
            )

        else:

            overall_score = 0.0

        return {
            "target_role":
                getattr(
                    job_requirement,
                    "role",
                    ""
                ),

            "experiences":
                results,

            "overall_relevance_score":
                round(
                    overall_score,
                    3
                ),

            "overall_relevance_percent":
                round(
                    overall_score * 100,
                    2
                ),
        }

    # ============================================================
    # DISPLAY
    # ============================================================

    @staticmethod
    def print_results(
        result: Dict
    ) -> None:
        """
        Print detailed relevance results.
        """

        print(
            "\n========================================"
        )

        print(
            "===== EXPERIENCE RELEVANCE ====="
        )

        print(
            "========================================"
        )

        print(
            f"\nTarget Role: "
            f"{result['target_role']}"
        )

        print(
            f"Overall Relevance: "
            f"{result['overall_relevance_percent']:.2f}%"
        )

        print(
            "\n===== ROLE RELEVANCE RANKING ====="
        )

        for index, experience in enumerate(
            result["experiences"],
            start=1
        ):

            print(
                f"\nRank {index}"
            )

            print(
                f"Role              : "
                f"{experience['job_title']}"
            )

            print(
                f"Company           : "
                f"{experience['company']}"
            )

            print(
                f"Title Similarity  : "
                f"{experience['title_similarity']:.3f}"
            )

            print(
                f"Skill Overlap     : "
                f"{experience['skill_overlap_score']:.3f}"
            )

            print(
                f"Role Family Score : "
                f"{experience['role_family_score']:.3f}"
            )

            print(
                f"Responsibility    : "
                f"{experience['responsibility_similarity']:.3f}"
            )

            print(
                f"Relevance Score   : "
                f"{experience['relevance_percent']:.2f}%"
            )

            print(
                f"Candidate Family  : "
                f"{experience['candidate_role_family']}"
            )

            print(
                f"Target Family     : "
                f"{experience['target_role_family']}"
            )

            print(
                "Candidate Skills  : "
                + (
                    ", ".join(
                        experience[
                            "candidate_skills"
                        ]
                    )
                    if experience[
                        "candidate_skills"
                    ]
                    else "None"
                )
            )

            print(
                "Matched Skills    : "
                + (
                    ", ".join(
                        experience[
                            "matched_skills"
                        ]
                    )
                    if experience[
                        "matched_skills"
                    ]
                    else "None"
                )
            )