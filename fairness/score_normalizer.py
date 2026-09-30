"""
Day 15 - Scoring Normalization

Purpose:
    Normalize candidate ATS scores into a common 0-1 range.

The original ATS score is always preserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class NormalizedScore:
    """Original and normalized score."""

    original_score: float
    normalized_score: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "original_score": self.original_score,
            "normalized_score": self.normalized_score,
        }


class ScoreNormalizer:
    """
    Normalize scores using min-max normalization.

    Formula:

        normalized = (score - minimum) / (maximum - minimum)

    When all scores are identical, 0.5 is used to avoid
    division by zero.
    """

    @staticmethod
    def validate_score(score: Any) -> float:
        """Validate an ATS score between 0 and 1."""

        if isinstance(score, bool):
            raise ValueError("Score must be numeric.")

        try:
            numeric_score = float(score)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid score: {score!r}"
            ) from exc

        if not 0.0 <= numeric_score <= 1.0:
            raise ValueError(
                "Score must be between 0 and 1. "
                f"Received: {numeric_score}"
            )

        return numeric_score

    def normalize_value(
        self,
        score: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """Normalize one score."""

        score = self.validate_score(score)
        minimum = self.validate_score(minimum)
        maximum = self.validate_score(maximum)

        if minimum > maximum:
            raise ValueError(
                "Minimum score cannot exceed maximum score."
            )

        if minimum == maximum:
            return 0.5

        normalized = (
            (score - minimum)
            / (maximum - minimum)
        )

        return round(
            max(
                0.0,
                min(1.0, normalized),
            ),
            4,
        )

    def normalize_scores(
        self,
        scores: Iterable[float],
    ) -> List[NormalizedScore]:
        """Normalize a collection of scores."""

        score_list = [
            self.validate_score(score)
            for score in scores
        ]

        if not score_list:
            return []

        minimum = min(score_list)
        maximum = max(score_list)

        return [
            NormalizedScore(
                original_score=score,
                normalized_score=self.normalize_value(
                    score,
                    minimum,
                    maximum,
                ),
            )
            for score in score_list
        ]

    def normalize_candidates(
        self,
        candidates: Iterable[Dict[str, Any]],
        score_key: str = "final_score",
        normalized_key: str = "normalized_score",
    ) -> List[Dict[str, Any]]:
        """
        Add normalized scores to candidate records.

        The original final_score is not modified.
        """

        candidate_list = list(candidates)

        if not candidate_list:
            return []

        scores: List[float] = []

        for index, candidate in enumerate(candidate_list):

            if not isinstance(candidate, dict):
                raise TypeError(
                    f"Candidate at index {index} "
                    "must be a dictionary."
                )

            if score_key not in candidate:
                raise KeyError(
                    f"Candidate at index {index} "
                    f"is missing score key: {score_key!r}"
                )

            scores.append(
                self.validate_score(
                    candidate[score_key]
                )
            )

        normalized_scores = self.normalize_scores(
            scores
        )

        result: List[Dict[str, Any]] = []

        for candidate, normalized in zip(
            candidate_list,
            normalized_scores,
        ):
            candidate_copy = dict(candidate)

            candidate_copy[normalized_key] = (
                normalized.normalized_score
            )

            candidate_copy["normalized_percentage"] = (
                round(
                    normalized.normalized_score * 100,
                    2,
                )
            )

            result.append(candidate_copy)

        return result

    def ranking_order(
        self,
        candidates: Iterable[Dict[str, Any]],
        score_key: str = "final_score",
    ) -> List[str]:
        """Return candidate IDs ordered by original score."""

        candidate_list = list(candidates)

        ordered = sorted(
            candidate_list,
            key=lambda candidate: self.validate_score(
                candidate[score_key]
            ),
            reverse=True,
        )

        return [
            str(
                candidate.get(
                    "candidate_id",
                    index,
                )
            )
            for index, candidate in enumerate(
                ordered
            )
        ]