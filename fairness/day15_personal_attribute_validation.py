"""
Day 15 - Personal Attribute Masking Validation
"""

from fairness.personal_attribute_masker import (
    MASK,
    PersonalAttributeMasker,
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
    print(
        "DAY 15 - PERSONAL ATTRIBUTE MASKING VALIDATION"
    )
    print("=" * 70)

    masker = PersonalAttributeMasker()

    resume_text = """
    Name: Test Candidate
    Email: test@example.com
    Phone: +91 98765 43210
    Date of Birth: 19-05-2003
    Age: 23 years
    Gender: Male
    Marital Status: Single
    Religion: Example
    Nationality: Indian
    Caste: Example Community
    Address: 10 Example Street, Kozhikode, Kerala
    Skills: Python, Django, SQL
    Experience: Python Developer
    """

    # --------------------------------------------------------------
    # Test 1 - Email
    # --------------------------------------------------------------

    masked_text = masker.mask_text(
        resume_text
    )

    assert_true(
        "test@example.com" not in masked_text,
        "Email address masked",
    )

    # --------------------------------------------------------------
    # Test 2 - Phone
    # --------------------------------------------------------------

    assert_true(
        "98765 43210" not in masked_text,
        "Phone number masked",
    )

    # --------------------------------------------------------------
    # Test 3 - Date of birth
    # --------------------------------------------------------------

    assert_true(
        "19-05-2003" not in masked_text,
        "Date of birth masked",
    )

    # --------------------------------------------------------------
    # Test 4 - Gender
    # --------------------------------------------------------------

    assert_true(
        "Gender: Male" not in masked_text,
        "Gender masked",
    )

    # --------------------------------------------------------------
    # Test 5 - Marital status
    # --------------------------------------------------------------

    assert_true(
        "Marital Status: Single" not in masked_text,
        "Marital status masked",
    )

    # --------------------------------------------------------------
    # Test 6 - Religion
    # --------------------------------------------------------------

    assert_true(
        "Religion: Example" not in masked_text,
        "Religion masked",
    )

    # --------------------------------------------------------------
    # Test 7 - Nationality
    # --------------------------------------------------------------

    assert_true(
        "Nationality: Indian" not in masked_text,
        "Nationality masked",
    )

    # --------------------------------------------------------------
    # Test 8 - Caste/community
    # --------------------------------------------------------------

    assert_true(
        "Caste: Example Community" not in masked_text,
        "Caste/community masked",
    )

    # --------------------------------------------------------------
    # Test 9 - Address
    # --------------------------------------------------------------

    assert_true(
        "10 Example Street" not in masked_text,
        "Address masked",
    )

    # --------------------------------------------------------------
    # Test 10 - Job-relevant skill preserved
    # --------------------------------------------------------------

    assert_true(
        "Python" in masked_text,
        "Job-relevant skill preserved",
    )

    # --------------------------------------------------------------
    # Test 11 - Job-relevant technology preserved
    # --------------------------------------------------------------

    assert_true(
        "Django" in masked_text,
        "Job-relevant technology preserved",
    )

    # --------------------------------------------------------------
    # Test 12 - Job-relevant experience preserved
    # --------------------------------------------------------------

    assert_true(
        "Python Developer" in masked_text,
        "Job-relevant experience preserved",
    )

    # --------------------------------------------------------------
    # Test 13 - Attribute detection
    # --------------------------------------------------------------

    detected = masker.detect_attributes(
        resume_text
    )

    assert_true(
        "email" in detected,
        "Email detected",
    )

    assert_true(
        "phone" in detected,
        "Phone detected",
    )

    assert_true(
        "gender" in detected,
        "Gender detected",
    )

    assert_true(
        "religion" in detected,
        "Religion detected",
    )

    # --------------------------------------------------------------
    # Structured resume
    # --------------------------------------------------------------

    structured_resume = {
        "name": "Test Candidate",
        "email": "test@example.com",
        "phone": "+91 98765 43210",
        "gender": "Male",
        "skills": [
            "Python",
            "Django",
        ],
        "experience": [
            {
                "job_title": "Python Developer",
                "company": "Example Technologies",
                "description": "Developed Python APIs.",
            }
        ],
    }

    original = structured_resume.copy()

    sanitized = masker.mask_resume_dict(
        structured_resume
    )

    # --------------------------------------------------------------
    # Test 14 - Structured email
    # --------------------------------------------------------------

    assert_equal(
        sanitized["email"],
        MASK,
        "Structured email masked",
    )

    # --------------------------------------------------------------
    # Test 15 - Structured phone
    # --------------------------------------------------------------

    assert_equal(
        sanitized["phone"],
        MASK,
        "Structured phone masked",
    )

    # --------------------------------------------------------------
    # Test 16 - Structured gender
    # --------------------------------------------------------------

    assert_equal(
        sanitized["gender"],
        MASK,
        "Structured gender masked",
    )

    # --------------------------------------------------------------
    # Test 17 - Structured skills preserved
    # --------------------------------------------------------------

    assert_equal(
        sanitized["skills"],
        [
            "Python",
            "Django",
        ],
        "Structured skills preserved",
    )

    # --------------------------------------------------------------
    # Test 18 - Original resume unchanged
    # --------------------------------------------------------------

    assert_equal(
        structured_resume,
        original,
        "Original resume remains unchanged",
    )

    # --------------------------------------------------------------
    # Test 19 - Invalid input
    # --------------------------------------------------------------

    assert_raises(
        TypeError,
        lambda: masker.mask_resume_dict(
            "invalid resume"
        ),
        "Invalid resume input rejected",
    )

    # --------------------------------------------------------------
    # Display results
    # --------------------------------------------------------------

    print("\n" + "=" * 70)
    print("MASKED RESUME TEXT")
    print("=" * 70)

    print(masked_text)

    print("\n" + "=" * 70)
    print("DETECTED ATTRIBUTES")
    print("=" * 70)

    for attribute in detected:
        print(
            f"- {attribute}"
        )

    print("\n" + "=" * 70)
    print(
        "DAY 15 PERSONAL ATTRIBUTE "
        "MASKING VALIDATION COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()