"""
Day 14 - Candidate Ranking & Shortlisting

Purpose:
    Rank candidates using the ATS score produced by Day 13.

Responsibilities:
    1. Sort candidates by ATS score.
    2. Assign candidate ranks.
    3. Apply configurable shortlisting thresholds.
    4. Classify candidates into:
         - SHORTLIST
         - REVIEW
         - REJECT
    5. Generate top-N candidates.
    6. Produce recruiter-friendly output.

Notes:
    - Candidate scores are expected to be normalized between 0 and 1.
    - Threshold values are configurable implementation defaults.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional


@dataclass(frozen=True)
class RankingThresholds:
    """
    Configurable thresholds for candidate classification.

    Scores are normalized between 0 and 1.

    Default implementation:
        >= 0.70 -> SHORTLIST
        >= 0.50 -> REVIEW
        <  0.50 -> REJECT
    """

    shortlist: float = 0.70
    review: float = 0.50

    def __post_init__(self) -> None:
        if not 0.0 <= self.review <= 1.0:
            raise ValueError("Review threshold must be between 0 and 1.")

        if not 0.0 <= self.shortlist <= 1.0:
            raise ValueError("Shortlist threshold must be between 0 and 1.")

        if self.shortlist < self.review:
            raise ValueError(
                "Shortlist threshold must be greater than or equal "
                "to the review threshold."
            )


@dataclass
class RankedCandidate:
    """
    Standard recruiter-friendly ranked candidate record.
    """

    rank: int
    candidate_id: str
    candidate_name: str
    score: float
    score_percentage: float
    status: str
    role: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return the candidate as a dictionary."""
        return asdict(self)


class CandidateRankingEngine:
    """
    Day 14 candidate ranking and shortlisting engine.

    The engine consumes candidate results produced by the Day 13
    ATS scoring framework.
    """

    VALID_STATUSES = {"SHORTLIST", "REVIEW", "REJECT"}

    def __init__(
        self,
        thresholds: Optional[RankingThresholds] = None,
    ) -> None:
        self.thresholds = thresholds or RankingThresholds()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_score(score: Any) -> float:
        """
        Validate and normalize an ATS score.

        Expected format:
            0.0 <= score <= 1.0
        """

        if isinstance(score, bool):
            raise ValueError("Candidate score must be numeric.")

        try:
            numeric_score = float(score)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid candidate score: {score!r}"
            ) from exc

        if not 0.0 <= numeric_score <= 1.0:
            raise ValueError(
                f"Candidate score must be between 0 and 1. "
                f"Received: {numeric_score}"
            )

        return numeric_score

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def classify_candidate(self, score: float) -> str:
        """
        Classify a candidate according to the configured thresholds.
        """

        score = self._validate_score(score)

        if score >= self.thresholds.shortlist:
            return "SHORTLIST"

        if score >= self.thresholds.review:
            return "REVIEW"

        return "REJECT"

    # ------------------------------------------------------------------
    # Ranking
    # ------------------------------------------------------------------

    def rank_candidates(
        self,
        candidates: Iterable[Dict[str, Any]],
        score_key: str = "final_score",
    ) -> List[Dict[str, Any]]:
        """
        Rank candidates in descending order of ATS score.

        Parameters:
            candidates:
                Iterable of Day 13 candidate-score dictionaries.

            score_key:
                Dictionary key containing the normalized ATS score.

        Returns:
            List of ranked candidate dictionaries.

        Notes:
            Tied candidates retain their original input order.
        """

        candidate_list = list(candidates)

        if not candidate_list:
            return []

        prepared_candidates: List[Dict[str, Any]] = []

        for index, candidate in enumerate(candidate_list):
            if not isinstance(candidate, dict):
                raise TypeError(
                    f"Candidate at index {index} must be a dictionary."
                )

            if score_key not in candidate:
                raise KeyError(
                    f"Candidate at index {index} is missing "
                    f"required score key: {score_key!r}"
                )

            score = self._validate_score(candidate[score_key])

            candidate_copy = dict(candidate)
            candidate_copy[score_key] = score
            candidate_copy["_original_index"] = index

            prepared_candidates.append(candidate_copy)

        # Python's sort is stable, so tied candidates retain their
        # original order because we only sort by score.
        prepared_candidates.sort(
            key=lambda item: item[score_key],
            reverse=True,
        )

        ranked_output: List[Dict[str, Any]] = []

        for rank, candidate in enumerate(
            prepared_candidates,
            start=1,
        ):
            candidate_copy = dict(candidate)

            score = candidate_copy[score_key]

            candidate_copy["rank"] = rank
            candidate_copy["status"] = self.classify_candidate(score)

            candidate_copy["score_percentage"] = round(
                score * 100,
                2,
            )

            candidate_copy.pop("_original_index", None)

            ranked_output.append(candidate_copy)

        return ranked_output

    # ------------------------------------------------------------------
    # Shortlisting
    # ------------------------------------------------------------------

    def shortlist_candidates(
        self,
        ranked_candidates: Iterable[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Return only candidates classified as SHORTLIST.
        """

        return [
            dict(candidate)
            for candidate in ranked_candidates
            if candidate.get("status") == "SHORTLIST"
        ]

    # ------------------------------------------------------------------
    # Review candidates
    # ------------------------------------------------------------------

    def review_candidates(
        self,
        ranked_candidates: Iterable[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Return candidates requiring recruiter review.
        """

        return [
            dict(candidate)
            for candidate in ranked_candidates
            if candidate.get("status") == "REVIEW"
        ]

    # ------------------------------------------------------------------
    # Rejected candidates
    # ------------------------------------------------------------------

    def rejected_candidates(
        self,
        ranked_candidates: Iterable[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Return candidates falling below the review threshold.
        """

        return [
            dict(candidate)
            for candidate in ranked_candidates
            if candidate.get("status") == "REJECT"
        ]

    # ------------------------------------------------------------------
    # Top-N candidates
    # ------------------------------------------------------------------

    def top_candidates(
        self,
        ranked_candidates: Iterable[Dict[str, Any]],
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Return the top N candidates from an already-ranked list.
        """

        if isinstance(top_n, bool) or not isinstance(top_n, int):
            raise ValueError("top_n must be an integer.")

        if top_n <= 0:
            raise ValueError("top_n must be greater than 0.")

        return [
            dict(candidate)
            for candidate in list(ranked_candidates)[:top_n]
        ]

    # ------------------------------------------------------------------
    # Recruiter-friendly output
    # ------------------------------------------------------------------

    def recruiter_summary(
        self,
        ranked_candidates: Iterable[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate a concise recruiter-oriented summary.
        """

        candidates = list(ranked_candidates)

        shortlist = self.shortlist_candidates(candidates)
        review = self.review_candidates(candidates)
        rejected = self.rejected_candidates(candidates)

        top_candidate = candidates[0] if candidates else None

        top_candidate_summary: Optional[Dict[str, Any]] = None

        if top_candidate is not None:
            top_candidate_summary = {
                "rank": top_candidate.get("rank"),
                "candidate_id": top_candidate.get(
                    "candidate_id"
                ),
                "candidate_name": top_candidate.get(
                    "candidate_name",
                    top_candidate.get("candidate_id", "Unknown"),
                ),
                "score_percentage": top_candidate.get(
                    "score_percentage"
                ),
                "status": top_candidate.get("status"),
            }

        return {
            "total_candidates": len(candidates),
            "shortlisted_count": len(shortlist),
            "review_count": len(review),
            "rejected_count": len(rejected),
            "top_candidate": top_candidate_summary,
            "thresholds": {
                "shortlist": self.thresholds.shortlist,
                "review": self.thresholds.review,
            },
        }

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def process_candidates(
        self,
        candidates: Iterable[Dict[str, Any]],
        score_key: str = "final_score",
        top_n: int = 5,
    ) -> Dict[str, Any]:
        """
        Execute the complete Day 14 ranking pipeline.

        Pipeline:
            Candidate scores
                ↓
            Ranking
                ↓
            Classification
                ↓
            Shortlist / Review / Reject
                ↓
            Top-N candidates
                ↓
            Recruiter summary
        """

        ranked = self.rank_candidates(
            candidates=candidates,
            score_key=score_key,
        )

        shortlisted = self.shortlist_candidates(ranked)
        review = self.review_candidates(ranked)
        rejected = self.rejected_candidates(ranked)
        top = self.top_candidates(
            ranked_candidates=ranked,
            top_n=top_n,
        )

        summary = self.recruiter_summary(ranked)

        return {
            "ranked_candidates": ranked,
            "shortlisted_candidates": shortlisted,
            "review_candidates": review,
            "rejected_candidates": rejected,
            "top_candidates": top,
            "recruiter_summary": summary,
        }