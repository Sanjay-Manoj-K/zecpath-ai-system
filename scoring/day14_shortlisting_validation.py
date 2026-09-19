"""
Day 14 - Shortlisting Automation Validation
"""

from scoring.shortlisting_automation import (
    ShortlistingAutomation,
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
    print("DAY 14 - SHORTLISTING AUTOMATION VALIDATION")
    print("=" * 70)

    candidates = [
        {
            "candidate_id": "CAND-001",
            "candidate_name": "Asha",
            "final_score": 0.91,
        },
        {
            "candidate_id": "CAND-002",
            "candidate_name": "Meera",
            "final_score": 0.83,
        },
        {
            "candidate_id": "CAND-003",
            "candidate_name": "Arjun",
            "final_score": 0.68,
        },
        {
            "candidate_id": "CAND-004",
            "candidate_name": "Nikhil",
            "final_score": 0.55,
        },
        {
            "candidate_id": "CAND-005",
            "candidate_name": "Rahul",
            "final_score": 0.49,
        },
        {
            "candidate_id": "CAND-006",
            "candidate_name": "Vivek",
            "final_score": 0.31,
        },
    ]

    automation = ShortlistingAutomation()

    # --------------------------------------------------------------
    # Test 1 - Candidate classification
    # --------------------------------------------------------------

    shortlist_candidate = automation.classify_candidate(
        candidates[0]
    )

    assert_equal(
        shortlist_candidate["status"],
        "SHORTLIST",
        "High-score candidate classified as SHORTLIST",
    )

    # --------------------------------------------------------------
    # Test 2 - Review classification
    # --------------------------------------------------------------

    review_candidate = automation.classify_candidate(
        candidates[2]
    )

    assert_equal(
        review_candidate["status"],
        "REVIEW",
        "Medium-score candidate classified as REVIEW",
    )

    # --------------------------------------------------------------
    # Test 3 - Reject classification
    # --------------------------------------------------------------

    reject_candidate = automation.classify_candidate(
        candidates[4]
    )

    assert_equal(
        reject_candidate["status"],
        "REJECT",
        "Low-score candidate classified as REJECT",
    )

    # --------------------------------------------------------------
    # Test 4 - Full processing
    # --------------------------------------------------------------

    result = automation.process(candidates)

    assert_equal(
        len(result["shortlisted"]),
        2,
        "Shortlist count",
    )

    assert_equal(
        len(result["review"]),
        2,
        "Review queue count",
    )

    assert_equal(
        len(result["rejected"]),
        2,
        "Rejection queue count",
    )

    # --------------------------------------------------------------
    # Test 5 - Shortlist ordering
    # --------------------------------------------------------------

    shortlist = automation.generate_shortlist(candidates)

    assert_equal(
        [
            candidate["candidate_name"]
            for candidate in shortlist
        ],
        [
            "Asha",
            "Meera",
        ],
        "Shortlist sorted by ATS score",
    )

    # --------------------------------------------------------------
    # Test 6 - Maximum shortlist size
    # --------------------------------------------------------------

    limited_shortlist = automation.generate_shortlist(
        candidates,
        maximum_candidates=1,
    )

    assert_equal(
        len(limited_shortlist),
        1,
        "Maximum shortlist size applied",
    )

    assert_equal(
        limited_shortlist[0]["candidate_name"],
        "Asha",
        "Highest-scoring candidate retained in limited shortlist",
    )

    # --------------------------------------------------------------
    # Test 7 - Review queue ordering
    # --------------------------------------------------------------

    review_queue = automation.generate_review_queue(
        candidates
    )

    assert_equal(
        [
            candidate["candidate_name"]
            for candidate in review_queue
        ],
        [
            "Arjun",
            "Nikhil",
        ],
        "Review queue sorted by ATS score",
    )

    # --------------------------------------------------------------
    # Test 8 - Rejection queue
    # --------------------------------------------------------------

    rejection_queue = automation.generate_rejection_queue(
        candidates
    )

    assert_equal(
        [
            candidate["candidate_name"]
            for candidate in rejection_queue
        ],
        [
            "Rahul",
            "Vivek",
        ],
        "Rejection queue generated correctly",
    )

    # --------------------------------------------------------------
    # Test 9 - Recruiter summary
    # --------------------------------------------------------------

    summary = automation.generate_decision_summary(
        candidates
    )

    assert_equal(
        summary["total_candidates"],
        6,
        "Recruiter summary total candidates",
    )

    assert_equal(
        summary["shortlisted"],
        2,
        "Recruiter summary shortlist count",
    )

    assert_equal(
        summary["review_required"],
        2,
        "Recruiter summary review count",
    )

    assert_equal(
        summary["auto_rejected"],
        2,
        "Recruiter summary reject count",
    )

    # --------------------------------------------------------------
    # Test 10 - Full automation
    # --------------------------------------------------------------

    automated = automation.automate(
        candidates,
        maximum_shortlist=2,
    )

    assert_equal(
        len(automated["shortlist"]),
        2,
        "Full automation shortlist",
    )

    assert_equal(
        len(automated["review_queue"]),
        2,
        "Full automation review queue",
    )

    assert_equal(
        len(automated["rejection_queue"]),
        2,
        "Full automation rejection queue",
    )

    # --------------------------------------------------------------
    # Test 11 - Invalid maximum shortlist
    # --------------------------------------------------------------

    assert_raises(
        ValueError,
        lambda: automation.generate_shortlist(
            candidates,
            maximum_candidates=0,
        ),
        "Reject invalid maximum shortlist size",
    )

    # --------------------------------------------------------------
    # Test 12 - Invalid candidate score
    # --------------------------------------------------------------

    assert_raises(
        ValueError,
        lambda: automation.classify_candidate(
            {
                "candidate_id": "INVALID",
                "candidate_name": "Invalid",
                "final_score": 1.5,
            }
        ),
        "Reject invalid ATS score",
    )

    # --------------------------------------------------------------
    # Display output
    # --------------------------------------------------------------

    print("\n" + "=" * 70)
    print("SHORTLIST")
    print("=" * 70)

    for candidate in automated["shortlist"]:
        print(
            f"{candidate['candidate_name']} - "
            f"{candidate['score_percentage']:.2f}% - "
            f"{candidate['status']}"
        )

    print("\n" + "=" * 70)
    print("REVIEW QUEUE")
    print("=" * 70)

    for candidate in automated["review_queue"]:
        print(
            f"{candidate['candidate_name']} - "
            f"{candidate['score_percentage']:.2f}% - "
            f"{candidate['status']}"
        )

    print("\n" + "=" * 70)
    print("AUTO-REJECTION QUEUE")
    print("=" * 70)

    for candidate in automated["rejection_queue"]:
        print(
            f"{candidate['candidate_name']} - "
            f"{candidate['score_percentage']:.2f}% - "
            f"{candidate['status']}"
        )

    print("\n" + "=" * 70)
    print("RECRUITER SUMMARY")
    print("=" * 70)

    print(
        f"Total candidates : "
        f"{automated['summary']['total_candidates']}"
    )

    print(
        f"Shortlisted      : "
        f"{automated['summary']['shortlisted']}"
    )

    print(
        f"Review required  : "
        f"{automated['summary']['review_required']}"
    )

    print(
        f"Auto-rejected    : "
        f"{automated['summary']['auto_rejected']}"
    )

    print("\n" + "=" * 70)
    print("DAY 14 SHORTLISTING AUTOMATION VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()