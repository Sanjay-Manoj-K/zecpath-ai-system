"""
Day 15 - Integrated Fairness Pipeline Validation
"""

from fairness.day15_fairness_pipeline import (
    Day15FairnessPipeline,
)


def assert_equal(
    actual,
    expected,
    test_name,
):
    if actual != expected:
        raise AssertionError(
            f"{test_name} FAILED: "
            f"expected {expected!r}, "
            f"got {actual!r}"
        )

    print(
        f"[PASS] {test_name}"
    )


def assert_true(
    condition,
    test_name,
):
    if not condition:
        raise AssertionError(
            f"{test_name} FAILED"
        )

    print(
        f"[PASS] {test_name}"
    )


def assert_raises(
    exception_type,
    function,
    test_name,
):
    try:
        function()

    except exception_type:
        print(
            f"[PASS] {test_name}"
        )
        return

    raise AssertionError(
        f"{test_name} FAILED: expected "
        f"{exception_type.__name__}"
    )


def main():

    print("=" * 70)
    print(
        "DAY 15 - INTEGRATED FAIRNESS PIPELINE VALIDATION"
    )
    print("=" * 70)

    pipeline = (
        Day15FairnessPipeline()
    )

    # --------------------------------------------------------------
    # Test 1 - Resume preparation
    # --------------------------------------------------------------

    resume_text = """
    Name: Test Candidate
    Email: test@example.com
    Phone: +91 98765 43210
    Gender: Male

    Skills:
    Python, Django, RESTful Web Services

    Experience:
    Python Developer
    """

    prepared = pipeline.prepare_resume(
        resume_text
    )

    assert_true(
        bool(
            prepared["normalized_text"]
        ),
        "Resume normalization integrated",
    )

    # --------------------------------------------------------------
    # Test 2 - Personal attributes detected
    # --------------------------------------------------------------

    assert_true(
        "email"
        in prepared["detected_attributes"],
        "Personal attribute detection integrated",
    )

    # --------------------------------------------------------------
    # Test 3 - Personal data masked
    # --------------------------------------------------------------

    assert_true(
        "test@example.com"
        not in prepared["masked_text"],
        "Personal data masking integrated",
    )

    # --------------------------------------------------------------
    # Test 4 - Job-relevant content preserved
    # --------------------------------------------------------------

    assert_true(
        "Python"
        in prepared["masked_text"],
        "Job-relevant content preserved",
    )

    # --------------------------------------------------------------
    # Test 5 - Hybrid skill calculation
    # --------------------------------------------------------------

    skill_result = (
        pipeline.calculate_fair_skill_score(
            [
                "Python",
                "Django",
                "RESTful Web Services",
            ],
            [
                "Python",
                "Django",
                "REST API",
            ],
        )
    )

    assert_true(
        0.0
        <= skill_result["hybrid_match_score"]
        <= 1.0,
        "Hybrid skill score generated",
    )

    # --------------------------------------------------------------
    # Test 6 - Semantic contribution exists
    # --------------------------------------------------------------

    assert_true(
        skill_result[
            "semantic_match_score"
        ] > 0.0,
        "Semantic contribution included",
    )

    # --------------------------------------------------------------
    # Test 7 - Adjusted signal
    # --------------------------------------------------------------

    original_signals = {
        "skill_match": 0.3333,
        "experience_relevance": 0.60,
        "education_alignment": 1.0,
        "semantic_similarity": 0.55,
    }

    adjusted = (
        pipeline.calculate_adjusted_signals(
            original_signals,
            [
                "Python",
                "Django",
                "RESTful Web Services",
            ],
            [
                "Python",
                "Django",
                "REST API",
            ],
        )
    )

    assert_equal(
        adjusted["original_signals"],
        original_signals,
        "Original signals preserved",
    )

    assert_true(
        adjusted["adjusted_signals"][
            "skill_match"
        ]
        != original_signals[
            "skill_match"
        ],
        "Fairness-adjusted skill signal generated",
    )

    # --------------------------------------------------------------
    # Test 8 - Candidate score comparison
    # --------------------------------------------------------------

    candidates = [
        {
            "candidate_id": "CAND-001",
            "candidate_name": "Candidate A",
            "role": "Python Developer",
            "final_score": 0.55,
            "signals": {
                "skill_match": 0.3333,
                "experience_relevance": 0.60,
                "education_alignment": 1.0,
                "semantic_similarity": 0.55,
            },
            "candidate_skills": [
                "Python",
                "Django",
                "RESTful Web Services",
            ],
            "required_skills": [
                "Python",
                "Django",
                "REST API",
            ],
        },
        {
            "candidate_id": "CAND-002",
            "candidate_name": "Candidate B",
            "role": "Python Developer",
            "final_score": 0.45,
            "signals": {
                "skill_match": 0.20,
                "experience_relevance": 0.40,
                "education_alignment": 0.50,
                "semantic_similarity": 0.35,
            },
            "candidate_skills": [
                "Python",
                "Flask",
                "Git",
            ],
            "required_skills": [
                "Python",
                "Django",
                "REST API",
            ],
        },
    ]

    compared = pipeline.compare_scores(
        candidates
    )

    assert_equal(
        len(compared),
        2,
        "Candidates processed by fairness pipeline",
    )

    # --------------------------------------------------------------
    # Test 9 - Original score retained
    # --------------------------------------------------------------

    assert_equal(
        compared[0][
            "original_final_score"
        ],
        0.55,
        "Original ATS score retained",
    )

    # --------------------------------------------------------------
    # Test 10 - Fairness score generated
    # --------------------------------------------------------------

    assert_true(
        "fairness_adjusted_score"
        in compared[0],
        "Fairness-adjusted score generated",
    )

    # --------------------------------------------------------------
    # Test 11 - Exact skill score retained
    # --------------------------------------------------------------

    assert_true(
        "exact_skill_match"
        in compared[0],
        "Exact skill score retained",
    )

    # --------------------------------------------------------------
    # Test 12 - Semantic skill score retained
    # --------------------------------------------------------------

    assert_true(
        "semantic_skill_match"
        in compared[0],
        "Semantic skill score retained",
    )

    # --------------------------------------------------------------
    # Test 13 - Hybrid score retained
    # --------------------------------------------------------------

    assert_true(
        "hybrid_skill_match"
        in compared[0],
        "Hybrid skill score retained",
    )

    # --------------------------------------------------------------
    # Test 14 - Normalize fairness scores
    # --------------------------------------------------------------

    normalized = (
        pipeline.normalize_fairness_scores(
            compared
        )
    )

    assert_true(
        all(
            "fairness_normalized_score"
            in candidate
            for candidate in normalized
        ),
        "Fairness scores normalized",
    )

    # --------------------------------------------------------------
    # Test 15 - Normalized values valid
    # --------------------------------------------------------------

    assert_true(
        all(
            0.0
            <= candidate[
                "fairness_normalized_score"
            ]
            <= 1.0
            for candidate in normalized
        ),
        "Normalized fairness scores remain valid",
    )

    # --------------------------------------------------------------
    # Test 16 - Invalid candidate
    # --------------------------------------------------------------

    assert_raises(
        KeyError,
        lambda: pipeline.compare_scores(
            [
                {
                    "candidate_id": "INVALID",
                    "final_score": 0.5,
                }
            ]
        ),
        "Incomplete candidate rejected",
    )

    # --------------------------------------------------------------
    # Display results
    # --------------------------------------------------------------

    print("\n" + "=" * 70)
    print(
        "FAIRNESS PIPELINE RESULTS"
    )
    print("=" * 70)

    for candidate in normalized:

        print(
            f"{candidate['candidate_name']:<20}"
            f"Original="
            f"{candidate['original_final_score'] * 100:.2f}% "
            f"| Fair="
            f"{candidate['fairness_adjusted_score'] * 100:.2f}% "
            f"| Normalized="
            f"{candidate['fairness_normalized_score'] * 100:.2f}%"
        )

    print("\n" + "=" * 70)
    print(
        "DAY 15 INTEGRATED FAIRNESS "
        "PIPELINE VALIDATION COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()