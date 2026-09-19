"""
Day 14 Validation

Validates:
    - Candidate sorting
    - Rank assignment
    - Shortlist threshold
    - Review zone
    - Reject zone
    - Top-N generation
    - Recruiter-friendly summary
    - Invalid input handling
"""

from scoring.resume_ranking_engine import (
    CandidateRankingEngine,
    RankingThresholds,
)


def assert_equal(actual, expected, test_name: str) -> None:
    if actual != expected:
        raise AssertionError(
            f"{test_name} FAILED: "
            f"expected {expected!r}, got {actual!r}"
        )

    print(f"[PASS] {test_name}")


def assert_raises(exception_type, function, test_name: str) -> None:
    try:
        function()
    except exception_type:
        print(f"[PASS] {test_name}")
        return

    raise AssertionError(
        f"{test_name} FAILED: expected "
        f"{exception_type.__name__}"
    )


def main() -> None:
    print("=" * 70)
    print("DAY 14 - CANDIDATE RANKING & SHORTLISTING VALIDATION")
    print("=" * 70)

    engine = CandidateRankingEngine()

    candidates = [
        {
            "candidate_id": "CAND-003",
            "candidate_name": "Arjun",
            "role": "Python Developer",
            "final_score": 0.61,
        },
        {
            "candidate_id": "CAND-001",
            "candidate_name": "Asha",
            "role": "Python Developer",
            "final_score": 0.84,
        },
        {
            "candidate_id": "CAND-004",
            "candidate_name": "Rahul",
            "role": "Python Developer",
            "final_score": 0.43,
        },
        {
            "candidate_id": "CAND-002",
            "candidate_name": "Meera",
            "role": "Python Developer",
            "final_score": 0.72,
        },
        {
            "candidate_id": "CAND-005",
            "candidate_name": "Nikhil",
            "role": "Python Developer",
            "final_score": 0.51,
        },
    ]

    # --------------------------------------------------------------
    # Test 1 - Ranking
    # --------------------------------------------------------------

    ranked = engine.rank_candidates(candidates)

    ranked_ids = [
        candidate["candidate_id"]
        for candidate in ranked
    ]

    assert_equal(
        ranked_ids,
        [
            "CAND-001",
            "CAND-002",
            "CAND-003",
            "CAND-005",
            "CAND-004",
        ],
        "Candidates sorted by descending ATS score",
    )

    # --------------------------------------------------------------
    # Test 2 - Rank numbering
    # --------------------------------------------------------------

    ranks = [
        candidate["rank"]
        for candidate in ranked
    ]

    assert_equal(
        ranks,
        [1, 2, 3, 4, 5],
        "Rank numbers assigned correctly",
    )

    # --------------------------------------------------------------
    # Test 3 - Shortlist classification
    # --------------------------------------------------------------

    statuses = [
        candidate["status"]
        for candidate in ranked
    ]

    assert_equal(
        statuses,
        [
            "SHORTLIST",
            "SHORTLIST",
            "REVIEW",
            "REVIEW",
            "REJECT",
        ],
        "Shortlist/review/reject zones assigned correctly",
    )

    # --------------------------------------------------------------
    # Test 4 - Score percentage
    # --------------------------------------------------------------

    assert_equal(
        ranked[0]["score_percentage"],
        84.0,
        "Score percentage generated correctly",
    )

    # --------------------------------------------------------------
    # Test 5 - Shortlisted candidates
    # --------------------------------------------------------------

    shortlisted = engine.shortlist_candidates(ranked)

    assert_equal(
        len(shortlisted),
        2,
        "Shortlisted candidate count",
    )

    # --------------------------------------------------------------
    # Test 6 - Review candidates
    # --------------------------------------------------------------

    review = engine.review_candidates(ranked)

    assert_equal(
        len(review),
        2,
        "Review candidate count",
    )

    # --------------------------------------------------------------
    # Test 7 - Rejected candidates
    # --------------------------------------------------------------

    rejected = engine.rejected_candidates(ranked)

    assert_equal(
        len(rejected),
        1,
        "Rejected candidate count",
    )

    # --------------------------------------------------------------
    # Test 8 - Top N
    # --------------------------------------------------------------

    top_three = engine.top_candidates(
        ranked_candidates=ranked,
        top_n=3,
    )

    assert_equal(
        [
            candidate["candidate_id"]
            for candidate in top_three
        ],
        [
            "CAND-001",
            "CAND-002",
            "CAND-003",
        ],
        "Top-N candidate generation",
    )

    # --------------------------------------------------------------
    # Test 9 - Recruiter summary
    # --------------------------------------------------------------

    summary = engine.recruiter_summary(ranked)

    assert_equal(
        summary["total_candidates"],
        5,
        "Recruiter summary total candidate count",
    )

    assert_equal(
        summary["shortlisted_count"],
        2,
        "Recruiter summary shortlist count",
    )

    assert_equal(
        summary["review_count"],
        2,
        "Recruiter summary review count",
    )

    assert_equal(
        summary["rejected_count"],
        1,
        "Recruiter summary reject count",
    )

    assert_equal(
        summary["top_candidate"]["candidate_id"],
        "CAND-001",
        "Recruiter summary top candidate",
    )

    # --------------------------------------------------------------
    # Test 10 - Custom thresholds
    # --------------------------------------------------------------

    custom_thresholds = RankingThresholds(
        shortlist=0.80,
        review=0.60,
    )

    custom_engine = CandidateRankingEngine(
        thresholds=custom_thresholds
    )

    custom_ranked = custom_engine.rank_candidates(candidates)

    custom_statuses = [
        candidate["status"]
        for candidate in custom_ranked
    ]

    assert_equal(
        custom_statuses,
        [
            "SHORTLIST",
            "REVIEW",
            "REVIEW",
            "REJECT",
            "REJECT",
        ],
        "Configurable thresholds",
    )

    # --------------------------------------------------------------
    # Test 11 - Invalid score
    # --------------------------------------------------------------

    assert_raises(
        ValueError,
        lambda: engine.rank_candidates(
            [
                {
                    "candidate_id": "INVALID",
                    "candidate_name": "Invalid Candidate",
                    "final_score": 1.5,
                }
            ]
        ),
        "Reject score outside 0-1 range",
    )

    # --------------------------------------------------------------
    # Test 12 - Missing score
    # --------------------------------------------------------------

    assert_raises(
        KeyError,
        lambda: engine.rank_candidates(
            [
                {
                    "candidate_id": "MISSING",
                    "candidate_name": "Missing Score",
                }
            ]
        ),
        "Reject candidate without ATS score",
    )

    # --------------------------------------------------------------
    # Test 13 - Invalid threshold configuration
    # --------------------------------------------------------------

    assert_raises(
        ValueError,
        lambda: RankingThresholds(
            shortlist=0.40,
            review=0.60,
        ),
        "Reject invalid threshold ordering",
    )

    # --------------------------------------------------------------
    # Recruiter output
    # --------------------------------------------------------------

    print("\n" + "=" * 70)
    print("RANKED CANDIDATES")
    print("=" * 70)

    for candidate in ranked:
        print(
            f"Rank #{candidate['rank']} | "
            f"{candidate['candidate_name']} | "
            f"{candidate['score_percentage']:.2f}% | "
            f"{candidate['status']}"
        )

    print("\n" + "=" * 70)
    print("RECRUITER SUMMARY")
    print("=" * 70)

    print(
        f"Total candidates : "
        f"{summary['total_candidates']}"
    )

    print(
        f"Shortlisted      : "
        f"{summary['shortlisted_count']}"
    )

    print(
        f"Review           : "
        f"{summary['review_count']}"
    )

    print(
        f"Rejected         : "
        f"{summary['rejected_count']}"
    )

    print(
        f"Top candidate    : "
        f"{summary['top_candidate']['candidate_name']} "
        f"({summary['top_candidate']['score_percentage']:.2f}%)"
    )

    print("\n" + "=" * 70)
    print("DAY 14 ATS RANKING VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()