"""
Day 15 - Bias Indicator Evaluation Validation
"""

from fairness.bias_indicator_evaluator import (
    BiasIndicatorEvaluator,
)


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


def assert_raises(
    exception_type,
    function,
    test_name,
):
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
    print(
        "DAY 15 - BIAS INDICATOR VALIDATION"
    )
    print("=" * 70)

    evaluator = BiasIndicatorEvaluator()

    # --------------------------------------------------------------
    # Controlled audit data
    #
    # Audit groups are explicitly supplied test labels.
    # They are NOT inferred from candidate resumes.
    # --------------------------------------------------------------

    candidates = [
        {
            "candidate_id": "A1",
            "final_score": 0.90,
            "status": "SHORTLIST",
            "audit_group": "group_a",
            "missing_signals": [],
        },
        {
            "candidate_id": "A2",
            "final_score": 0.82,
            "status": "SHORTLIST",
            "audit_group": "group_a",
            "missing_signals": [],
        },
        {
            "candidate_id": "A3",
            "final_score": 0.68,
            "status": "REVIEW",
            "audit_group": "group_a",
            "missing_signals": [],
        },
        {
            "candidate_id": "A4",
            "final_score": 0.55,
            "status": "REVIEW",
            "audit_group": "group_a",
            "missing_signals": [
                "experience_relevance"
            ],
        },
        {
            "candidate_id": "B1",
            "final_score": 0.78,
            "status": "SHORTLIST",
            "audit_group": "group_b",
            "missing_signals": [],
        },
        {
            "candidate_id": "B2",
            "final_score": 0.70,
            "status": "SHORTLIST",
            "audit_group": "group_b",
            "missing_signals": [],
        },
        {
            "candidate_id": "B3",
            "final_score": 0.60,
            "status": "REVIEW",
            "audit_group": "group_b",
            "missing_signals": [],
        },
        {
            "candidate_id": "B4",
            "final_score": 0.35,
            "status": "REJECT",
            "audit_group": "group_b",
            "missing_signals": [
                "education_alignment"
            ],
        },
    ]

    # --------------------------------------------------------------
    # Test 1 - Group metrics
    # --------------------------------------------------------------

    group_a = (
        evaluator.calculate_group_metrics(
            candidates,
            "group_a",
        )
    )

    assert_equal(
        group_a.candidate_count,
        4,
        "Group candidate count",
    )

    # --------------------------------------------------------------
    # Test 2 - Mean score
    # --------------------------------------------------------------

    expected_mean_a = round(
        (0.90 + 0.82 + 0.68 + 0.55) / 4,
        4,
    )

    assert_equal(
        group_a.mean_score,
        expected_mean_a,
        "Group mean score calculated",
    )

    # --------------------------------------------------------------
    # Test 3 - Shortlist rate
    # --------------------------------------------------------------

    assert_equal(
        group_a.shortlist_rate,
        0.5,
        "Group shortlist rate calculated",
    )

    # --------------------------------------------------------------
    # Test 4 - Review rate
    # --------------------------------------------------------------

    assert_equal(
        group_a.review_rate,
        0.5,
        "Group review rate calculated",
    )

    # --------------------------------------------------------------
    # Test 5 - Missing-signal rate
    # --------------------------------------------------------------

    assert_equal(
        group_a.missing_signal_rate,
        0.25,
        "Missing-signal rate calculated",
    )

    # --------------------------------------------------------------
    # Test 6 - Full evaluation
    # --------------------------------------------------------------

    audit = evaluator.evaluate(
        candidates,
        reference_group="group_a",
    )

    assert_equal(
        len(audit["groups"]),
        2,
        "Both audit groups evaluated",
    )

    # --------------------------------------------------------------
    # Test 7 - Comparison generated
    # --------------------------------------------------------------

    assert_equal(
        len(audit["comparisons"]),
        1,
        "Group comparison generated",
    )

    comparison = audit[
        "comparisons"
    ][0]

    assert_equal(
        comparison["reference_group"],
        "group_a",
        "Reference group preserved",
    )

    assert_equal(
        comparison["comparison_group"],
        "group_b",
        "Comparison group preserved",
    )

    # --------------------------------------------------------------
    # Test 8 - Indicator generation
    # --------------------------------------------------------------

    report = evaluator.generate_report(
        candidates,
        reference_group="group_a",
        threshold=0.10,
    )

    assert_true(
        "indicators" in report,
        "Bias indicators included in report",
    )

    # --------------------------------------------------------------
    # Test 9 - Threshold stored
    # --------------------------------------------------------------

    assert_equal(
        report["indicator_threshold"],
        0.10,
        "Indicator threshold stored",
    )

    # --------------------------------------------------------------
    # Test 10 - Invalid reference group
    # --------------------------------------------------------------

    assert_raises(
        ValueError,
        lambda: evaluator.evaluate(
            candidates,
            reference_group="missing_group",
        ),
        "Invalid reference group rejected",
    )

    # --------------------------------------------------------------
    # Test 11 - Missing audit group
    # --------------------------------------------------------------

    assert_raises(
        KeyError,
        lambda: evaluator.evaluate(
            [
                {
                    "final_score": 0.7,
                    "status": "REVIEW",
                }
            ],
            reference_group="group_a",
        ),
        "Candidate without audit group rejected",
    )

    # --------------------------------------------------------------
    # Test 12 - Invalid score
    # --------------------------------------------------------------

    assert_raises(
        ValueError,
        lambda: evaluator.evaluate(
            [
                {
                    "final_score": 1.5,
                    "status": "REVIEW",
                    "audit_group": "group_a",
                }
            ],
            reference_group="group_a",
        ),
        "Invalid score rejected",
    )

    # --------------------------------------------------------------
    # Test 13 - Invalid status
    # --------------------------------------------------------------

    assert_raises(
        ValueError,
        lambda: evaluator.evaluate(
            [
                {
                    "final_score": 0.7,
                    "status": "INVALID",
                    "audit_group": "group_a",
                }
            ],
            reference_group="group_a",
        ),
        "Invalid status rejected",
    )

    # --------------------------------------------------------------
    # Test 14 - Invalid indicator threshold
    # --------------------------------------------------------------

    assert_raises(
        ValueError,
        lambda: evaluator.identify_indicators(
            audit,
            threshold=1.5,
        ),
        "Invalid indicator threshold rejected",
    )

    # --------------------------------------------------------------
    # Display result
    # --------------------------------------------------------------

    print("\n" + "=" * 70)
    print(
        "GROUP METRICS"
    )
    print("=" * 70)

    for group in report["groups"]:
        print(
            f"{group['group']:<12}"
            f"Candidates={group['candidate_count']:<4}"
            f"Mean Score={group['mean_score']:.4f} "
            f"Shortlist={group['shortlist_rate'] * 100:.2f}% "
            f"Review={group['review_rate'] * 100:.2f}% "
            f"Reject={group['reject_rate'] * 100:.2f}% "
            f"Missing={group['missing_signal_rate'] * 100:.2f}%"
        )

    print("\n" + "=" * 70)
    print(
        "BIAS INDICATORS"
    )
    print("=" * 70)

    if report["indicators"]:

        for indicator in report["indicators"]:
            print(
                f"{indicator['metric']:<25}"
                f"Gap={indicator['absolute_gap']:.4f}"
                f" | "
                f"{indicator['reference_group']}"
                f" vs "
                f"{indicator['comparison_group']}"
            )

    else:
        print(
            "No indicators exceeded the configured threshold."
        )

    print(
        f"\nIndicator Count: "
        f"{report['indicator_count']}"
    )

    print("\n" + "=" * 70)
    print(
        "DAY 15 BIAS INDICATOR "
        "VALIDATION COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()