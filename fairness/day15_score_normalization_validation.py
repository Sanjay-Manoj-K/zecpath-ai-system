"""
Day 15 - Score Normalization Validation
"""

from fairness.score_normalizer import ScoreNormalizer


def assert_equal(actual, expected, test_name):
    if actual != expected:
        raise AssertionError(
            f"{test_name} FAILED: "
            f"expected {expected!r}, got {actual!r}"
        )

    print(f"[PASS] {test_name}")


def assert_true(condition, test_name):
    if not condition:
        raise AssertionError(
            f"{test_name} FAILED"
        )

    print(f"[PASS] {test_name}")


def assert_raises(exception_type, function, test_name):
    try:
        function()
    except exception_type:
        print(f"[PASS] {test_name}")
        return

    raise AssertionError(
        f"{test_name} FAILED: "
        f"expected {exception_type.__name__}"
    )


def main():
    print("=" * 70)
    print("DAY 15 - SCORE NORMALIZATION VALIDATION")
    print("=" * 70)

    normalizer = ScoreNormalizer()

    scores = [
        0.30,
        0.50,
        0.75,
        0.90,
    ]

    candidates = [
        {
            "candidate_id": "CAND-001",
            "candidate_name": "Candidate A",
            "final_score": 0.90,
        },
        {
            "candidate_id": "CAND-002",
            "candidate_name": "Candidate B",
            "final_score": 0.75,
        },
        {
            "candidate_id": "CAND-003",
            "candidate_name": "Candidate C",
            "final_score": 0.50,
        },
        {
            "candidate_id": "CAND-004",
            "candidate_name": "Candidate D",
            "final_score": 0.30,
        },
    ]

    normalized = normalizer.normalize_scores(scores)

    assert_equal(
        len(normalized),
        4,
        "All scores normalized",
    )

    assert_equal(
        normalized[0].normalized_score,
        0.0,
        "Minimum score normalized to 0",
    )

    assert_equal(
        normalized[-1].normalized_score,
        1.0,
        "Maximum score normalized to 1",
    )

    assert_equal(
        normalized[1].normalized_score,
        0.3333,
        "Intermediate score normalized correctly",
    )

    assert_true(
        all(
            0.0 <= item.normalized_score <= 1.0
            for item in normalized
        ),
        "All normalized scores remain within 0-1",
    )

    assert_equal(
        normalizer.normalize_scores([]),
        [],
        "Empty score collection handled",
    )

    equal_scores = normalizer.normalize_scores(
        [0.60, 0.60, 0.60]
    )

    assert_equal(
        [
            item.normalized_score
            for item in equal_scores
        ],
        [0.5, 0.5, 0.5],
        "Equal scores handled safely",
    )

    normalized_candidates = (
        normalizer.normalize_candidates(
            candidates
        )
    )

    assert_equal(
        len(normalized_candidates),
        4,
        "Candidate scores normalized",
    )

    assert_equal(
        normalized_candidates[0]["final_score"],
        0.90,
        "Original ATS score preserved",
    )

    assert_true(
        "normalized_score"
        in normalized_candidates[0],
        "Normalized score field added",
    )

    assert_true(
        "normalized_percentage"
        in normalized_candidates[0],
        "Normalized percentage field added",
    )

    original_order = [
        candidate["candidate_id"]
        for candidate in sorted(
            candidates,
            key=lambda candidate:
                candidate["final_score"],
            reverse=True,
        )
    ]

    normalized_order = [
        candidate["candidate_id"]
        for candidate in sorted(
            normalized_candidates,
            key=lambda candidate:
                candidate["normalized_score"],
            reverse=True,
        )
    ]

    assert_equal(
        normalized_order,
        original_order,
        "Score normalization preserves ranking",
    )

    assert_raises(
        ValueError,
        lambda: normalizer.normalize_scores(
            [0.50, 1.50]
        ),
        "Invalid score rejected",
    )

    assert_raises(
        KeyError,
        lambda: normalizer.normalize_candidates(
            [
                {
                    "candidate_id": "INVALID"
                }
            ]
        ),
        "Candidate without score rejected",
    )

    print("\n" + "=" * 70)
    print("NORMALIZED SCORE RESULTS")
    print("=" * 70)

    for candidate in normalized_candidates:
        print(
            f"{candidate['candidate_name']:<20}"
            f"Original="
            f"{candidate['final_score']:.4f}"
            f" ({candidate['final_score'] * 100:.2f}%)"
            f" | Normalized="
            f"{candidate['normalized_score']:.4f}"
            f" ({candidate['normalized_percentage']:.2f}%)"
        )

    print("\n" + "=" * 70)
    print(
        "DAY 15 SCORE NORMALIZATION "
        "VALIDATION COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()