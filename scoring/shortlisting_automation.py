"""
Day 14 - Shortlisting Automation Module

Purpose:
    Automate candidate shortlisting decisions after ATS ranking.

Responsibilities:
    1. Apply configurable score thresholds.
    2. Separate candidates into:
         - SHORTLIST
         - REVIEW
         - REJECT
    3. Generate shortlist-ready candidate records.
    4. Generate recruiter review records.
    5. Generate auto-rejected records.
    6. Generate a recruiter-friendly decision summary.

This module works with ranked candidate records produced by
CandidateRankingEngine.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from scoring.resume_ranking_engine import (
    CandidateRankingEngine,
    RankingThresholds,
)


class ShortlistingAutomation:
    """
    Automates recruitment decisions using ATS score thresholds.

    Default implementation thresholds:
        >= 0.70 -> SHORTLIST
        >= 0.50 -> REVIEW
        <  0.50 -> REJECT

    These values are implementation defaults and are configurable.
    """

    def __init__(
        self,
        shortlist_threshold: float = 0.70,
        review_threshold: float = 0.50,
    ) -> None:

        self.thresholds = RankingThresholds(
            shortlist=shortlist_threshold,
            review=review_threshold,
        )

        self.ranking_engine = CandidateRankingEngine(
            thresholds=self.thresholds
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_candidate(candidate: Dict[str, Any]) -> None:
        """
        Validate the minimum information required from a ranked
        candidate.
        """

        if not isinstance(candidate, dict):
            raise TypeError(
                "Each candidate must be represented as a dictionary."
            )

        if "final_score" not in candidate:
            raise KeyError(
                "Candidate is missing required field: 'final_score'"
            )

    # ------------------------------------------------------------------
    # Candidate classification
    # ------------------------------------------------------------------

    def classify_candidate(
        self,
        candidate: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Classify a single candidate.

        Returns:
            A copy of the candidate containing status and score
            percentage.
        """

        self._validate_candidate(candidate)

        candidate_copy = dict(candidate)

        score = float(candidate_copy["final_score"])

        # Validate score using the ranking engine.
        status = self.ranking_engine.classify_candidate(score)

        candidate_copy["status"] = status
        candidate_copy["score_percentage"] = round(
            score * 100,
            2,
        )

        return candidate_copy

    # ------------------------------------------------------------------
    # Process all candidates
    # ------------------------------------------------------------------

    def process(
        self,
        candidates: Iterable[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Classify all candidates into recruitment decision zones.

        Returns:
            Dictionary containing shortlist, review, and reject lists.
        """

        shortlisted: List[Dict[str, Any]] = []
        review: List[Dict[str, Any]] = []
        rejected: List[Dict[str, Any]] = []

        for candidate in candidates:

            classified = self.classify_candidate(candidate)

            status = classified["status"]

            if status == "SHORTLIST":
                shortlisted.append(classified)

            elif status == "REVIEW":
                review.append(classified)

            elif status == "REJECT":
                rejected.append(classified)

        return {
            "shortlisted": shortlisted,
            "review": review,
            "rejected": rejected,
        }

    # ------------------------------------------------------------------
    # Shortlist limit
    # ------------------------------------------------------------------

    def generate_shortlist(
        self,
        candidates: Iterable[Dict[str, Any]],
        maximum_candidates: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate the final shortlist.

        Candidates are sorted by ATS score before applying the optional
        maximum shortlist size.
        """

        processed = self.process(candidates)

        shortlist = processed["shortlisted"]

        shortlist.sort(
            key=lambda candidate: candidate["final_score"],
            reverse=True,
        )

        if maximum_candidates is not None:

            if (
                isinstance(maximum_candidates, bool)
                or not isinstance(maximum_candidates, int)
            ):
                raise ValueError(
                    "maximum_candidates must be an integer."
                )

            if maximum_candidates <= 0:
                raise ValueError(
                    "maximum_candidates must be greater than 0."
                )

            shortlist = shortlist[:maximum_candidates]

        return shortlist

    # ------------------------------------------------------------------
    # Review queue
    # ------------------------------------------------------------------

    def generate_review_queue(
        self,
        candidates: Iterable[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Generate candidates requiring recruiter review.

        Review candidates are ordered by ATS score from highest
        to lowest.
        """

        processed = self.process(candidates)

        review = processed["review"]

        review.sort(
            key=lambda candidate: candidate["final_score"],
            reverse=True,
        )

        return review

    # ------------------------------------------------------------------
    # Reject queue
    # ------------------------------------------------------------------

    def generate_rejection_queue(
        self,
        candidates: Iterable[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Generate candidates eligible for automated rejection.

        Rejected candidates are ordered by ATS score from highest
        to lowest so recruiters can still inspect borderline cases.
        """

        processed = self.process(candidates)

        rejected = processed["rejected"]

        rejected.sort(
            key=lambda candidate: candidate["final_score"],
            reverse=True,
        )

        return rejected

    # ------------------------------------------------------------------
    # Recruiter decision summary
    # ------------------------------------------------------------------

    def generate_decision_summary(
        self,
        candidates: Iterable[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate a recruiter-friendly decision summary.
        """

        candidate_list = list(candidates)

        processed = self.process(candidate_list)

        shortlisted = processed["shortlisted"]
        review = processed["review"]
        rejected = processed["rejected"]

        total = len(candidate_list)

        return {
            "total_candidates": total,
            "shortlisted": len(shortlisted),
            "review_required": len(review),
            "auto_rejected": len(rejected),
            "shortlist_threshold": self.thresholds.shortlist,
            "review_threshold": self.thresholds.review,
            "decision_zones": {
                "SHORTLIST": {
                    "minimum_score": self.thresholds.shortlist,
                    "maximum_score": 1.0,
                },
                "REVIEW": {
                    "minimum_score": self.thresholds.review,
                    "maximum_score": self.thresholds.shortlist,
                },
                "REJECT": {
                    "minimum_score": 0.0,
                    "maximum_score": self.thresholds.review,
                },
            },
        }

    # ------------------------------------------------------------------
    # Full automation pipeline
    # ------------------------------------------------------------------

    def automate(
        self,
        candidates: Iterable[Dict[str, Any]],
        maximum_shortlist: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute the complete shortlisting automation process.

        Pipeline:

            Candidate Scores
                   ↓
              Classification
                   ↓
          ┌────────┼─────────┐
          ↓        ↓         ↓
       SHORTLIST REVIEW    REJECT
          ↓        ↓         ↓
      Final List Review  Auto-Reject
                   ↓
          Recruiter Summary
        """

        candidate_list = list(candidates)

        processed = self.process(candidate_list)

        shortlist = self.generate_shortlist(
            candidate_list,
            maximum_candidates=maximum_shortlist,
        )

        review_queue = self.generate_review_queue(
            candidate_list
        )

        rejection_queue = self.generate_rejection_queue(
            candidate_list
        )

        summary = self.generate_decision_summary(
            candidate_list
        )

        return {
            "shortlist": shortlist,
            "review_queue": review_queue,
            "rejection_queue": rejection_queue,
            "summary": summary,
        }