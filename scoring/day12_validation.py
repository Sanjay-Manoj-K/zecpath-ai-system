"""
Day 12 - Semantic Matching Validation and Threshold Evaluation

Purpose:
    Validate the semantic matching engine across multiple resumes
    and benchmark Job Descriptions.

This script:
    1. Loads all resumes.
    2. Loads all benchmark JDs.
    3. Calculates semantic section scores.
    4. Stores every resume-JD comparison.
    5. Evaluates multiple similarity thresholds.
    6. Calculates accuracy, precision, recall, and F1.
    7. Saves detailed comparison results to CSV.
    8. Saves threshold evaluation results to CSV.

Important:
    The benchmark labels are controlled test labels for this
    Day 12 evaluation dataset. They should not be interpreted as
    real-world ATS accuracy.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from parsers.resume_text_extractor import extract_resume_text
from parsers.resume_parser import parse_resume_text
from parsers.jd_parser import read_job_description, parse_job_description
from scoring.semantic_matching import SemanticMatchingEngine


# ============================================================
# CONFIGURATION
# ============================================================

RESUME_DIR = Path("data/resumes")
BENCHMARK_JD_DIR = Path("data/day12_benchmarks")

MODEL_NAME = "all-MiniLM-L6-v2"

# Current/default threshold used by the semantic engine.
DEFAULT_THRESHOLD = 0.55

# Thresholds to evaluate.
THRESHOLDS = [
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
]

# Output files.
COMPARISON_RESULTS_FILE = (
    BENCHMARK_JD_DIR / "day12_semantic_results.csv"
)

THRESHOLD_RESULTS_FILE = (
    BENCHMARK_JD_DIR / "day12_threshold_evaluation.csv"
)


# ============================================================
# CONTROLLED BENCHMARK LABELS
# ============================================================

# Each pair below is an intentionally related resume-JD pair
# in the Day 12 benchmark dataset.

POSITIVE_PAIRS = {
    (
        "ai-developer-resume.docx",
        "ai_ml_engineer.txt",
    ),

    (
        "data-scientist-resume.pdf",
        "data_scientist.txt",
    ),

    (
        "finance-resume.docx",
        "finance_analyst.txt",
    ),

    (
        "legal-resume.docx",
        "legal_intern.txt",
    ),

    (
        "software-engineering-resume.docx",
        "software_engineer.txt",
    ),
}


# ============================================================
# HELPERS
# ============================================================

def join_items(items: List[str]) -> str:
    """
    Convert a list of strings into one semantic text block.
    """

    if not items:
        return ""

    cleaned_items = []

    for item in items:

        if item is None:
            continue

        text = str(item).strip()

        if text:
            cleaned_items.append(text)

    return ". ".join(cleaned_items)


def format_score(value) -> str:
    """
    Format a numeric score or unavailable value.
    """

    if value is None:
        return "N/A"

    return f"{value:.4f}"


# ============================================================
# RESUME LOADING
# ============================================================

def build_resume_profile(
    resume_path: Path,
) -> Dict:
    """
    Extract and parse one resume using the project's
    existing parser architecture.
    """

    resume_text = extract_resume_text(
        str(resume_path)
    )

    candidate = parse_resume_text(
        resume_text
    )

    return {
        "name": candidate.get(
            "name",
            "",
        ),

        "skills": candidate.get(
            "skills",
            [],
        ),

        "experience": candidate.get(
            "experience",
            "",
        ),

        "education": candidate.get(
            "education",
            "",
        ),

        "certifications": candidate.get(
            "certifications",
            [],
        ),

        "full_text": resume_text,
    }


# ============================================================
# JOB DESCRIPTION LOADING
# ============================================================

def build_jd_profile(
    jd_path: Path,
) -> Dict:
    """
    Read and parse one benchmark Job Description.
    """

    jd_text = read_job_description(
        str(jd_path)
    )

    job = parse_job_description(
        jd_text
    )

    return {
        "role": job.get(
            "role",
            "",
        ),

        "required_skills": job.get(
            "required_skills",
            [],
        ),

        "experience": job.get(
            "experience",
            "",
        ),

        "education": job.get(
            "education",
            "",
        ),

        "responsibilities": job.get(
            "responsibilities",
            [],
        ),

        "full_text": jd_text,
    }


# ============================================================
# RESUME-JD SEMANTIC COMPARISON
# ============================================================

def compare_resume_to_jd(
    engine: SemanticMatchingEngine,
    resume: Dict,
    jd: Dict,
) -> Dict:
    """
    Compare one resume against one JD.

    Empty sections remain empty.
    The semantic engine skips unavailable sections.
    """

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    resume_skills = join_items(
        resume.get(
            "skills",
            [],
        )
    )

    jd_skills = join_items(
        jd.get(
            "required_skills",
            [],
        )
    )

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    resume_experience = str(
        resume.get(
            "experience",
            "",
        )
        or ""
    ).strip()

    jd_experience = str(
        jd.get(
            "experience",
            "",
        )
        or ""
    ).strip()

    # --------------------------------------------------------
    # Context / Projects
    # --------------------------------------------------------
    #
    # Current resume_parser.py does not expose a dedicated
    # project field.
    #
    # Therefore, use full resume text as resume context.
    # JD responsibilities provide the corresponding JD context.
    # --------------------------------------------------------

    resume_context = str(
        resume.get(
            "full_text",
            "",
        )
        or ""
    ).strip()

    jd_context = join_items(
        jd.get(
            "responsibilities",
            [],
        )
    )

    # --------------------------------------------------------
    # Generate section-level results.
    #
    # The engine's match() method uses the default threshold,
    # but the section scores are independent of threshold.
    # --------------------------------------------------------

    result = engine.match(
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        resume_experience=resume_experience,
        jd_experience=jd_experience,
        resume_projects=resume_context,
        jd_projects=jd_context,
    )

    return {
        "overall_similarity": result.overall_similarity,
        "skill_similarity": result.skill_similarity,
        "experience_similarity": result.experience_similarity,
        "project_similarity": result.project_similarity,
    }


# ============================================================
# BENCHMARK LABEL
# ============================================================

def is_expected_match(
    resume_name: str,
    jd_name: str,
) -> bool:
    """
    Return the controlled benchmark label.

    True  = intentionally related pair.
    False = intentionally unrelated pair.
    """

    return (
        resume_name,
        jd_name,
    ) in POSITIVE_PAIRS


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    results: List[Dict],
    threshold: float,
) -> Dict:
    """
    Calculate classification metrics for one threshold.
    """

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0

    for row in results:

        predicted_match = (
            row["overall_similarity"]
            >= threshold
        )

        expected_match = row["expected_match"]

        if predicted_match and expected_match:
            true_positive += 1

        elif not predicted_match and not expected_match:
            true_negative += 1

        elif predicted_match and not expected_match:
            false_positive += 1

        elif not predicted_match and expected_match:
            false_negative += 1

    total = (
        true_positive
        + true_negative
        + false_positive
        + false_negative
    )

    accuracy = (
        (true_positive + true_negative) / total
        if total
        else 0.0
    )

    precision_denominator = (
        true_positive + false_positive
    )

    precision = (
        true_positive / precision_denominator
        if precision_denominator
        else 0.0
    )

    recall_denominator = (
        true_positive + false_negative
    )

    recall = (
        true_positive / recall_denominator
        if recall_denominator
        else 0.0
    )

    f1_denominator = (
        precision + recall
    )

    f1 = (
        2 * precision * recall / f1_denominator
        if f1_denominator
        else 0.0
    )

    return {
        "threshold": threshold,

        "true_positive": true_positive,
        "true_negative": true_negative,

        "false_positive": false_positive,
        "false_negative": false_negative,

        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


# ============================================================
# CSV: DETAILED COMPARISON RESULTS
# ============================================================

def save_comparison_results(
    results: List[Dict],
    output_file: Path,
) -> None:
    """
    Save all resume-JD semantic comparisons to CSV.
    """

    fieldnames = [
        "resume",
        "jd",
        "expected_match",
        "overall_similarity",
        "skill_similarity",
        "experience_similarity",
        "project_similarity",
    ]

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in results:

            writer.writerow({
                "resume": row["resume"],
                "jd": row["jd"],
                "expected_match": row["expected_match"],
                "overall_similarity": row[
                    "overall_similarity"
                ],
                "skill_similarity": row[
                    "skill_similarity"
                ],
                "experience_similarity": row[
                    "experience_similarity"
                ],
                "project_similarity": row[
                    "project_similarity"
                ],
            })

    print(
        f"\nDetailed comparison results saved to:"
        f"\n  {output_file}"
    )


# ============================================================
# CSV: THRESHOLD EVALUATION
# ============================================================

def save_threshold_results(
    threshold_results: List[Dict],
    output_file: Path,
) -> None:
    """
    Save threshold evaluation metrics to CSV.
    """

    fieldnames = [
        "threshold",
        "true_positive",
        "true_negative",
        "false_positive",
        "false_negative",
        "accuracy",
        "precision",
        "recall",
        "f1",
    ]

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in threshold_results:
            writer.writerow(row)

    print(
        f"Threshold evaluation saved to:"
        f"\n  {output_file}"
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print("=" * 80)
    print("DAY 12 - SEMANTIC MATCHING AND THRESHOLD EVALUATION")
    print("=" * 80)

    print(
        f"\nResume directory: "
        f"{RESUME_DIR}"
    )

    print(
        f"Benchmark JD directory: "
        f"{BENCHMARK_JD_DIR}"
    )

    print(
        f"Semantic model: "
        f"{MODEL_NAME}"
    )

    print(
        f"Default threshold: "
        f"{DEFAULT_THRESHOLD}"
    )

    # ========================================================
    # DIRECTORY CHECKS
    # ========================================================

    if not RESUME_DIR.exists():

        print(
            f"\nERROR: Resume directory not found:"
            f" {RESUME_DIR}"
        )

        return

    if not BENCHMARK_JD_DIR.exists():

        print(
            f"\nERROR: Benchmark JD directory not found:"
            f" {BENCHMARK_JD_DIR}"
        )

        return

    # ========================================================
    # DISCOVER FILES
    # ========================================================

    resume_files = sorted(
        [
            path
            for path in RESUME_DIR.iterdir()
            if path.is_file()
            and path.suffix.lower()
            in {
                ".docx",
                ".pdf",
                ".txt",
            }
        ]
    )

    jd_files = sorted(
        [
            path
            for path in BENCHMARK_JD_DIR.iterdir()
            if path.is_file()
            and path.suffix.lower() == ".txt"
        ]
    )

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    if not resume_files:

        print(
            "\nERROR: No resume files found."
        )

        return

    if not jd_files:

        print(
            "\nERROR: No benchmark JD files found."
        )

        return

    print(
        f"\nFound {len(resume_files)} resumes."
    )

    print(
        f"Found {len(jd_files)} benchmark JDs."
    )

    print(
        f"Expected positive benchmark pairs:"
        f" {len(POSITIVE_PAIRS)}"
    )

    # ========================================================
    # LOAD ENGINE
    # ========================================================

    print(
        "\nLoading semantic matching engine..."
    )

    engine = SemanticMatchingEngine(
        model_name=MODEL_NAME,
        threshold=DEFAULT_THRESHOLD,
    )

    # ========================================================
    # LOAD RESUMES
    # ========================================================

    print("\n" + "-" * 80)
    print("LOADING RESUMES")
    print("-" * 80)

    resumes: Dict[str, Dict] = {}

    for resume_path in resume_files:

        print(
            f"\nProcessing resume:"
            f" {resume_path.name}"
        )

        try:

            profile = build_resume_profile(
                resume_path
            )

            resumes[resume_path.name] = profile

            print(
                f"  Name: "
                f"{profile['name']}"
            )

            print(
                f"  Skills detected: "
                f"{len(profile['skills'])}"
            )

            print(
                f"  Resume characters: "
                f"{len(profile['full_text'])}"
            )

            print(
                f"  Experience available: "
                f"{bool(profile['experience'].strip())}"
            )

        except Exception as exc:

            print(
                f"  ERROR: {exc}"
            )

    # ========================================================
    # LOAD JOB DESCRIPTIONS
    # ========================================================

    print("\n" + "-" * 80)
    print("LOADING BENCHMARK JOB DESCRIPTIONS")
    print("-" * 80)

    jobs: Dict[str, Dict] = {}

    for jd_path in jd_files:

        print(
            f"\nProcessing JD:"
            f" {jd_path.name}"
        )

        try:

            profile = build_jd_profile(
                jd_path
            )

            jobs[jd_path.name] = profile

            print(
                f"  Role: "
                f"{profile['role']}"
            )

            print(
                f"  Required skills detected: "
                f"{len(profile['required_skills'])}"
            )

            print(
                f"  Experience requirement available: "
                f"{bool(profile['experience'].strip())}"
            )

            print(
                f"  Responsibilities detected: "
                f"{len(profile['responsibilities'])}"
            )

        except Exception as exc:

            print(
                f"  ERROR: {exc}"
            )

    # ========================================================
    # RUN ALL COMPARISONS
    # ========================================================

    print("\n" + "=" * 80)
    print("SEMANTIC MATCHING RESULTS")
    print("=" * 80)

    results: List[Dict] = []

    for resume_name, resume in resumes.items():

        print(
            f"\nResume: "
            f"{resume_name}"
        )

        print(
            "-" * 80
        )

        for jd_name, jd in jobs.items():

            try:

                scores = compare_resume_to_jd(
                    engine=engine,
                    resume=resume,
                    jd=jd,
                )

                expected_match = is_expected_match(
                    resume_name,
                    jd_name,
                )

                row = {
                    "resume": resume_name,
                    "jd": jd_name,

                    "expected_match": expected_match,

                    "overall_similarity":
                        scores["overall_similarity"],

                    "skill_similarity":
                        scores["skill_similarity"],

                    "experience_similarity":
                        scores["experience_similarity"],

                    "project_similarity":
                        scores["project_similarity"],
                }

                results.append(row)

                print(
                    f"{jd_name:<25} "
                    f"Overall="
                    f"{format_score(row['overall_similarity'])}  "
                    f"Skills="
                    f"{format_score(row['skill_similarity'])}  "
                    f"Experience="
                    f"{format_score(row['experience_similarity'])}  "
                    f"Context="
                    f"{format_score(row['project_similarity'])}  "
                    f"Expected="
                    f"{row['expected_match']}"
                )

            except Exception as exc:

                print(
                    f"{jd_name:<25} "
                    f"ERROR: {exc}"
                )

    # ========================================================
    # SAVE DETAILED RESULTS
    # ========================================================

    if not results:

        print(
            "\nERROR: No semantic comparisons were produced."
        )

        return

    save_comparison_results(
        results,
        COMPARISON_RESULTS_FILE,
    )

    # ========================================================
    # THRESHOLD EVALUATION
    # ========================================================

    print("\n" + "=" * 80)
    print("THRESHOLD EVALUATION")
    print("=" * 80)

    threshold_results = []

    for threshold in THRESHOLDS:

        metrics = calculate_metrics(
            results,
            threshold,
        )

        threshold_results.append(
            metrics
        )

        print(
            f"\nThreshold: "
            f"{threshold:.2f}"
        )

        print(
            f"  TP: {metrics['true_positive']}"
        )

        print(
            f"  TN: {metrics['true_negative']}"
        )

        print(
            f"  FP: {metrics['false_positive']}"
        )

        print(
            f"  FN: {metrics['false_negative']}"
        )

        print(
            f"  Accuracy: "
            f"{metrics['accuracy']:.4f}"
        )

        print(
            f"  Precision: "
            f"{metrics['precision']:.4f}"
        )

        print(
            f"  Recall: "
            f"{metrics['recall']:.4f}"
        )

        print(
            f"  F1: "
            f"{metrics['f1']:.4f}"
        )

    # ========================================================
    # SAVE THRESHOLD RESULTS
    # ========================================================

    save_threshold_results(
        threshold_results,
        THRESHOLD_RESULTS_FILE,
    )

    # ========================================================
    # CURRENT THRESHOLD SUMMARY
    # ========================================================

    current_metrics = calculate_metrics(
        results,
        DEFAULT_THRESHOLD,
    )

    print("\n" + "=" * 80)
    print(
        f"RESULT AT DEFAULT THRESHOLD "
        f"{DEFAULT_THRESHOLD:.2f}"
    )
    print("=" * 80)

    print(
        f"\nAccuracy : "
        f"{current_metrics['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{current_metrics['precision']:.4f}"
    )

    print(
        f"Recall   : "
        f"{current_metrics['recall']:.4f}"
    )

    print(
        f"F1       : "
        f"{current_metrics['f1']:.4f}"
    )

    print(
        f"\nTP={current_metrics['true_positive']}, "
        f"TN={current_metrics['true_negative']}, "
        f"FP={current_metrics['false_positive']}, "
        f"FN={current_metrics['false_negative']}"
    )

    # ========================================================
    # VALIDATION SUMMARY
    # ========================================================

    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    print(
        f"\nTotal resumes tested : "
        f"{len(resumes)}"
    )

    print(
        f"Total JDs tested     : "
        f"{len(jobs)}"
    )

    print(
        f"Total comparisons    : "
        f"{len(results)}"
    )

    positive_count = sum(
        1
        for row in results
        if row["expected_match"]
    )

    negative_count = (
        len(results) - positive_count
    )

    print(
        f"Expected positive pairs: "
        f"{positive_count}"
    )

    print(
        f"Expected negative pairs: "
        f"{negative_count}"
    )

    # --------------------------------------------------------
    # Average score
    # --------------------------------------------------------

    average_score = (
        sum(
            row["overall_similarity"]
            for row in results
        )
        / len(results)
    )

    print(
        f"Average semantic similarity: "
        f"{average_score:.4f}"
    )

    # --------------------------------------------------------
    # Positive-pair score summary
    # --------------------------------------------------------

    positive_scores = [
        row["overall_similarity"]
        for row in results
        if row["expected_match"]
    ]

    negative_scores = [
        row["overall_similarity"]
        for row in results
        if not row["expected_match"]
    ]

    if positive_scores:

        print(
            f"Average positive-pair similarity: "
            f"{sum(positive_scores) / len(positive_scores):.4f}"
        )

        print(
            f"Minimum positive-pair similarity: "
            f"{min(positive_scores):.4f}"
        )

        print(
            f"Maximum positive-pair similarity: "
            f"{max(positive_scores):.4f}"
        )

    if negative_scores:

        print(
            f"Average negative-pair similarity: "
            f"{sum(negative_scores) / len(negative_scores):.4f}"
        )

        print(
            f"Minimum negative-pair similarity: "
            f"{min(negative_scores):.4f}"
        )

        print(
            f"Maximum negative-pair similarity: "
            f"{max(negative_scores):.4f}"
        )

    # --------------------------------------------------------
    # Highest and lowest
    # --------------------------------------------------------

    highest = max(
        results,
        key=lambda row:
        row["overall_similarity"],
    )

    lowest = min(
        results,
        key=lambda row:
        row["overall_similarity"],
    )

    print(
        "\nHighest similarity:"
    )

    print(
        f"  Resume: "
        f"{highest['resume']}"
    )

    print(
        f"  JD: "
        f"{highest['jd']}"
    )

    print(
        f"  Score: "
        f"{highest['overall_similarity']:.4f}"
    )

    print(
        f"  Expected match: "
        f"{highest['expected_match']}"
    )

    print(
        "\nLowest similarity:"
    )

    print(
        f"  Resume: "
        f"{lowest['resume']}"
    )

    print(
        f"  JD: "
        f"{lowest['jd']}"
    )

    print(
        f"  Score: "
        f"{lowest['overall_similarity']:.4f}"
    )

    print(
        f"  Expected match: "
        f"{lowest['expected_match']}"
    )

    # ========================================================
    # SECTION AVAILABILITY
    # ========================================================

    skill_available_count = sum(
        1
        for row in results
        if row["skill_similarity"] is not None
    )

    experience_available_count = sum(
        1
        for row in results
        if row["experience_similarity"] is not None
    )

    context_available_count = sum(
        1
        for row in results
        if row["project_similarity"] is not None
    )

    print("\nSECTION AVAILABILITY")

    print(
        f"  Skill comparisons: "
        f"{skill_available_count}/"
        f"{len(results)}"
    )

    print(
        f"  Experience comparisons: "
        f"{experience_available_count}/"
        f"{len(results)}"
    )

    print(
        f"  Context comparisons: "
        f"{context_available_count}/"
        f"{len(results)}"
    )

    # ========================================================
    # COMPLETION
    # ========================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "DAY 12 SEMANTIC MATCHING AND "
        "THRESHOLD EVALUATION COMPLETE"
    )

    print(
        "=" * 80
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()