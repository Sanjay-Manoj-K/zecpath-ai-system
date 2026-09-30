"""
Day 15 - Bias Indicator Evaluation

Purpose:
    Evaluate simple, transparent indicators that can reveal whether
    candidate scoring or decision outcomes differ across explicitly
    supplied audit groups.

Important:
    This module does NOT infer protected attributes.
    Audit-group labels must be supplied explicitly as test/audit data.

The results are indicators for further investigation, not proof of
discrimination or legal compliance.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List


@dataclass
class GroupMetrics:
    """
    Aggregate metrics for one explicitly supplied audit group.
    """

    group: str
    candidate_count: int
    mean_score: float
    shortlist_rate: float
    review_rate: float
    reject_rate: float
    missing_signal_rate: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BiasIndicatorEvaluator:
    """
    Evaluate group-level outcome indicators.

    Expected candidate structure:

        {
            "candidate_id": "...",
            "final_score": 0.72,
            "status": "SHORTLIST",
            "audit_group": "group_a",
            "missing_signals": []
        }

    `audit_group` is an explicitly supplied audit label.
    """

    VALID_STATUSES = {
        "SHORTLIST",
        "REVIEW",
        "REJECT",
    }

    # --------------------------------------------------------------
    # Validation
    # --------------------------------------------------------------

    @staticmethod
    def validate_candidate(
        candidate: Dict[str, Any],
    ) -> None:
        """
        Validate a candidate audit record.
        """

        if not isinstance(candidate, dict):
            raise TypeError(
                "Each candidate must be a dictionary."
            )

        if "final_score" not in candidate:
            raise KeyError(
                "Candidate is missing 'final_score'."
            )

        if "audit_group" not in candidate:
            raise KeyError(
                "Candidate is missing 'audit_group'."
            )

        if "status" not in candidate:
            raise KeyError(
                "Candidate is missing 'status'."
            )

        score = float(
            candidate["final_score"]
        )

        if not 0.0 <= score <= 1.0:
            raise ValueError(
                "final_score must be between 0 and 1."
            )

        status = str(
            candidate["status"]
        ).upper()

        if status not in BiasIndicatorEvaluator.VALID_STATUSES:
            raise ValueError(
                f"Invalid status: {status}"
            )

    # --------------------------------------------------------------
    # Group metrics
    # --------------------------------------------------------------

    def calculate_group_metrics(
        self,
        candidates: Iterable[Dict[str, Any]],
        group: str,
    ) -> GroupMetrics:
        """
        Calculate aggregate outcome metrics for one audit group.
        """

        group_candidates = [
            candidate
            for candidate in candidates
            if str(
                candidate.get("audit_group")
            ) == str(group)
        ]

        if not group_candidates:
            raise ValueError(
                f"No candidates found for audit group: {group}"
            )

        count = len(group_candidates)

        total_score = sum(
            float(candidate["final_score"])
            for candidate in group_candidates
        )

        mean_score = (
            total_score / count
        )

        shortlist_count = sum(
            1
            for candidate in group_candidates
            if str(
                candidate["status"]
            ).upper() == "SHORTLIST"
        )

        review_count = sum(
            1
            for candidate in group_candidates
            if str(
                candidate["status"]
            ).upper() == "REVIEW"
        )

        reject_count = sum(
            1
            for candidate in group_candidates
            if str(
                candidate["status"]
            ).upper() == "REJECT"
        )

        missing_count = sum(
            1
            for candidate in group_candidates
            if candidate.get(
                "missing_signals"
            )
        )

        return GroupMetrics(
            group=str(group),
            candidate_count=count,
            mean_score=round(
                mean_score,
                4,
            ),
            shortlist_rate=round(
                shortlist_count / count,
                4,
            ),
            review_rate=round(
                review_count / count,
                4,
            ),
            reject_rate=round(
                reject_count / count,
                4,
            ),
            missing_signal_rate=round(
                missing_count / count,
                4,
            ),
        )

    # --------------------------------------------------------------
    # Compare groups
    # --------------------------------------------------------------

    @staticmethod
    def compare_groups(
        reference: GroupMetrics,
        comparison: GroupMetrics,
    ) -> Dict[str, Any]:
        """
        Compare two explicitly supplied audit groups.

        The differences are reported as indicators only.
        """

        mean_score_gap = (
            comparison.mean_score
            - reference.mean_score
        )

        shortlist_rate_gap = (
            comparison.shortlist_rate
            - reference.shortlist_rate
        )

        review_rate_gap = (
            comparison.review_rate
            - reference.review_rate
        )

        reject_rate_gap = (
            comparison.reject_rate
            - reference.reject_rate
        )

        missing_signal_gap = (
            comparison.missing_signal_rate
            - reference.missing_signal_rate
        )

        return {
            "reference_group": reference.group,
            "comparison_group": comparison.group,
            "mean_score_gap": round(
                mean_score_gap,
                4,
            ),
            "shortlist_rate_gap": round(
                shortlist_rate_gap,
                4,
            ),
            "review_rate_gap": round(
                review_rate_gap,
                4,
            ),
            "reject_rate_gap": round(
                reject_rate_gap,
                4,
            ),
            "missing_signal_rate_gap": round(
                missing_signal_gap,
                4,
            ),
        }

    # --------------------------------------------------------------
    # Full audit
    # --------------------------------------------------------------

    def evaluate(
        self,
        candidates: Iterable[Dict[str, Any]],
        reference_group: str,
    ) -> Dict[str, Any]:
        """
        Evaluate all groups against a reference group.
        """

        candidate_list = list(
            candidates
        )

        if not candidate_list:
            return {
                "groups": [],
                "comparisons": [],
            }

        for candidate in candidate_list:
            self.validate_candidate(
                candidate
            )

        groups = sorted(
            {
                str(
                    candidate["audit_group"]
                )
                for candidate in candidate_list
            }
        )

        if reference_group not in groups:
            raise ValueError(
                f"Reference group '{reference_group}' "
                "does not exist in the audit data."
            )

        metrics = {
            group:
                self.calculate_group_metrics(
                    candidate_list,
                    group,
                )
            for group in groups
        }

        reference_metrics = metrics[
            reference_group
        ]

        comparisons: List[
            Dict[str, Any]
        ] = []

        for group in groups:

            if group == reference_group:
                continue

            comparison = self.compare_groups(
                reference_metrics,
                metrics[group],
            )

            comparisons.append(
                comparison
            )

        return {
            "reference_group":
                reference_group,

            "groups": [
                metric.to_dict()
                for metric in metrics.values()
            ],

            "comparisons":
                comparisons,
        }

    # --------------------------------------------------------------
    # Indicator flags
    # --------------------------------------------------------------

    @staticmethod
    def identify_indicators(
        audit_result: Dict[str, Any],
        threshold: float = 0.10,
    ) -> List[Dict[str, Any]]:
        """
        Identify outcome differences that meet a configurable
        investigation threshold.

        The threshold is an implementation setting, not a legal
        standard.

        A 0.10 threshold means a difference of 10 percentage points
        or more for rate-based indicators.
        """

        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                "threshold must be between 0 and 1."
            )

        indicators: List[
            Dict[str, Any]
        ] = []

        for comparison in audit_result.get(
            "comparisons",
            [],
        ):

            for metric in (
                "shortlist_rate_gap",
                "review_rate_gap",
                "reject_rate_gap",
                "missing_signal_rate_gap",
            ):

                gap = abs(
                    float(
                        comparison[metric]
                    )
                )

                if gap >= threshold:

                    indicators.append(
                        {
                            "reference_group":
                                comparison[
                                    "reference_group"
                                ],
                            "comparison_group":
                                comparison[
                                    "comparison_group"
                                ],
                            "metric":
                                metric,
                            "absolute_gap":
                                round(
                                    gap,
                                    4,
                                ),
                            "flagged":
                                True,
                        }
                    )

            score_gap = abs(
                float(
                    comparison[
                        "mean_score_gap"
                    ]
                )
            )

            if score_gap >= threshold:

                indicators.append(
                    {
                        "reference_group":
                            comparison[
                                "reference_group"
                            ],
                        "comparison_group":
                            comparison[
                                "comparison_group"
                            ],
                        "metric":
                            "mean_score_gap",
                        "absolute_gap":
                            round(
                                score_gap,
                                4,
                            ),
                        "flagged":
                            True,
                    }
                )

        return indicators

    # --------------------------------------------------------------
    # Report
    # --------------------------------------------------------------

    def generate_report(
        self,
        candidates: Iterable[Dict[str, Any]],
        reference_group: str,
        threshold: float = 0.10,
    ) -> Dict[str, Any]:
        """
        Generate a complete bias-indicator audit report.
        """

        audit = self.evaluate(
            candidates,
            reference_group,
        )

        indicators = (
            self.identify_indicators(
                audit,
                threshold=threshold,
            )
        )

        return {
            **audit,
            "indicator_threshold":
                threshold,
            "indicators":
                indicators,
            "indicator_count":
                len(indicators),
        }