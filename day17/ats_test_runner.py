"""
Day 17 - ATS System Testing

Runs the existing Day 13 -> Day 14 ATS pipeline against:

    5 job descriptions x 12 resumes = 60 test cases

The existing ATS engine is treated as a black-box system under test.
No ATS scoring logic is modified.

Binary evaluation rule:

    SHORTLIST / REVIEW -> AI-positive
    REJECT             -> AI-negative

Important:
If the existing ATS pipeline fails to produce a score for a candidate,
the case is recorded as EXECUTION_ERROR.

Execution errors are NOT counted as true/false positives or negatives.
Accuracy, precision and recall are calculated only over valid predictions.

Manual reference labels come from:
    day17.manual_review_dataset
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "day17"
)


# ============================================================================
# RUN EXISTING ATS
# ============================================================================

def run_existing_ats(
    job_file: str,
    resumes: list[str],
) -> str:
    """
    Execute the existing Day 14 ATS pipeline as a black box.

    UTF-8 is forced because the existing pipeline prints Unicode characters.
    """

    command = [
        sys.executable,
        "-X",
        "utf8",
        "-m",
        "scoring.day14_end_to_end",
        job_file,
        *resumes,
    ]

    print()
    print("=" * 90)
    print("DAY 17 ATS TEST BATCH")
    print("=" * 90)

    print(
        f"Job Description: {job_file}"
    )

    print(
        f"Resumes: {len(resumes)}"
    )

    child_env = os.environ.copy()

    child_env["PYTHONIOENCODING"] = "utf-8"
    child_env["PYTHONUTF8"] = "1"

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=child_env,
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            "ATS batch execution failed "
            f"with return code {result.returncode}"
        )

    return result.stdout


# ============================================================================
# EXTRACT ATS RESULTS
# ============================================================================

def extract_candidate_results(
    stdout: str,
    job_file: str,
) -> list[dict[str, Any]]:
    """
    Extract all candidate test results.

    A candidate can produce either:

        1. A valid ATS score
        2. An execution error

    Execution errors are retained instead of being silently dropped.
    """

    blocks = re.findall(
        r"PROCESSING CANDIDATE(.*?)(?="
        r"PROCESSING CANDIDATE|"
        r"DAY 14 - REAL CANDIDATE RANKING"
        r")",
        stdout,
        flags=re.DOTALL,
    )

    results: list[dict[str, Any]] = []

    for block in blocks:

        # --------------------------------------------------------------------
        # Resume path
        # --------------------------------------------------------------------

        resume_match = re.search(
            r"Resume:\s*(.+)",
            block,
        )

        if not resume_match:
            continue

        resume_path = (
            resume_match
            .group(1)
            .strip()
        )

        # --------------------------------------------------------------------
        # Candidate name
        # --------------------------------------------------------------------

        candidate_match = re.search(
            r"Candidate:\s*(.+)",
            block,
        )

        if candidate_match:

            candidate_name = (
                candidate_match
                .group(1)
                .strip()
            )

        else:

            candidate_name = (
                Path(resume_path)
                .stem
            )

        # --------------------------------------------------------------------
        # Look for ATS score
        # --------------------------------------------------------------------

        score_match = re.search(
            r"Day 13 ATS Score:\s*([0-9.]+)%",
            block,
        )

        # --------------------------------------------------------------------
        # VALID ATS RESULT
        # --------------------------------------------------------------------

        if score_match:

            score = float(
                score_match
                .group(1)
            )

            # Day 14 implementation defaults:
            #
            # >= 70 -> SHORTLIST
            # >= 50 -> REVIEW
            # < 50  -> REJECT

            if score >= 70:

                status = "SHORTLIST"

            elif score >= 50:

                status = "REVIEW"

            else:

                status = "REJECT"

            results.append(
                {
                    "job_description": job_file,
                    "resume_file": resume_path,
                    "candidate_name": candidate_name,
                    "ats_score_percentage": score,
                    "ats_status": status,
                    "execution_status": "SUCCESS",
                    "error_reason": None,
                }
            )

            continue

        # --------------------------------------------------------------------
        # EXECUTION ERROR
        # --------------------------------------------------------------------

        error_match = re.search(
            r"ERROR processing:\s*"
            r"Resume:\s*(.+?)\s*"
            r"Reason:\s*(.+?)(?:\n\s*\n|\Z)",
            block,
            flags=re.DOTALL,
        )

        if error_match:

            error_resume = (
                error_match
                .group(1)
                .strip()
            )

            error_reason = (
                error_match
                .group(2)
                .strip()
            )

            results.append(
                {
                    "job_description": job_file,
                    "resume_file": error_resume,
                    "candidate_name": candidate_name,
                    "ats_score_percentage": None,
                    "ats_status": "ERROR",
                    "execution_status": "ERROR",
                    "error_reason": error_reason,
                }
            )

    return results


# ============================================================================
# BUILD MANUAL LOOKUP
# ============================================================================

def build_lookup(
    dataset: list[dict[str, Any]],
) -> dict[
    tuple[str, str],
    dict[str, Any],
]:
    """
    Create manual reference lookup using:

        (job_file, resume_file)
    """

    lookup: dict[
        tuple[str, str],
        dict[str, Any],
    ] = {}

    for case in dataset:

        job_file = (
            str(
                Path(
                    case["job_file"]
                )
            )
            .replace("/", "\\")
        )

        resume_file = (
            str(
                Path(
                    case["resume_file"]
                )
            )
            .replace("/", "\\")
        )

        lookup[
            (
                job_file.lower(),
                resume_file.lower(),
            )
        ] = case

    return lookup


# ============================================================================
# EVALUATE RESULT
# ============================================================================

def evaluate_result(
    result: dict[str, Any],
    manual_case: dict[str, Any],
) -> dict[str, Any]:
    """
    Compare ATS output against manual reference.

    Execution errors are kept separate from binary classification.
    """

    evaluated = dict(result)

    manual_suitable = bool(
        manual_case["manual_suitable"]
    )

    # ------------------------------------------------------------------------
    # EXECUTION ERROR
    # ------------------------------------------------------------------------

    if result["execution_status"] == "ERROR":

        evaluated.update(
            {
                "role": manual_case["role"],
                "role_type": manual_case["role_type"],
                "manual_suitable": manual_suitable,
                "ai_positive": None,
                "outcome": "EXECUTION_ERROR",
                "manual_basis": manual_case[
                    "manual_basis"
                ],
            }
        )

        return evaluated

    # ------------------------------------------------------------------------
    # VALID ATS PREDICTION
    # ------------------------------------------------------------------------

    ai_positive = (
        result["ats_status"]
        in {
            "SHORTLIST",
            "REVIEW",
        }
    )

    if manual_suitable and ai_positive:

        outcome = "TRUE_POSITIVE"

    elif (
        not manual_suitable
        and not ai_positive
    ):

        outcome = "TRUE_NEGATIVE"

    elif manual_suitable and not ai_positive:

        outcome = "FALSE_NEGATIVE"

    else:

        outcome = "FALSE_POSITIVE"

    evaluated.update(
        {
            "role": manual_case["role"],
            "role_type": manual_case["role_type"],
            "manual_suitable": manual_suitable,
            "ai_positive": ai_positive,
            "outcome": outcome,
            "manual_basis": manual_case[
                "manual_basis"
            ],
        }
    )

    return evaluated


# ============================================================================
# CALCULATE METRICS
# ============================================================================

def calculate_metrics(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calculate confusion-matrix metrics only over successful ATS predictions.

    Execution errors are reported separately.
    """

    total_cases = len(results)

    execution_errors = sum(
        1
        for item in results
        if item["outcome"] == "EXECUTION_ERROR"
    )

    valid_results = [
        item
        for item in results
        if item["outcome"] != "EXECUTION_ERROR"
    ]

    valid_predictions = len(
        valid_results
    )

    true_positive = sum(
        1
        for item in valid_results
        if item["outcome"] == "TRUE_POSITIVE"
    )

    true_negative = sum(
        1
        for item in valid_results
        if item["outcome"] == "TRUE_NEGATIVE"
    )

    false_positive = sum(
        1
        for item in valid_results
        if item["outcome"] == "FALSE_POSITIVE"
    )

    false_negative = sum(
        1
        for item in valid_results
        if item["outcome"] == "FALSE_NEGATIVE"
    )

    # ------------------------------------------------------------------------
    # Accuracy
    # ------------------------------------------------------------------------

    if valid_predictions:

        accuracy = (
            true_positive
            + true_negative
        ) / valid_predictions

    else:

        accuracy = 0.0

    # ------------------------------------------------------------------------
    # Precision
    # ------------------------------------------------------------------------

    predicted_positive = (
        true_positive
        + false_positive
    )

    if predicted_positive:

        precision = (
            true_positive
            / predicted_positive
        )

    else:

        precision = 0.0

    # ------------------------------------------------------------------------
    # Recall
    # ------------------------------------------------------------------------

    actual_positive = (
        true_positive
        + false_negative
    )

    if actual_positive:

        recall = (
            true_positive
            / actual_positive
        )

    else:

        recall = 0.0

    # ------------------------------------------------------------------------
    # Reliability metrics
    # ------------------------------------------------------------------------

    if total_cases:

        prediction_coverage = (
            valid_predictions
            / total_cases
        )

        execution_error_rate = (
            execution_errors
            / total_cases
        )

    else:

        prediction_coverage = 0.0
        execution_error_rate = 0.0

    return {
        "total_cases": total_cases,
        "valid_predictions": valid_predictions,
        "execution_errors": execution_errors,
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "accuracy": round(
            accuracy,
            4,
        ),
        "precision": round(
            precision,
            4,
        ),
        "recall": round(
            recall,
            4,
        ),
        "prediction_coverage": round(
            prediction_coverage,
            4,
        ),
        "execution_error_rate": round(
            execution_error_rate,
            4,
        ),
    }


# ============================================================================
# ROLE-WISE METRICS
# ============================================================================

def calculate_role_metrics(
    results: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """
    Calculate metrics separately for each role.
    """

    role_groups: dict[
        str,
        list[dict[str, Any]],
    ] = {}

    for item in results:

        role = item["role"]

        role_groups.setdefault(
            role,
            [],
        ).append(item)

    role_metrics: dict[
        str,
        dict[str, Any],
    ] = {}

    for role, role_results in role_groups.items():

        role_metrics[role] = (
            calculate_metrics(
                role_results
            )
        )

    return role_metrics


# ============================================================================
# SAVE RESULTS
# ============================================================================

def save_results(
    results: list[dict[str, Any]],
    metrics: dict[str, Any],
    role_metrics: dict[str, Any],
) -> None:
    """
    Save detailed test cases and metrics.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_file = (
        OUTPUT_DIR
        / "day17_test_results.json"
    )

    metrics_file = (
        OUTPUT_DIR
        / "day17_accuracy_metrics.json"
    )

    # ------------------------------------------------------------------------
    # Detailed results
    # ------------------------------------------------------------------------

    with results_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # ------------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------------

    with metrics_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            {
                "overall": metrics,
                "by_role": role_metrics,
            },
            file,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================================
# PRINT SUMMARY
# ============================================================================

def print_summary(
    results: list[dict[str, Any]],
    metrics: dict[str, Any],
    role_metrics: dict[str, Any],
) -> None:
    """
    Print complete Day 17 testing summary.
    """

    print()
    print("=" * 90)
    print("DAY 17 - ATS TESTING SUMMARY")
    print("=" * 90)

    # ------------------------------------------------------------------------
    # INDIVIDUAL RESULTS
    # ------------------------------------------------------------------------

    for item in results:

        score = item[
            "ats_score_percentage"
        ]

        if score is None:

            score_text = "ERROR "

        else:

            score_text = (
                f"{score:6.2f}%"
            )

        print(
            f"{item['role']:20} | "
            f"{item['candidate_name'][:38]:38} | "
            f"{score_text:7} | "
            f"{item['ats_status']:9} | "
            f"{item['outcome']}"
        )

        # Print execution error details
        if (
            item["outcome"]
            == "EXECUTION_ERROR"
        ):

            print(
                f"  ERROR: "
                f"{item['error_reason']}"
            )

    # ------------------------------------------------------------------------
    # OVERALL METRICS
    # ------------------------------------------------------------------------

    print()
    print("=" * 90)
    print("OVERALL METRICS")
    print("=" * 90)

    print(
        f"Total test cases       : "
        f"{metrics['total_cases']}"
    )

    print(
        f"Valid ATS predictions  : "
        f"{metrics['valid_predictions']}"
    )

    print(
        f"Execution errors       : "
        f"{metrics['execution_errors']}"
    )

    print(
        f"True positives         : "
        f"{metrics['true_positive']}"
    )

    print(
        f"True negatives         : "
        f"{metrics['true_negative']}"
    )

    print(
        f"False positives        : "
        f"{metrics['false_positive']}"
    )

    print(
        f"False negatives        : "
        f"{metrics['false_negative']}"
    )

    print(
        f"Accuracy               : "
        f"{metrics['accuracy'] * 100:.2f}%"
    )

    print(
        f"Precision              : "
        f"{metrics['precision'] * 100:.2f}%"
    )

    print(
        f"Recall                 : "
        f"{metrics['recall'] * 100:.2f}%"
    )

    print(
        f"Prediction coverage   : "
        f"{metrics['prediction_coverage'] * 100:.2f}%"
    )

    print(
        f"Execution error rate  : "
        f"{metrics['execution_error_rate'] * 100:.2f}%"
    )

    # ------------------------------------------------------------------------
    # ROLE-WISE METRICS
    # ------------------------------------------------------------------------

    print()
    print("=" * 90)
    print("ROLE-WISE METRICS")
    print("=" * 90)

    for role, role_metric in role_metrics.items():

        print(
            f"{role:20} | "
            f"Cases: "
            f"{role_metric['total_cases']:2} | "
            f"Valid: "
            f"{role_metric['valid_predictions']:2} | "
            f"Errors: "
            f"{role_metric['execution_errors']:2} | "
            f"Accuracy: "
            f"{role_metric['accuracy'] * 100:6.2f}% | "
            f"Precision: "
            f"{role_metric['precision'] * 100:6.2f}% | "
            f"Recall: "
            f"{role_metric['recall'] * 100:6.2f}%"
        )

    # ------------------------------------------------------------------------
    # EXECUTION ERRORS
    # ------------------------------------------------------------------------

    error_cases = [
        item
        for item in results
        if item["outcome"]
        == "EXECUTION_ERROR"
    ]

    print()
    print("=" * 90)
    print("EXECUTION ERROR CASES")
    print("=" * 90)

    if error_cases:

        for item in error_cases:

            print(
                f"Role    : "
                f"{item['role']}"
            )

            print(
                f"Candidate: "
                f"{item['candidate_name']}"
            )

            print(
                f"Resume  : "
                f"{item['resume_file']}"
            )

            print(
                f"Reason  : "
                f"{item['error_reason']}"
            )

            print("-" * 90)

    else:

        print(
            "No execution errors."
        )

    # ------------------------------------------------------------------------
    # OUTPUT FILES
    # ------------------------------------------------------------------------

    print()
    print(
        "Results saved to: "
        "outputs\\day17\\day17_test_results.json"
    )

    print(
        "Metrics saved to: "
        "outputs\\day17\\day17_accuracy_metrics.json"
    )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:

    # ------------------------------------------------------------------------
    # Import manual reference dataset
    # ------------------------------------------------------------------------

    try:

        from day17.manual_review_dataset import (
            JOBS,
            build_manual_reference_dataset,
        )

    except ModuleNotFoundError:

        from manual_review_dataset import (
            JOBS,
            build_manual_reference_dataset,
        )

    # ------------------------------------------------------------------------
    # Build 60-case reference dataset
    # ------------------------------------------------------------------------

    dataset = (
        build_manual_reference_dataset()
    )

    print()
    print("=" * 90)
    print("DAY 17 - ATS SYSTEM TESTING")
    print("=" * 90)

    print(
        f"Expected test cases: "
        f"{len(dataset)}"
    )

    print(
        f"Job descriptions   : "
        f"{len(JOBS)}"
    )

    print(
        "Expected structure : "
        "5 JDs x 12 resumes = 60 cases"
    )

    # ------------------------------------------------------------------------
    # Build manual lookup
    # ------------------------------------------------------------------------

    lookup = build_lookup(
        dataset
    )

    all_results: list[
        dict[str, Any]
    ] = []

    # ------------------------------------------------------------------------
    # Run all five roles
    # ------------------------------------------------------------------------

    for role, job in JOBS.items():

        print()
        print()
        print("#" * 90)

        print(
            f"TESTING ROLE: {role}"
        )

        print(
            "#" * 90
        )

        job_path = str(
            Path(
                "data/day12_benchmarks"
            )
            / job["file"]
        )

        resume_paths = [
            case["resume_file"]
            for case in dataset
            if case["role"] == role
        ]

        print(
            f"Role: {role}"
        )

        print(
            f"Role type: "
            f"{job['role_type']}"
        )

        print(
            f"Reference resumes: "
            f"{len(resume_paths)}"
        )

        # --------------------------------------------------------------------
        # Existing ATS pipeline
        # --------------------------------------------------------------------

        stdout = run_existing_ats(
            job_path,
            resume_paths,
        )

        # --------------------------------------------------------------------
        # Parse both successes and errors
        # --------------------------------------------------------------------

        ats_results = (
            extract_candidate_results(
                stdout,
                job_path,
            )
        )

        print(
            f"ATS results extracted: "
            f"{len(ats_results)}"
        )

        # --------------------------------------------------------------------
        # Match with manual reference cases
        # --------------------------------------------------------------------

        for result in ats_results:

            job_key = (
                str(
                    Path(
                        result[
                            "job_description"
                        ]
                    )
                )
                .replace(
                    "/",
                    "\\",
                )
            )

            resume_key = (
                str(
                    Path(
                        result[
                            "resume_file"
                        ]
                    )
                )
                .replace(
                    "/",
                    "\\",
                )
            )

            manual_case = lookup.get(
                (
                    job_key.lower(),
                    resume_key.lower(),
                )
            )

            if manual_case is None:

                print()
                print(
                    "WARNING: Manual reference "
                    "not found."
                )

                print(
                    f"Job: {job_key}"
                )

                print(
                    f"Resume: {resume_key}"
                )

                continue

            evaluated = evaluate_result(
                result,
                manual_case,
            )

            all_results.append(
                evaluated
            )

    # ------------------------------------------------------------------------
    # Validate that all 60 cases were observed
    # ------------------------------------------------------------------------

    expected_cases = len(
        dataset
    )

    actual_cases = len(
        all_results
    )

    print()
    print("=" * 90)
    print("DAY 17 DATASET VALIDATION")
    print("=" * 90)

    print(
        f"Expected cases : "
        f"{expected_cases}"
    )

    print(
        f"Observed cases : "
        f"{actual_cases}"
    )

    if actual_cases != expected_cases:

        raise RuntimeError(
            f"Expected {expected_cases} "
            f"test cases but observed "
            f"{actual_cases}."
        )

    print(
        "Dataset validation: PASSED"
    )

    # ------------------------------------------------------------------------
    # Calculate metrics
    # ------------------------------------------------------------------------

    metrics = calculate_metrics(
        all_results
    )

    role_metrics = (
        calculate_role_metrics(
            all_results
        )
    )

    # ------------------------------------------------------------------------
    # Save results
    # ------------------------------------------------------------------------

    save_results(
        all_results,
        metrics,
        role_metrics,
    )

    # ------------------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------------------

    print_summary(
        all_results,
        metrics,
        role_metrics,
    )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()