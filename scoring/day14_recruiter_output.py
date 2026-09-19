"""
Day 14 - Recruiter-Friendly Ranked Candidate Output

Purpose:
    Generate a clean recruiter-facing candidate ranking report
    from ATS scores.

This module consumes candidate scores produced by the Day 13
ATS scoring framework and uses the Day 14 ranking and shortlisting
engine to generate:

    1. Ranked candidate table
    2. Shortlist
    3. Review queue
    4. Auto-rejection queue
    5. Top candidate list
    6. Recruiter summary
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from scoring.resume_ranking_engine import (
    CandidateRankingEngine,
    RankingThresholds,
)


def print_separator(char: str = "-", length: int = 90) -> None:
    """Print a visual separator."""

    print(char * length)


def print_ranked_output(
    ranked_candidates: List[Dict[str, Any]],
) -> None:
    """Display the complete ranked candidate table."""

    print("\n")
    print_separator("=")
    print("DAY 14 - RANKED CANDIDATE OUTPUT")
    print_separator("=")

    print(
        f"{'Rank':<8}"
        f"{'Candidate':<25}"
        f"{'ATS Score':<15}"
        f"{'Status':<12}"
        f"{'Role':<25}"
    )

    print_separator()

    for candidate in ranked_candidates:

        rank = candidate.get("rank", "-")
        name = candidate.get(
            "candidate_name",
            candidate.get("candidate_id", "Unknown"),
        )
        score = candidate.get(
            "score_percentage",
            candidate.get("final_score", 0) * 100,
        )
        status = candidate.get("status", "UNKNOWN")
        role = candidate.get("role", "N/A")

        print(
            f"{rank:<8}"
            f"{str(name):<25}"
            f"{float(score):>7.2f}%       "
            f"{status:<12}"
            f"{str(role):<25}"
        )


def print_candidate_zone(
    title: str,
    candidates: List[Dict[str, Any]],
) -> None:
    """Display one recruitment decision zone."""

    print("\n")
    print_separator("=")
    print(title)
    print_separator("=")

    if not candidates:
        print("No candidates in this zone.")
        return

    for candidate in candidates:

        rank = candidate.get("rank", "-")
        name = candidate.get(
            "candidate_name",
            candidate.get("candidate_id", "Unknown"),
        )
        score = candidate.get(
            "score_percentage",
            candidate.get("final_score", 0) * 100,
        )

        print(
            f"Rank #{rank} | "
            f"{name} | "
            f"{float(score):.2f}%"
        )


def print_top_candidates(
    candidates: List[Dict[str, Any]],
) -> None:
    """Display the Top-N candidate list."""

    print("\n")
    print_separator("=")
    print("TOP CANDIDATES")
    print_separator("=")

    if not candidates:
        print("No candidates available.")
        return

    for candidate in candidates:

        rank = candidate.get("rank", "-")
        name = candidate.get(
            "candidate_name",
            candidate.get("candidate_id", "Unknown"),
        )
        score = candidate.get(
            "score_percentage",
            candidate.get("final_score", 0) * 100,
        )
        status = candidate.get("status", "UNKNOWN")

        print(
            f"#{rank} "
            f"{name:<25} "
            f"{float(score):>6.2f}% "
            f"| {status}"
        )


def print_recruiter_summary(
    summary: Dict[str, Any],
) -> None:
    """Display the recruiter summary."""

    print("\n")
    print_separator("=")
    print("RECRUITER SUMMARY")
    print_separator("=")

    print(
        f"Total candidates : "
        f"{summary.get('total_candidates', 0)}"
    )

    print(
        f"Shortlisted      : "
        f"{summary.get('shortlisted_count', 0)}"
    )

    print(
        f"Review required  : "
        f"{summary.get('review_count', 0)}"
    )

    print(
        f"Auto-rejected    : "
        f"{summary.get('rejected_count', 0)}"
    )

    top_candidate = summary.get("top_candidate")

    if top_candidate:

        print(
            f"Top-ranked       : "
            f"{top_candidate.get('candidate_name', 'Unknown')} "
            f"({top_candidate.get('score_percentage', 0):.2f}%)"
        )

    thresholds = summary.get("thresholds", {})

    print(
        f"Shortlist limit  : "
        f"{thresholds.get('shortlist', 0) * 100:.0f}%"
    )

    print(
        f"Review limit     : "
        f"{thresholds.get('review', 0) * 100:.0f}%"
    )


def save_json_output(
    result: Dict[str, Any],
    output_path: str = "outputs/day14_ranked_candidates.json",
) -> Path:
    """
    Save the complete recruiter-friendly output as JSON.
    """

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return path


def main() -> None:
    """
    Execute the Day 14 recruiter output demonstration.

    The candidate scores below are demonstration inputs.
    In the production workflow, these values should come from
    Day 13 ATS scoring results.
    """

    candidates = [
        {
            "candidate_id": "CAND-001",
            "candidate_name": "Asha",
            "role": "Python Developer",
            "final_score": 0.91,
        },
        {
            "candidate_id": "CAND-002",
            "candidate_name": "Meera",
            "role": "Python Developer",
            "final_score": 0.83,
        },
        {
            "candidate_id": "CAND-003",
            "candidate_name": "Arjun",
            "role": "Python Developer",
            "final_score": 0.68,
        },
        {
            "candidate_id": "CAND-004",
            "candidate_name": "Nikhil",
            "role": "Python Developer",
            "final_score": 0.55,
        },
        {
            "candidate_id": "CAND-005",
            "candidate_name": "Rahul",
            "role": "Python Developer",
            "final_score": 0.49,
        },
        {
            "candidate_id": "CAND-006",
            "candidate_name": "Vivek",
            "role": "Python Developer",
            "final_score": 0.31,
        },
    ]

    # Configurable implementation defaults.
    thresholds = RankingThresholds(
        shortlist=0.70,
        review=0.50,
    )

    engine = CandidateRankingEngine(
        thresholds=thresholds
    )

    # Complete Day 14 processing.
    result = engine.process_candidates(
        candidates=candidates,
        score_key="final_score",
        top_n=5,
    )

    ranked_candidates = result["ranked_candidates"]

    print_ranked_output(
        ranked_candidates
    )

    print_candidate_zone(
        "SHORTLISTED CANDIDATES",
        result["shortlisted_candidates"],
    )

    print_candidate_zone(
        "REVIEW QUEUE",
        result["review_candidates"],
    )

    print_candidate_zone(
        "AUTO-REJECTION QUEUE",
        result["rejected_candidates"],
    )

    print_top_candidates(
        result["top_candidates"]
    )

    print_recruiter_summary(
        result["recruiter_summary"]
    )

    # Save complete structured output.
    output_path = save_json_output(result)

    print("\n")
    print_separator("=")
    print("OUTPUT FILE")
    print_separator("=")
    print(output_path)

    print("\n")
    print_separator("=")
    print("DAY 14 RECRUITER OUTPUT GENERATION COMPLETE")
    print_separator("=")


if __name__ == "__main__":
    main()