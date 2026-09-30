"""
Day 15 - Keyword Dependence Reduction

Purpose:
    Reduce over-dependence on exact keyword matching when evaluating
    candidate skills against job requirements.

Approach:
    1. Calculate exact skill coverage.
    2. Calculate semantic similarity between candidate and required skills.
    3. Combine both signals into a transparent hybrid score.

This module supplements keyword matching; it does not replace
job-relevant skill requirements.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from sentence_transformers import SentenceTransformer


@dataclass
class SkillMatchResult:
    """
    Transparent skill-matching result.
    """

    exact_match_score: float
    semantic_match_score: float
    hybrid_match_score: float
    matched_skills: List[str]
    semantic_matches: List[Dict[str, object]]

    def to_dict(self) -> Dict[str, object]:
        return {
            "exact_match_score": self.exact_match_score,
            "semantic_match_score": self.semantic_match_score,
            "hybrid_match_score": self.hybrid_match_score,
            "matched_skills": self.matched_skills,
            "semantic_matches": self.semantic_matches,
        }


class KeywordDependenceReducer:
    """
    Hybrid skill matcher.

    Default implementation:
        40% exact matching
        60% semantic matching

    These weights are implementation choices for this fairness module,
    not values specified by the Day 15 task document.
    """

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(
        self,
        exact_weight: float = 0.40,
        semantic_weight: float = 0.60,
        similarity_threshold: float = 0.65,
        model: Optional[SentenceTransformer] = None,
    ) -> None:

        if exact_weight < 0:
            raise ValueError(
                "exact_weight cannot be negative."
            )

        if semantic_weight < 0:
            raise ValueError(
                "semantic_weight cannot be negative."
            )

        total_weight = (
            exact_weight
            + semantic_weight
        )

        if total_weight <= 0:
            raise ValueError(
                "At least one matching weight must be greater than 0."
            )

        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError(
                "similarity_threshold must be between 0 and 1."
            )

        self.exact_weight = (
            exact_weight / total_weight
        )

        self.semantic_weight = (
            semantic_weight / total_weight
        )

        self.similarity_threshold = (
            similarity_threshold
        )

        self.model = model

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------

    def _get_model(self) -> SentenceTransformer:
        """
        Lazily load the semantic model.

        The same model instance is reused for subsequent comparisons.
        """

        if self.model is None:

            print(
                f"Loading semantic skill model: "
                f"{self.MODEL_NAME}"
            )

            self.model = SentenceTransformer(
                self.MODEL_NAME
            )

            print(
                "Semantic skill model loaded."
            )

        return self.model

    # ------------------------------------------------------------------
    # Text normalization
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_skill(
        skill: str,
    ) -> str:
        """
        Normalize skill wording for exact comparison.
        """

        return " ".join(
            str(skill)
            .strip()
            .lower()
            .split()
        )

    @classmethod
    def _normalize_skills(
        cls,
        skills: Iterable[str],
    ) -> List[str]:
        """
        Normalize and deduplicate skill names.
        """

        result: List[str] = []
        seen: set[str] = set()

        for skill in skills:

            if not skill:
                continue

            cleaned = str(skill).strip()

            if not cleaned:
                continue

            normalized = cls._normalize_skill(
                cleaned
            )

            if normalized in seen:
                continue

            seen.add(normalized)
            result.append(cleaned)

        return result

    # ------------------------------------------------------------------
    # Exact matching
    # ------------------------------------------------------------------

    def calculate_exact_match(
        self,
        candidate_skills: List[str],
        required_skills: List[str],
    ) -> Tuple[float, List[str]]:
        """
        Calculate exact required-skill coverage.

        Score:
            matched required skills / total required skills
        """

        if not required_skills:
            return 0.0, []

        candidate_normalized = {
            self._normalize_skill(skill)
            for skill in candidate_skills
        }

        matched_skills: List[str] = []

        for required in required_skills:

            required_normalized = (
                self._normalize_skill(
                    required
                )
            )

            if required_normalized in candidate_normalized:
                matched_skills.append(
                    required
                )

        score = (
            len(matched_skills)
            / len(required_skills)
        )

        return round(score, 4), matched_skills

    # ------------------------------------------------------------------
    # Semantic matching
    # ------------------------------------------------------------------

    def calculate_semantic_match(
        self,
        candidate_skills: List[str],
        required_skills: List[str],
    ) -> Tuple[
        float,
        List[Dict[str, object]],
    ]:
        """
        Calculate semantic coverage.

        Each required skill is compared against all candidate skills.
        The strongest semantic similarity is used for that required
        skill.

        This preserves requirement-level transparency.
        """

        if not required_skills:
            return 0.0, []

        if not candidate_skills:
            return 0.0, []

        model = self._get_model()

        candidate_embeddings = model.encode(
            candidate_skills,
            normalize_embeddings=True,
        )

        required_embeddings = model.encode(
            required_skills,
            normalize_embeddings=True,
        )

        similarities = (
            required_embeddings
            @ candidate_embeddings.T
        )

        semantic_values: List[float] = []

        semantic_matches: List[
            Dict[str, object]
        ] = []

        for index, required_skill in enumerate(
            required_skills
        ):

            row = similarities[index]

            best_index = int(
                row.argmax()
            )

            best_score = float(
                row[best_index]
            )

            best_candidate_skill = (
                candidate_skills[best_index]
            )

            # Cosine similarity can theoretically reach
            # values below zero. For skill coverage we keep
            # the normalized contribution within 0-1.
            normalized_score = max(
                0.0,
                min(
                    1.0,
                    best_score,
                ),
            )

            semantic_values.append(
                normalized_score
            )

            semantic_matches.append(
                {
                    "required_skill":
                        required_skill,
                    "best_candidate_skill":
                        best_candidate_skill,
                    "similarity":
                        round(
                            normalized_score,
                            4,
                        ),
                    "accepted":
                        normalized_score
                        >= self.similarity_threshold,
                }
            )

        semantic_score = (
            sum(semantic_values)
            / len(semantic_values)
        )

        return (
            round(
                semantic_score,
                4,
            ),
            semantic_matches,
        )

    # ------------------------------------------------------------------
    # Hybrid score
    # ------------------------------------------------------------------

    def calculate_hybrid_match(
        self,
        candidate_skills: Iterable[str],
        required_skills: Iterable[str],
    ) -> SkillMatchResult:
        """
        Calculate the transparent hybrid skill score.
        """

        candidate_list = (
            self._normalize_skills(
                candidate_skills
            )
        )

        required_list = (
            self._normalize_skills(
                required_skills
            )
        )

        exact_score, matched_skills = (
            self.calculate_exact_match(
                candidate_list,
                required_list,
            )
        )

        semantic_score, semantic_matches = (
            self.calculate_semantic_match(
                candidate_list,
                required_list,
            )
        )

        hybrid_score = (
            (
                self.exact_weight
                * exact_score
            )
            +
            (
                self.semantic_weight
                * semantic_score
            )
        )

        return SkillMatchResult(
            exact_match_score=round(
                exact_score,
                4,
            ),
            semantic_match_score=round(
                semantic_score,
                4,
            ),
            hybrid_match_score=round(
                hybrid_score,
                4,
            ),
            matched_skills=matched_skills,
            semantic_matches=semantic_matches,
        )