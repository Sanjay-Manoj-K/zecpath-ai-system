from __future__ import annotations

from scoring.ats_scoring_engine import ATSScoringEngine


def print_result(title: str, result: dict) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    print(f"Role              : {result['role']}")
    print(f"Normalized Role    : {result['normalized_role']}")
    print(f"Final Score        : {result['final_percentage']}%")

    print("\nAvailable Signals:")
    for signal in result["available_signals"]:
        print(f"  - {signal}")

    print("\nMissing Signals:")
    if result["missing_signals"]:
        for signal in result["missing_signals"]:
            print(f"  - {signal}")
    else:
        print("  None")

    print("\nComponent Breakdown:")
    for name, component in result["components"].items():
        score = component["score"]

        if score is None:
            score_text = "Unavailable"
        else:
            score_text = f"{score:.4f}"

        print(
            f"  {name:24s} "
            f"score={score_text:>11s} "
            f"base={component['base_weight']:.4f} "
            f"effective={component['effective_weight']:.4f} "
            f"contribution={component['contribution']:.4f}"
        )


def test_full_data(engine: ATSScoringEngine) -> None:
    result = engine.generate_candidate_score(
        candidate_id="candidate_full",
        role="Python Developer",
        signals={
            "skill_match": 0.80,
            "experience_relevance": 0.70,
            "education_alignment": 1.00,
            "semantic_similarity": 0.66,
        },
    )

    expected = 0.751

    assert abs(result["final_score"] - expected) < 0.0001
    assert len(result["available_signals"]) == 4
    assert result["missing_signals"] == []

    print_result("TEST 1 - FULL DATA", result)
    print("PASS: Full weighted scoring is correct.")


def test_missing_education(engine: ATSScoringEngine) -> None:
    result = engine.generate_candidate_score(
        candidate_id="candidate_no_education",
        role="Python Developer",
        signals={
            "skill_match": 0.80,
            "experience_relevance": 0.70,
            "education_alignment": None,
            "semantic_similarity": 0.66,
        },
    )

    assert "education_alignment" in result["missing_signals"]
    assert result["components"]["education_alignment"]["available"] is False

    effective_total = sum(
        component["effective_weight"]
        for component in result["components"].values()
    )

    assert abs(effective_total - 1.0) < 0.0001

    print_result("TEST 2 - MISSING EDUCATION", result)
    print("PASS: Missing education is excluded and weights are redistributed.")


def test_missing_experience(engine: ATSScoringEngine) -> None:
    result = engine.generate_candidate_score(
        candidate_id="candidate_no_experience",
        role="Python Developer",
        signals={
            "skill_match": 0.80,
            "experience_relevance": None,
            "education_alignment": 1.00,
            "semantic_similarity": 0.66,
        },
    )

    assert "experience_relevance" in result["missing_signals"]
    assert result["components"]["experience_relevance"]["available"] is False

    effective_total = sum(
        component["effective_weight"]
        for component in result["components"].values()
    )

    assert abs(effective_total - 1.0) < 0.0001

    print_result("TEST 3 - MISSING EXPERIENCE", result)
    print("PASS: Missing experience is excluded and weights are redistributed.")


def test_missing_skill_signal(engine: ATSScoringEngine) -> None:
    result = engine.generate_candidate_score(
        candidate_id="candidate_no_skills",
        role="Python Developer",
        signals={
            "skill_match": None,
            "experience_relevance": 0.70,
            "education_alignment": 1.00,
            "semantic_similarity": 0.66,
        },
    )

    assert "skill_match" in result["missing_signals"]
    assert result["components"]["skill_match"]["available"] is False

    effective_total = sum(
        component["effective_weight"]
        for component in result["components"].values()
    )

    assert abs(effective_total - 1.0) < 0.0001

    print_result("TEST 4 - MISSING SKILL SIGNAL", result)
    print("PASS: Missing skill evidence is handled correctly.")


def test_ai_ml_role(engine: ATSScoringEngine) -> None:
    result = engine.generate_candidate_score(
        candidate_id="candidate_ai",
        role="AI/ML Engineer",
        signals={
            "skill_match": 0.80,
            "experience_relevance": 0.70,
            "education_alignment": 1.00,
            "semantic_similarity": 0.66,
        },
    )

    assert result["normalized_role"] == "ai_ml"

    assert (
        result["components"]["semantic_similarity"]["base_weight"]
        == 0.40
    )

    print_result("TEST 5 - AI/ML ROLE WEIGHTS", result)
    print("PASS: AI/ML role-specific weights are applied.")


def test_finance_role(engine: ATSScoringEngine) -> None:
    result = engine.generate_candidate_score(
        candidate_id="candidate_finance",
        role="Finance Analyst",
        signals={
            "skill_match": 0.80,
            "experience_relevance": 0.70,
            "education_alignment": 1.00,
            "semantic_similarity": 0.66,
        },
    )

    assert result["normalized_role"] == "finance"

    assert (
        result["components"]["skill_match"]["base_weight"]
        == 0.40
    )

    print_result("TEST 6 - FINANCE ROLE WEIGHTS", result)
    print("PASS: Finance role-specific weights are applied.")


def test_unknown_role(engine: ATSScoringEngine) -> None:
    result = engine.generate_candidate_score(
        candidate_id="candidate_unknown",
        role="Specialist Analyst",
        signals={
            "skill_match": 0.80,
            "experience_relevance": 0.70,
            "education_alignment": 1.00,
            "semantic_similarity": 0.66,
        },
    )

    assert result["normalized_role"] == "default"

    print_result("TEST 7 - UNKNOWN ROLE", result)
    print("PASS: Unknown roles correctly fall back to default weights.")


def test_invalid_score(engine: ATSScoringEngine) -> None:
    try:
        engine.generate_candidate_score(
            candidate_id="candidate_invalid",
            role="Python Developer",
            signals={
                "skill_match": 1.50,
                "experience_relevance": 0.70,
                "education_alignment": 1.00,
                "semantic_similarity": 0.66,
            },
        )

    except ValueError as exc:
        print("\n" + "=" * 70)
        print("TEST 8 - INVALID SCORE VALIDATION")
        print("=" * 70)
        print(f"Caught expected error: {exc}")
        print("PASS: Invalid score was rejected.")

    else:
        raise AssertionError(
            "Invalid score was not rejected."
        )


def test_all_signals_missing(engine: ATSScoringEngine) -> None:
    try:
        engine.generate_candidate_score(
            candidate_id="candidate_empty",
            role="Python Developer",
            signals={
                "skill_match": None,
                "experience_relevance": None,
                "education_alignment": None,
                "semantic_similarity": None,
            },
        )

    except ValueError as exc:
        print("\n" + "=" * 70)
        print("TEST 9 - ALL SIGNALS MISSING")
        print("=" * 70)
        print(f"Caught expected error: {exc}")
        print("PASS: Empty scoring input was rejected.")

    else:
        raise AssertionError(
            "All-missing scoring input was not rejected."
        )


def main() -> None:
    print("=" * 70)
    print("DAY 13 - ATS SCORING ENGINE VALIDATION")
    print("=" * 70)

    engine = ATSScoringEngine()

    tests = [
        test_full_data,
        test_missing_education,
        test_missing_experience,
        test_missing_skill_signal,
        test_ai_ml_role,
        test_finance_role,
        test_unknown_role,
        test_invalid_score,
        test_all_signals_missing,
    ]

    passed = 0

    for test in tests:
        test(engine)
        passed += 1

    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total tests : {len(tests)}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {len(tests) - passed}")

    if passed == len(tests):
        print("\nDAY 13 ATS VALIDATION COMPLETE")
        print("All tests passed successfully.")
    else:
        raise AssertionError("One or more validation tests failed.")


if __name__ == "__main__":
    main()