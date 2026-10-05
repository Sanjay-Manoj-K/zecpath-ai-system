"""
Day 16 - API Schema Validation
"""

from pydantic import ValidationError

from api.schemas import (
    ScoreRequest,
    ScoreResponse,
    ShortlistingRequest,
    JobCreateRequest,
    ResumeUploadResponse,
)


def assert_true(condition: bool, test_name: str) -> None:
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
        f"{test_name} FAILED: "
        f"expected {exception_type.__name__}"
    )


def main() -> None:

    print("=" * 70)
    print("DAY 16 - API SCHEMA VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------------
    # Test 1 - Resume upload response
    # --------------------------------------------------------------

    upload = ResumeUploadResponse(
        resume_id="RES-000001",
        filename="resume.pdf",
        status="UPLOADED",
        message="Resume uploaded successfully.",
    )

    assert_true(
        upload.resume_id == "RES-000001",
        "Resume upload response schema",
    )

    # --------------------------------------------------------------
    # Test 2 - Score request
    # --------------------------------------------------------------

    score_request = ScoreRequest(
        job_description_id="JD-000001"
    )

    assert_true(
        score_request.job_description_id
        == "JD-000001",
        "Score request schema",
    )

    # --------------------------------------------------------------
    # Test 3 - Score response
    # --------------------------------------------------------------

    score_response = ScoreResponse(
        resume_id="RES-000001",
        job_description_id="JD-000001",
        candidate_id="Candidate A",
        role="Python Developer",
        normalized_role="software_engineering",
        final_score=0.72,
        final_percentage=72.0,
    )

    assert_true(
        score_response.final_score == 0.72,
        "Score response schema",
    )

    # --------------------------------------------------------------
    # Test 4 - Shortlisting request
    # --------------------------------------------------------------

    shortlist_request = ShortlistingRequest(
        job_description_id="JD-000001",
        candidate_ids=[
            "RES-000001",
            "RES-000002",
        ],
        top_n=5,
    )

    assert_true(
        len(shortlist_request.candidate_ids) == 2,
        "Shortlisting request schema",
    )

    # --------------------------------------------------------------
    # Test 5 - Threshold defaults
    # --------------------------------------------------------------

    assert_true(
        shortlist_request.thresholds.shortlist
        == 0.70,
        "Shortlist threshold default",
    )

    assert_true(
        shortlist_request.thresholds.review
        == 0.50,
        "Review threshold default",
    )

    # --------------------------------------------------------------
    # Test 6 - Async job request
    # --------------------------------------------------------------

    job_request = JobCreateRequest(
        operation="score_and_rank",
        job_description_id="JD-000001",
        resume_ids=[
            "RES-000001",
            "RES-000002",
        ],
    )

    assert_true(
        job_request.operation
        == "score_and_rank",
        "Async job request schema",
    )

    # --------------------------------------------------------------
    # Test 7 - Invalid score
    # --------------------------------------------------------------

    assert_raises(
        ValidationError,
        lambda: ScoreResponse(
            resume_id="RES-1",
            job_description_id="JD-1",
            candidate_id="Candidate",
            role="Python Developer",
            normalized_role="software_engineering",
            final_score=1.5,
            final_percentage=150.0,
        ),
        "Invalid score rejected",
    )

    # --------------------------------------------------------------
    # Test 8 - Empty candidate list
    # --------------------------------------------------------------

    assert_raises(
        ValidationError,
        lambda: ShortlistingRequest(
            job_description_id="JD-000001",
            candidate_ids=[],
        ),
        "Empty candidate list rejected",
    )

    # --------------------------------------------------------------
    # Test 9 - Invalid top-N
    # --------------------------------------------------------------

    assert_raises(
        ValidationError,
        lambda: ShortlistingRequest(
            job_description_id="JD-000001",
            candidate_ids=["RES-000001"],
            top_n=0,
        ),
        "Invalid top-N rejected",
    )

    print("\n" + "=" * 70)
    print("DAY 16 API SCHEMAS VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()