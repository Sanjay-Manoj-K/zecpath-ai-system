"""
Day 15 - Keyword Dependence Reduction Validation
"""

from fairness.keyword_dependence_reducer import (
    KeywordDependenceReducer,
)


def assert_equal(
    actual,
    expected,
    test_name: str,
) -> None:

    if actual != expected:
        raise AssertionError(
            f"{test_name} FAILED: "
            f"expected {expected!r}, "
            f"got {actual!r}"
        )

    print(f"[PASS] {test_name}")


def assert_true(
    condition: bool,
    test_name: str,
) -> None:

    if not condition:
        raise AssertionError(
            f"{test_name} FAILED"
        )

    print(f"[PASS] {test_name}")


def assert_raises(
    exception_type,
    function,
    test_name: str,
) -> None:

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
    print(
        "DAY 15 - KEYWORD DEPENDENCE REDUCTION VALIDATION"
    )
    print("=" * 70)

    matcher = KeywordDependenceReducer(
        exact_weight=0.40,
        semantic_weight=0.60,
        similarity_threshold=0.65,
    )

    # --------------------------------------------------------------
    # Test data
    # --------------------------------------------------------------

    candidate_skills = [
        "Python",
        "Django",
        "RESTful Web Services",
        "PostgreSQL",
        "Git",
    ]

    required_skills = [
        "Python",
        "Django",
        "REST API",
        "SQL",
        "Version Control",
    ]

    # --------------------------------------------------------------
    # Test 1 - Exact matching
    # --------------------------------------------------------------

    exact_score, exact_matches = (
        matcher.calculate_exact_match(
            candidate_skills,
            required_skills,
        )
    )

    assert_equal(
        exact_score,
        0.4,
        "Exact skill matching calculated",
    )

    # --------------------------------------------------------------
    # Test 2 - Exact matches preserved
    # --------------------------------------------------------------

    assert_true(
        "Python" in exact_matches,
        "Exact Python match detected",
    )

    assert_true(
        "Django" in exact_matches,
        "Exact Django match detected",
    )

    # --------------------------------------------------------------
    # Test 3 - Semantic matching
    # --------------------------------------------------------------

    semantic_score, semantic_matches = (
        matcher.calculate_semantic_match(
            candidate_skills,
            required_skills,
        )
    )

    assert_true(
        0.0 <= semantic_score <= 1.0,
        "Semantic score remains within 0-1 range",
    )

    # --------------------------------------------------------------
    # Test 4 - Semantic comparison generated
    # --------------------------------------------------------------

    assert_equal(
        len(semantic_matches),
        len(required_skills),
        "Semantic comparison generated for every JD skill",
    )

    # --------------------------------------------------------------
    # Test 5 - Hybrid matching
    # --------------------------------------------------------------

    result = matcher.calculate_hybrid_match(
        candidate_skills,
        required_skills,
    )

    assert_true(
        0.0 <= result.hybrid_match_score <= 1.0,
        "Hybrid skill score remains within 0-1 range",
    )

    # --------------------------------------------------------------
    # Test 6 - Hybrid score differs from pure exact score
    # --------------------------------------------------------------

    assert_true(
        result.hybrid_match_score != result.exact_match_score,
        "Hybrid scoring incorporates semantic information",
    )

    # --------------------------------------------------------------
    # Test 7 - Result is serializable
    # --------------------------------------------------------------

    result_dict = result.to_dict()

    assert_true(
        "exact_match_score" in result_dict,
        "Exact score exposed in output",
    )

    assert_true(
        "semantic_match_score" in result_dict,
        "Semantic score exposed in output",
    )

    assert_true(
        "hybrid_match_score" in result_dict,
        "Hybrid score exposed in output",
    )

    # --------------------------------------------------------------
    # Test 8 - Empty candidate skills
    # --------------------------------------------------------------

    empty_result = matcher.calculate_hybrid_match(
        [],
        required_skills,
    )

    assert_equal(
        empty_result.exact_match_score,
        0.0,
        "Empty candidate skills handled",
    )

    # --------------------------------------------------------------
    # Test 9 - Empty requirements
    # --------------------------------------------------------------

    no_requirement_result = (
        matcher.calculate_hybrid_match(
            candidate_skills,
            [],
        )
    )

    assert_equal(
        no_requirement_result.exact_match_score,
        0.0,
        "Empty required skills handled",
    )

    # --------------------------------------------------------------
    # Test 10 - Invalid threshold
    # --------------------------------------------------------------

    assert_raises(
        ValueError,
        lambda: KeywordDependenceReducer(
            similarity_threshold=1.5
        ),
        "Invalid similarity threshold rejected",
    )

    # --------------------------------------------------------------
    # Test 11 - Invalid weights
    # --------------------------------------------------------------

    assert_raises(
        ValueError,
        lambda: KeywordDependenceReducer(
            exact_weight=0.0,
            semantic_weight=0.0,
        ),
        "Zero total weight rejected",
    )

    # --------------------------------------------------------------
    # Display results
    # --------------------------------------------------------------

    print("\n" + "=" * 70)
    print("KEYWORD DEPENDENCE REDUCTION RESULT")
    print("=" * 70)

    print(
        f"Exact Match Score     : "
        f"{result.exact_match_score:.4f}"
    )

    print(
        f"Semantic Match Score  : "
        f"{result.semantic_match_score:.4f}"
    )

    print(
        f"Hybrid Match Score    : "
        f"{result.hybrid_match_score:.4f}"
    )

    print(
        f"\nExact Matches:"
    )

    for skill in result.matched_skills:
        print(
            f"  - {skill}"
        )

    print(
        "\nSemantic Comparisons:"
    )

    for item in result.semantic_matches:

        print(
            f"  {item['required_skill']}"
            f" -> "
            f"{item['best_candidate_skill']}"
            f" | similarity="
            f"{item['similarity']}"
            f" | accepted="
            f"{item['accepted']}"
        )

    print("\n" + "=" * 70)
    print(
        "DAY 15 KEYWORD DEPENDENCE "
        "VALIDATION COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()