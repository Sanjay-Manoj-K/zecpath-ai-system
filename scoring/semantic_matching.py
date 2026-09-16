"""
Day 12 - Semantic Matching Engine

Purpose:
    Provide embedding-based semantic similarity between resume content
    and job-description content.

Features:
    - Text embeddings
    - Pairwise semantic similarity
    - Section-level semantic similarity
    - Dynamic weighted overall score
    - Missing-section handling
    - Threshold-based match classification

Model:
    sentence-transformers/all-MiniLM-L6-v2

Day 12 target areas:
    1. Skills
    2. Experience summaries
    3. Project descriptions
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Optional, Any

from sentence_transformers import SentenceTransformer


# ============================================================
# DATA MODEL
# ============================================================

@dataclass
class SemanticMatchResult:
    """
    Structured result returned by the semantic matching engine.

    A section score can be None when that section was not available
    for a valid comparison.
    """

    overall_similarity: float

    skill_similarity: Optional[float]
    experience_similarity: Optional[float]
    project_similarity: Optional[float]

    threshold: float
    matched: bool

    model_name: str

    # Indicates which sections contributed to the final score.
    skill_available: bool
    experience_available: bool
    project_available: bool

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the result into a normal dictionary.
        """
        return asdict(self)


# ============================================================
# SEMANTIC MATCHING ENGINE
# ============================================================

class SemanticMatchingEngine:
    """
    Embedding-based resume-to-job semantic matching engine.

    The engine converts text into sentence embeddings and compares
    the resulting vectors using cosine similarity.

    Missing sections are skipped instead of being represented by
    artificial placeholder text.
    """

    DEFAULT_MODEL = "all-MiniLM-L6-v2"

    # Default relative weights.
    SKILL_WEIGHT = 0.50
    EXPERIENCE_WEIGHT = 0.30
    PROJECT_WEIGHT = 0.20

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        threshold: float = 0.55,
    ) -> None:

        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                "threshold must be between 0.0 and 1.0"
            )

        self.model_name = model_name
        self.threshold = threshold

        print(
            f"Loading semantic model: "
            f"sentence-transformers/{self.model_name}"
        )

        self.model = SentenceTransformer(
            self.model_name
        )

        print("Semantic model loaded successfully.")

    # ========================================================
    # EMBEDDING
    # ========================================================

    def encode_text(
        self,
        text: str,
    ):
        """
        Convert text into a normalized sentence embedding.

        Raises:
            ValueError: when text is empty.
        """

        if text is None or not str(text).strip():
            raise ValueError(
                "Text must not be empty."
            )

        return self.model.encode(
            str(text).strip(),
            normalize_embeddings=True,
        )

    def encode_texts(self, texts):
        """
        Convert multiple non-empty text strings into embeddings.
        """

        if not texts:
            raise ValueError(
                "texts must contain at least one item."
            )

        cleaned_texts = [
            str(text).strip()
            for text in texts
            if text is not None and str(text).strip()
        ]

        if not cleaned_texts:
            raise ValueError(
                "No valid text values were supplied."
            )

        return self.model.encode(
            cleaned_texts,
            normalize_embeddings=True,
        )

    # ========================================================
    # TEXT AVAILABILITY
    # ========================================================

    @staticmethod
    def has_text(text: Optional[str]) -> bool:
        """
        Check whether a section contains real text.
        """

        return (
            text is not None
            and bool(str(text).strip())
        )

    # ========================================================
    # SIMILARITY
    # ========================================================

    def similarity(
        self,
        text_a: str,
        text_b: str,
    ) -> float:
        """
        Calculate semantic similarity between two non-empty texts.

        Because embeddings are normalized, cosine similarity is
        obtained from their dot product.
        """

        embedding_a = self.encode_text(text_a)
        embedding_b = self.encode_text(text_b)

        similarity_value = float(
            embedding_a @ embedding_b
        )

        return max(
            -1.0,
            min(1.0, similarity_value),
        )

    # ========================================================
    # EMBEDDING SIMILARITY
    # ========================================================

    def embedding_similarity(
        self,
        embedding_a,
        embedding_b,
    ) -> float:
        """
        Calculate cosine similarity directly from embeddings.
        """

        similarity_value = float(
            embedding_a @ embedding_b
        )

        return max(
            -1.0,
            min(1.0, similarity_value),
        )

    # ========================================================
    # SECTION COMPARISON
    # ========================================================

    def compare_sections(
        self,
        resume_skills: Optional[str],
        jd_skills: Optional[str],
        resume_experience: Optional[str],
        jd_experience: Optional[str],
        resume_projects: Optional[str],
        jd_projects: Optional[str],
    ) -> Dict[str, Optional[float]]:
        """
        Compare the three Day 12 target areas.

        A section is only compared when BOTH the resume and JD
        contain actual text.

        Missing sections return None instead of a fabricated score.
        """

        # ----------------------------------------------------
        # Skills
        # ----------------------------------------------------

        if (
            self.has_text(resume_skills)
            and self.has_text(jd_skills)
        ):
            skill_similarity = round(
                self.similarity(
                    resume_skills,
                    jd_skills,
                ),
                4,
            )
        else:
            skill_similarity = None

        # ----------------------------------------------------
        # Experience
        # ----------------------------------------------------

        if (
            self.has_text(resume_experience)
            and self.has_text(jd_experience)
        ):
            experience_similarity = round(
                self.similarity(
                    resume_experience,
                    jd_experience,
                ),
                4,
            )
        else:
            experience_similarity = None

        # ----------------------------------------------------
        # Projects / Context
        # ----------------------------------------------------

        if (
            self.has_text(resume_projects)
            and self.has_text(jd_projects)
        ):
            project_similarity = round(
                self.similarity(
                    resume_projects,
                    jd_projects,
                ),
                4,
            )
        else:
            project_similarity = None

        return {
            "skill_similarity": skill_similarity,
            "experience_similarity": experience_similarity,
            "project_similarity": project_similarity,
        }

    # ========================================================
    # DYNAMIC WEIGHTED SCORE
    # ========================================================

    def calculate_overall_similarity(
        self,
        skill_similarity: Optional[float],
        experience_similarity: Optional[float],
        project_similarity: Optional[float],
        skill_weight: float = SKILL_WEIGHT,
        experience_weight: float = EXPERIENCE_WEIGHT,
        project_weight: float = PROJECT_WEIGHT,
    ) -> float:
        """
        Calculate a weighted semantic similarity score.

        Only available sections participate in the calculation.

        Example:

            Skills available       0.50
            Experience unavailable 0.30  -> skipped
            Projects available     0.20

        Effective weights:

            Skills   = 0.50 / 0.70
            Projects = 0.20 / 0.70
        """

        available_scores = []
        available_weights = []

        if skill_similarity is not None:
            available_scores.append(
                skill_similarity
            )
            available_weights.append(
                skill_weight
            )

        if experience_similarity is not None:
            available_scores.append(
                experience_similarity
            )
            available_weights.append(
                experience_weight
            )

        if project_similarity is not None:
            available_scores.append(
                project_similarity
            )
            available_weights.append(
                project_weight
            )

        if not available_scores:
            raise ValueError(
                "No valid semantic sections are available "
                "for scoring."
            )

        weights_total = sum(
            available_weights
        )

        if weights_total <= 0:
            raise ValueError(
                "Available semantic weights must sum to "
                "a positive value."
            )

        normalized_weights = [
            weight / weights_total
            for weight in available_weights
        ]

        overall = sum(
            score * weight
            for score, weight in zip(
                available_scores,
                normalized_weights,
            )
        )

        return round(
            float(overall),
            4,
        )

    # ========================================================
    # THRESHOLD CLASSIFICATION
    # ========================================================

    def classify_similarity(
        self,
        similarity_score: float,
        threshold: Optional[float] = None,
    ) -> bool:
        """
        Determine whether a similarity score meets the threshold.
        """

        active_threshold = (
            self.threshold
            if threshold is None
            else threshold
        )

        if not 0.0 <= active_threshold <= 1.0:
            raise ValueError(
                "threshold must be between 0.0 and 1.0"
            )

        return similarity_score >= active_threshold

    # ========================================================
    # COMPLETE MATCH
    # ========================================================

    def match(
        self,
        resume_skills: Optional[str],
        jd_skills: Optional[str],
        resume_experience: Optional[str],
        jd_experience: Optional[str],
        resume_projects: Optional[str],
        jd_projects: Optional[str],
        threshold: Optional[float] = None,
    ) -> SemanticMatchResult:
        """
        Perform a complete semantic resume-to-JD match.
        """

        active_threshold = (
            self.threshold
            if threshold is None
            else threshold
        )

        # ----------------------------------------------------
        # Calculate section-level similarities
        # ----------------------------------------------------

        section_scores = self.compare_sections(
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            resume_experience=resume_experience,
            jd_experience=jd_experience,
            resume_projects=resume_projects,
            jd_projects=jd_projects,
        )

        # ----------------------------------------------------
        # Validate that at least one section is available
        # ----------------------------------------------------

        if not any(
            value is not None
            for value in section_scores.values()
        ):
            raise ValueError(
                "No valid semantic sections are available "
                "for matching."
            )

        # ----------------------------------------------------
        # Calculate final score using only available sections
        # ----------------------------------------------------

        overall_similarity = (
            self.calculate_overall_similarity(
                skill_similarity=section_scores[
                    "skill_similarity"
                ],
                experience_similarity=section_scores[
                    "experience_similarity"
                ],
                project_similarity=section_scores[
                    "project_similarity"
                ],
            )
        )

        # ----------------------------------------------------
        # Classification
        # ----------------------------------------------------

        matched = self.classify_similarity(
            overall_similarity,
            threshold=active_threshold,
        )

        # ----------------------------------------------------
        # Availability flags
        # ----------------------------------------------------

        skill_available = (
            section_scores["skill_similarity"]
            is not None
        )

        experience_available = (
            section_scores["experience_similarity"]
            is not None
        )

        project_available = (
            section_scores["project_similarity"]
            is not None
        )

        return SemanticMatchResult(
            overall_similarity=overall_similarity,

            skill_similarity=section_scores[
                "skill_similarity"
            ],

            experience_similarity=section_scores[
                "experience_similarity"
            ],

            project_similarity=section_scores[
                "project_similarity"
            ],

            threshold=active_threshold,
            matched=matched,
            model_name=self.model_name,

            skill_available=skill_available,
            experience_available=experience_available,
            project_available=project_available,
        )


# ============================================================
# STANDALONE DEMONSTRATION
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("DAY 12 - SEMANTIC MATCHING ENGINE")
    print("=" * 60)

    engine = SemanticMatchingEngine(
        threshold=0.55
    )

    # --------------------------------------------------------
    # Basic semantic test
    # --------------------------------------------------------

    text_a = (
        "Python developer with Django and REST API experience"
    )

    text_b = (
        "Software engineer experienced in Python web APIs"
    )

    basic_similarity = engine.similarity(
        text_a,
        text_b,
    )

    print()
    print("BASIC SEMANTIC TEST")
    print("-" * 60)

    print("Text A:", text_a)
    print("Text B:", text_b)

    print(
        "Similarity:",
        round(basic_similarity, 4),
    )

    # --------------------------------------------------------
    # Section-level semantic test
    # --------------------------------------------------------

    result = engine.match(

        resume_skills=(
            "Python, Django, REST APIs, SQL, Git, "
            "Machine Learning"
        ),

        jd_skills=(
            "Python, Django, REST APIs, SQL, "
            "Git and backend development"
        ),

        resume_experience=(
            "Developed Python applications and REST APIs. "
            "Worked with Django and SQL databases."
        ),

        jd_experience=(
            "Experience building Python web applications, "
            "REST APIs and database-backed systems."
        ),

        resume_projects=(
            "Built a Django healthcare API and an ML "
            "classification project."
        ),

        jd_projects=(
            "Develop backend services and integrate "
            "machine-learning functionality."
        ),
    )

    print()
    print("SECTION-LEVEL SEMANTIC MATCH")
    print("-" * 60)

    for key, value in result.to_dict().items():
        print(
            f"{key}: {value}"
        )

    # --------------------------------------------------------
    # Missing-section demonstration
    # --------------------------------------------------------

    print()
    print("MISSING-SECTION TEST")
    print("-" * 60)

    missing_section_result = engine.match(

        resume_skills="Python, SQL, Git",

        jd_skills="Python, SQL, Git and software development",

        resume_experience="",

        jd_experience="",

        resume_projects=(
            "Built a Python web application using SQL."
        ),

        jd_projects=(
            "Develop and maintain Python applications "
            "using databases."
        ),
    )

    for key, value in missing_section_result.to_dict().items():
        print(
            f"{key}: {value}"
        )

    print()
    print("=" * 60)
    print("DAY 12 SEMANTIC TEST COMPLETE")
    print("=" * 60)