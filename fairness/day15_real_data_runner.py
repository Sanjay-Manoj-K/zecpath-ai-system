"""
Day 15 - Real Data Fairness Evaluation

Runs the Day 15 fairness components against the same real
Zecpath resumes used during Day 14.

Pipeline:
    Real Resume
        ->
    Resume Normalization + Personal Attribute Audit
        ->
    Day 13 ATS Score
        ->
    Hybrid Skill Matching
        ->
    Fairness-adjusted ATS Score
        ->
    Score Normalization
        ->
    Day 14 Ranking using fairness-adjusted score

Important:
    - Original Day 13 scores are preserved.
    - Fairness-adjusted scores are separate.
    - Personal-attribute masking is reported as a preprocessing/audit
      result and does not overwrite the original resume.
    - The 70% / 50% ranking thresholds are implementation defaults.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from fairness.day15_fairness_pipeline import (
    Day15FairnessPipeline,
)

from fairness.score_normalizer import (
    ScoreNormalizer,
)

from fairness.personal_attribute_masker import (
    PersonalAttributeMasker,
)

from scoring import day13_candidate_score as day13

from scoring.day14_end_to_end import (
    score_candidate,
)

from scoring.resume_ranking_engine import (
    CandidateRankingEngine,
    RankingThresholds,
)


def process_real_candidates(
    jd_path: Path,
    resume_paths: List[Path],
) -> Dict[str, Any]:
    """
    Process real resumes through the Day 13 + Day 15 + Day 14 flow.
    """

    fairness_pipeline = Day15FairnessPipeline()

    masker = PersonalAttributeMasker()

    score_normalizer = ScoreNormalizer()

    candidate_inputs: List[Dict[str, Any]] = []

    privacy_audits: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Step 1 - Run Day 13 on every real resume
    # ------------------------------------------------------------------

    for resume_path in resume_paths:

        print("\n" + "=" * 80)
        print("DAY 15 REAL CANDIDATE PROCESSING")
        print("=" * 80)

        print(
            f"Resume: {resume_path}"
        )

        # --------------------------------------------------------------
        # Resume extraction for Day 15 privacy audit
        # --------------------------------------------------------------

        resume_text = day13.extract_resume_text(
            str(resume_path)
        )

        if not resume_text.strip():
            print(
                "WARNING: Resume text is empty."
            )

        normalized_text = (
            day13_text_normalization(
                resume_text
            )
        )

        detected_attributes = (
            masker.detect_attributes(
                normalized_text
            )
        )

        masked_text = masker.mask_text(
            normalized_text
        )

        # Keep the audit output compact.
        privacy_audits.append(
            {
                "resume_path": str(
                    resume_path
                ),
                "detected_personal_attributes": (
                    detected_attributes
                ),
                "detected_attribute_count": len(
                    detected_attributes
                ),
                "masked_preview": (
                    masked_text[:1200]
                ),
            }
        )

        # --------------------------------------------------------------
        # Actual Day 13 scoring
        # --------------------------------------------------------------

        candidate = score_candidate(
            resume_path,
            jd_path,
        )

        candidate_inputs.append(
            candidate
        )

    if not candidate_inputs:
        raise RuntimeError(
            "No real candidates were successfully processed."
        )

    # ------------------------------------------------------------------
    # Step 2 - Build Day 15 fairness input
    # ------------------------------------------------------------------

    fairness_inputs: List[
        Dict[str, Any]
    ] = []

    for candidate in candidate_inputs:

        signals = {
            "skill_match": candidate.get(
                "skill_match"
            ),
            "experience_relevance": candidate.get(
                "experience_relevance"
            ),
            "education_alignment": candidate.get(
                "education_alignment"
            ),
            "semantic_similarity": candidate.get(
                "semantic_similarity"
            ),
        }

        fairness_inputs.append(
            {
                "candidate_id": candidate.get(
                    "candidate_id",
                    "candidate",
                ),
                "candidate_name": candidate.get(
                    "candidate_name",
                    "Unknown",
                ),
                "role": candidate.get(
                    "role",
                    "unknown",
                ),
                "final_score": candidate.get(
                    "final_score"
                ),
                "signals": signals,
                "candidate_skills": candidate.get(
                    "candidate_skills",
                    [],
                ),
                "required_skills": candidate.get(
                    "required_skills",
                    [],
                ),
                "resume_path": candidate.get(
                    "resume_path",
                    "",
                ),
                "job_description_path": candidate.get(
                    "job_description_path",
                    "",
                ),
            }
        )

    # ------------------------------------------------------------------
    # Step 3 - Apply Day 15 fairness scoring
    # ------------------------------------------------------------------

    compared = (
        fairness_pipeline.compare_scores(
            fairness_inputs
        )
    )

    # ------------------------------------------------------------------
    # Step 4 - Normalize fairness-adjusted scores
    # ------------------------------------------------------------------

    normalized = (
        fairness_pipeline.normalize_fairness_scores(
            compared
        )
    )

    # ------------------------------------------------------------------
    # Step 5 - Day 14 ranking
    # ------------------------------------------------------------------

    thresholds = RankingThresholds(
        shortlist=0.70,
        review=0.50,
    )

    ranking_engine = CandidateRankingEngine(
        thresholds=thresholds
    )

    ranked_result = (
        ranking_engine.process_candidates(
            candidates=normalized,
            score_key="fairness_adjusted_score",
            top_n=5,
        )
    )

    # ------------------------------------------------------------------
    # Step 6 - Build final output
    # ------------------------------------------------------------------

    final_candidates = []

    for candidate in ranked_result[
        "ranked_candidates"
    ]:

        final_candidates.append(
            {
                "rank": candidate.get(
                    "rank"
                ),
                "candidate_id": candidate.get(
                    "candidate_id"
                ),
                "candidate_name": candidate.get(
                    "candidate_name"
                ),
                "role": candidate.get(
                    "role"
                ),

                "original_ats_score": candidate.get(
                    "original_final_score"
                ),

                "original_ats_percentage": round(
                    candidate.get(
                        "original_final_score",
                        0.0,
                    ) * 100,
                    2,
                ),

                "fairness_adjusted_score": candidate.get(
                    "fairness_adjusted_score"
                ),

                "fairness_adjusted_percentage": candidate.get(
                    "fairness_adjusted_percentage"
                ),

                "fairness_normalized_score": candidate.get(
                    "fairness_normalized_score"
                ),

                "fairness_normalized_percentage": round(
                    candidate.get(
                        "fairness_normalized_score",
                        0.0,
                    ) * 100,
                    2,
                ),

                "original_skill_match": candidate.get(
                    "original_skill_match"
                ),

                "exact_skill_match": candidate.get(
                    "exact_skill_match"
                ),

                "semantic_skill_match": candidate.get(
                    "semantic_skill_match"
                ),

                "hybrid_skill_match": candidate.get(
                    "hybrid_skill_match"
                ),

                "status": candidate.get(
                    "status"
                ),

                "resume_path": candidate.get(
                    "resume_path"
                ),
            }
        )

    output = {
        "job_description": str(
            jd_path
        ),

        "thresholds": {
            "shortlist": thresholds.shortlist,
            "review": thresholds.review,
        },

        "candidate_count": len(
            final_candidates
        ),

        "ranked_candidates": (
            final_candidates
        ),

        "shortlisted_candidates": [
            {
                "rank": candidate.get(
                    "rank"
                ),
                "candidate_name": candidate.get(
                    "candidate_name"
                ),
                "fairness_adjusted_percentage":
                    candidate.get(
                        "fairness_adjusted_percentage"
                    ),
                "status": candidate.get(
                    "status"
                ),
            }
            for candidate in ranked_result[
                "shortlisted_candidates"
            ]
        ],

        "review_candidates": [
            {
                "rank": candidate.get(
                    "rank"
                ),
                "candidate_name": candidate.get(
                    "candidate_name"
                ),
                "fairness_adjusted_percentage":
                    candidate.get(
                        "fairness_adjusted_percentage"
                    ),
                "status": candidate.get(
                    "status"
                ),
            }
            for candidate in ranked_result[
                "review_candidates"
            ]
        ],

        "rejected_candidates": [
            {
                "rank": candidate.get(
                    "rank"
                ),
                "candidate_name": candidate.get(
                    "candidate_name"
                ),
                "fairness_adjusted_percentage":
                    candidate.get(
                        "fairness_adjusted_percentage"
                    ),
                "status": candidate.get(
                    "status"
                ),
            }
            for candidate in ranked_result[
                "rejected_candidates"
            ]
        ],

        "privacy_audit": privacy_audits,

        "summary": {
            "total_candidates": (
                len(final_candidates)
            ),
            "shortlisted": len(
                ranked_result[
                    "shortlisted_candidates"
                ]
            ),
            "review": len(
                ranked_result[
                    "review_candidates"
                ]
            ),
            "rejected": len(
                ranked_result[
                    "rejected_candidates"
                ]
            ),
        },
    }

    # ------------------------------------------------------------------
    # Step 7 - Save JSON
    # ------------------------------------------------------------------

    output_path = Path(
        "outputs/day15_real_fairness_results.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False,
            default=str,
        )

    # ------------------------------------------------------------------
    # Step 8 - Print results
    # ------------------------------------------------------------------

    print("\n" + "=" * 90)
    print(
        "DAY 15 - REAL FAIRNESS RESULTS"
    )
    print("=" * 90)

    print(
        f"{'Rank':<8}"
        f"{'Candidate':<25}"
        f"{'Original':<13}"
        f"{'Fair':<13}"
        f"{'Normalized':<13}"
        f"{'Status':<12}"
    )

    print("-" * 90)

    for candidate in final_candidates:

        print(
            f"{candidate['rank']:<8}"
            f"{candidate['candidate_name']:<25}"
            f"{candidate['original_ats_percentage']:>7.2f}%   "
            f"{candidate['fairness_adjusted_percentage']:>7.2f}%   "
            f"{candidate['fairness_normalized_percentage']:>7.2f}%   "
            f"{candidate['status']:<12}"
        )

    print("\n" + "=" * 80)
    print("PRIVACY / PERSONAL ATTRIBUTE AUDIT")
    print("=" * 80)

    for audit in privacy_audits:

        print(
            f"\nResume: "
            f"{audit['resume_path']}"
        )

        print(
            f"Detected attributes: "
            f"{audit['detected_personal_attributes']}"
        )

    print("\n" + "=" * 80)
    print("RECRUITER SUMMARY")
    print("=" * 80)

    print(
        f"Total candidates : "
        f"{output['summary']['total_candidates']}"
    )

    print(
        f"Shortlisted      : "
        f"{output['summary']['shortlisted']}"
    )

    print(
        f"Review required  : "
        f"{output['summary']['review']}"
    )

    print(
        f"Auto-rejected    : "
        f"{output['summary']['rejected']}"
    )

    print(
        f"\nJSON output: "
        f"{output_path}"
    )

    print("\n" + "=" * 90)
    print(
        "DAY 15 REAL DATA FAIRNESS "
        "EVALUATION COMPLETE"
    )
    print("=" * 90)


def day13_text_normalization(
    resume_text: str,
) -> str:
    """
    Perform lightweight normalization before the privacy audit.
    """

    if not resume_text:
        return ""

    return " ".join(
        str(resume_text)
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split()
    )


def main() -> None:

    if len(sys.argv) < 3:

        print(
            "\nUsage:"
        )

        print(
            "python -m fairness.day15_real_data_runner "
            "<jd_path> <resume1> <resume2> ..."
        )

        sys.exit(1)

    jd_path = Path(
        sys.argv[1]
    )

    resume_paths = [
        Path(path)
        for path in sys.argv[2:]
    ]

    if not jd_path.exists():

        print(
            f"ERROR: Job description not found: "
            f"{jd_path}"
        )

        sys.exit(1)

    missing = [
        path
        for path in resume_paths
        if not path.exists()
    ]

    if missing:

        print(
            "ERROR: Missing resume files:"
        )

        for path in missing:
            print(
                f"  - {path}"
            )

        sys.exit(1)

    process_real_candidates(
        jd_path,
        resume_paths,
    )


if __name__ == "__main__":
    main()