"""
Day 15 - Resume Normalization Validation
"""

from fairness.resume_normalizer import (
    ResumeNormalizer,
    normalize_resume_text,
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
        "DAY 15 - RESUME NORMALIZATION VALIDATION"
    )
    print("=" * 70)

    # --------------------------------------------------------------
    # Sample parsed resume
    # --------------------------------------------------------------

    resume = {
        "name": "Test Candidate",

        "summary":
            "Python developer with backend experience.",

        "skills": [
            "Python",
            "Python",
            "Django",
            "SQL",
            "Git",
        ],

        "experience": [
            {
                "title": "Python Developer",
                "organization": "Example Technologies",
                "start_date": "2022",
                "end_date": "2024",
                "description":
                    "Developed Python applications.",
            }
        ],

        "education": [
            {
                "qualification": "B.Tech",
                "field": "Computer Science",
                "institution": "Example University",
                "end_date": "2022",
            }
        ],

        "certifications": [
            "Python Certification",
            "Python Certification",
        ],

        "projects": [
            {
                "title": "ATS Project",
                "description":
                    "Built a resume analysis system.",
                "technologies": [
                    "Python",
                    "FastAPI",
                ],
            }
        ],
    }

    normalizer = ResumeNormalizer()

    normalized = normalizer.normalize(
        resume
    )

    result = normalized.to_dict()

    # --------------------------------------------------------------
    # Test 1
    # --------------------------------------------------------------

    assert_equal(
        result["name"],
        "Test Candidate",
        "Candidate name preserved",
    )

    # --------------------------------------------------------------
    # Test 2
    # --------------------------------------------------------------

    assert_equal(
        result["summary"],
        "Python developer with backend experience.",
        "Summary normalized",
    )

    # --------------------------------------------------------------
    # Test 3
    # --------------------------------------------------------------

    assert_equal(
        result["skills"],
        [
            "Python",
            "Django",
            "SQL",
            "Git",
        ],
        "Duplicate skills removed",
    )

    # --------------------------------------------------------------
    # Test 4
    # --------------------------------------------------------------

    assert_equal(
        result["experience"][0]["job_title"],
        "Python Developer",
        "Experience title standardized",
    )

    # --------------------------------------------------------------
    # Test 5
    # --------------------------------------------------------------

    assert_equal(
        result["experience"][0]["company"],
        "Example Technologies",
        "Experience organization standardized",
    )

    # --------------------------------------------------------------
    # Test 6
    # --------------------------------------------------------------

    assert_equal(
        result["education"][0]["degree"],
        "B.Tech",
        "Education degree standardized",
    )

    # --------------------------------------------------------------
    # Test 7
    # --------------------------------------------------------------

    assert_equal(
        result["education"][0]["field_of_study"],
        "Computer Science",
        "Education field standardized",
    )

    # --------------------------------------------------------------
    # Test 8
    # --------------------------------------------------------------

    assert_equal(
        result["certifications"],
        [
            "Python Certification"
        ],
        "Duplicate certifications removed",
    )

    # --------------------------------------------------------------
    # Test 9
    # --------------------------------------------------------------

    assert_equal(
        result["projects"][0]["name"],
        "ATS Project",
        "Project title standardized",
    )

    # --------------------------------------------------------------
    # Test 10
    # --------------------------------------------------------------

    raw_text = (
        "Python Developer   \n\n"
        "   Python   Django    SQL\n\n\n"
        "Experience"
    )

    normalized_text = normalize_resume_text(
        raw_text
    )

    assert_equal(
        normalized_text,
        (
            "Python Developer\n"
            "Python Django SQL\n"
            "Experience"
        ),
        "Raw resume text normalized",
    )

    # --------------------------------------------------------------
    # Test 11
    # --------------------------------------------------------------

    empty_result = normalizer.normalize(
        None
    ).to_dict()

    assert_equal(
        empty_result["skills"],
        [],
        "Missing skills handled safely",
    )

    # --------------------------------------------------------------
    # Test 12
    # --------------------------------------------------------------

    assert_equal(
        empty_result["experience"],
        [],
        "Missing experience handled safely",
    )

    # --------------------------------------------------------------
    # Test 13
    # --------------------------------------------------------------

    assert_true(
        result["education"][0][
            "institution"
        ] == "Example University",
        "Education institution preserved",
    )

    # --------------------------------------------------------------
    # Test 14
    # --------------------------------------------------------------

    assert_raises(
        TypeError,
        lambda: normalizer.normalize(
            "invalid resume"
        ),
        "Invalid resume input rejected",
    )

    print("\n" + "=" * 70)
    print(
        "NORMALIZED RESUME OUTPUT"
    )
    print("=" * 70)

    for field, value in result.items():
        print(
            f"{field:<18}: {value}"
        )

    print("\n" + "=" * 70)
    print(
        "DAY 15 RESUME NORMALIZATION "
        "VALIDATION COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()