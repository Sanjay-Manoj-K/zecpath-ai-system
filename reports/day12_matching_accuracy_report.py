"""
Day 12 - Matching Accuracy Report Generator

Purpose:
    Read the Day 12 semantic matching and threshold evaluation CSV files
    and generate a human-readable Markdown report.

Input:
    data/day12_benchmarks/day12_semantic_results.csv
    data/day12_benchmarks/day12_threshold_evaluation.csv

Output:
    reports/day12_matching_accuracy_report.md
"""

from __future__ import annotations

import csv
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path("data/day12_benchmarks")

COMPARISON_FILE = (
    BASE_DIR / "day12_semantic_results.csv"
)

THRESHOLD_FILE = (
    BASE_DIR / "day12_threshold_evaluation.csv"
)

OUTPUT_FILE = Path(
    "reports/day12_matching_accuracy_report.md"
)


# ============================================================
# CSV READERS
# ============================================================

def read_csv(file_path: Path):
    """
    Read a CSV file and return a list of dictionaries.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        return list(
            csv.DictReader(file)
        )


# ============================================================
# FORMAT HELPERS
# ============================================================

def percentage(value: float) -> str:
    """
    Convert decimal metric to percentage text.
    """

    return f"{value * 100:.2f}%"


def score(value: float) -> str:
    """
    Format similarity score.
    """

    return f"{value:.4f}"


# ============================================================
# REPORT GENERATION
# ============================================================

def generate_report():
    """
    Build the Markdown accuracy report.
    """

    comparisons = read_csv(
        COMPARISON_FILE
    )

    thresholds = read_csv(
        THRESHOLD_FILE
    )

    if not comparisons:
        raise ValueError(
            "No comparison results found."
        )

    if not thresholds:
        raise ValueError(
            "No threshold evaluation results found."
        )

    # --------------------------------------------------------
    # Basic counts
    # --------------------------------------------------------

    total_comparisons = len(
        comparisons
    )

    positive_pairs = sum(
        1
        for row in comparisons
        if row["expected_match"].lower() == "true"
    )

    negative_pairs = (
        total_comparisons
        - positive_pairs
    )

    # --------------------------------------------------------
    # Positive and negative score groups
    # --------------------------------------------------------

    positive_scores = [
        float(row["overall_similarity"])
        for row in comparisons
        if row["expected_match"].lower() == "true"
    ]

    negative_scores = [
        float(row["overall_similarity"])
        for row in comparisons
        if row["expected_match"].lower() == "false"
    ]

    avg_positive = (
        sum(positive_scores) / len(positive_scores)
        if positive_scores
        else 0.0
    )

    avg_negative = (
        sum(negative_scores) / len(negative_scores)
        if negative_scores
        else 0.0
    )

    # --------------------------------------------------------
    # Default threshold
    # --------------------------------------------------------

    default_threshold = 0.55

    default_rows = [
        row
        for row in thresholds
        if abs(
            float(row["threshold"])
            - default_threshold
        ) < 0.00001
    ]

    default = (
        default_rows[0]
        if default_rows
        else None
    )

    # --------------------------------------------------------
    # Highest F1 threshold
    # --------------------------------------------------------

    best_f1_row = max(
        thresholds,
        key=lambda row: float(row["f1"])
    )

    # --------------------------------------------------------
    # Highest similarity pair
    # --------------------------------------------------------

    highest_pair = max(
        comparisons,
        key=lambda row:
        float(row["overall_similarity"])
    )

    # --------------------------------------------------------
    # Lowest similarity pair
    # --------------------------------------------------------

    lowest_pair = min(
        comparisons,
        key=lambda row:
        float(row["overall_similarity"])
    )

    # --------------------------------------------------------
    # Build report
    # --------------------------------------------------------

    lines = []

    lines.append(
        "# Day 12 — Semantic Matching Accuracy Report"
    )

    lines.append("")

    lines.append(
        "## 1. Objective"
    )

    lines.append("")

    lines.append(
        "The purpose of this evaluation was to validate the "
        "embedding-based semantic matching engine across "
        "multiple resume and Job Description combinations."
    )

    lines.append(
        "The evaluation also examined how different semantic "
        "similarity thresholds affected classification metrics."
    )

    lines.append("")

    # --------------------------------------------------------
    # Architecture
    # --------------------------------------------------------

    lines.append(
        "## 2. Evaluation Pipeline"
    )

    lines.append("")

    lines.append(
        "```text"
    )

    lines.append(
        "Resume (DOCX/PDF/TXT)"
    )

    lines.append(
        "        ↓"
    )

    lines.append(
        "Resume text extraction"
    )

    lines.append(
        "        ↓"
    )

    lines.append(
        "Structured resume parsing"
    )

    lines.append(
        "        ↓"
    )

    lines.append(
        "Sentence-transformer embeddings"
    )

    lines.append(
        "        ↓"
    )

    lines.append(
        "Section-level semantic similarity"
    )

    lines.append(
        "        ↓"
    )

    lines.append(
        "Weighted overall semantic score"
    )

    lines.append(
        "        ↓"
    )

    lines.append(
        "Threshold-based classification"
    )

    lines.append(
        "```"
    )

    lines.append("")

    # --------------------------------------------------------
    # Dataset
    # --------------------------------------------------------

    lines.append(
        "## 3. Benchmark Dataset"
    )

    lines.append("")

    lines.append(
        f"- Total resume–JD comparisons: "
        f"{total_comparisons}"
    )

    lines.append(
        f"- Intended positive pairs: "
        f"{positive_pairs}"
    )

    lines.append(
        f"- Intended negative pairs: "
        f"{negative_pairs}"
    )

    lines.append(
        "- Resume formats tested: DOCX and PDF"
    )

    lines.append(
        "- Benchmark JD domains: AI/ML, Data Science, "
        "Finance, Legal, and Software Engineering"
    )

    lines.append("")

    # --------------------------------------------------------
    # Similarity distribution
    # --------------------------------------------------------

    lines.append(
        "## 4. Similarity Distribution"
    )

    lines.append("")

    lines.append(
        f"- Average positive-pair similarity: "
        f"{score(avg_positive)}"
    )

    lines.append(
        f"- Minimum positive-pair similarity: "
        f"{score(min(positive_scores))}"
    )

    lines.append(
        f"- Maximum positive-pair similarity: "
        f"{score(max(positive_scores))}"
    )

    lines.append(
        f"- Average negative-pair similarity: "
        f"{score(avg_negative)}"
    )

    lines.append(
        f"- Minimum negative-pair similarity: "
        f"{score(min(negative_scores))}"
    )

    lines.append(
        f"- Maximum negative-pair similarity: "
        f"{score(max(negative_scores))}"
    )

    lines.append("")

    # --------------------------------------------------------
    # Threshold table
    # --------------------------------------------------------

    lines.append(
        "## 5. Threshold Evaluation"
    )

    lines.append("")

    lines.append(
        "| Threshold | TP | TN | FP | FN | Accuracy | Precision | Recall | F1 |"
    )

    lines.append(
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    )

    for row in thresholds:

        lines.append(
            f"| {float(row['threshold']):.2f} "
            f"| {row['true_positive']} "
            f"| {row['true_negative']} "
            f"| {row['false_positive']} "
            f"| {row['false_negative']} "
            f"| {percentage(float(row['accuracy']))} "
            f"| {percentage(float(row['precision']))} "
            f"| {percentage(float(row['recall']))} "
            f"| {percentage(float(row['f1']))} |"
        )

    lines.append("")

    # --------------------------------------------------------
    # Default threshold
    # --------------------------------------------------------

    lines.append(
        "## 6. Default Threshold Result"
    )

    lines.append("")

    if default:

        lines.append(
            f"The configured default threshold was "
            f"**{default_threshold:.2f}**."
        )

        lines.append("")

        lines.append(
            f"- Accuracy: "
            f"**{percentage(float(default['accuracy']))}**"
        )

        lines.append(
            f"- Precision: "
            f"**{percentage(float(default['precision']))}**"
        )

        lines.append(
            f"- Recall: "
            f"**{percentage(float(default['recall']))}**"
        )

        lines.append(
            f"- F1: "
            f"**{percentage(float(default['f1']))}**"
        )

        lines.append(
            f"- True positives: "
            f"{default['true_positive']}"
        )

        lines.append(
            f"- True negatives: "
            f"{default['true_negative']}"
        )

        lines.append(
            f"- False positives: "
            f"{default['false_positive']}"
        )

        lines.append(
            f"- False negatives: "
            f"{default['false_negative']}"
        )

    lines.append("")

    # --------------------------------------------------------
    # Highest F1
    # --------------------------------------------------------

    lines.append(
        "## 7. Threshold With Highest Observed F1"
    )

    lines.append("")

    lines.append(
        f"Within this controlled benchmark, the highest "
        f"observed F1 was **{percentage(float(best_f1_row['f1']))}** "
        f"at threshold **{float(best_f1_row['threshold']):.2f}**."
    )

    lines.append("")

    lines.append(
        "This is a benchmark observation rather than a "
        "universal semantic-matching threshold."
    )

    lines.append("")

    # --------------------------------------------------------
    # Example score extremes
    # --------------------------------------------------------

    lines.append(
        "## 8. Observed Score Extremes"
    )

    lines.append("")

    lines.append(
        f"Highest observed similarity: "
        f"**{score(float(highest_pair['overall_similarity']))}**"
    )

    lines.append("")

    lines.append(
        f"- Resume: `{highest_pair['resume']}`"
    )

    lines.append(
        f"- Job Description: `{highest_pair['jd']}`"
    )

    lines.append(
        f"- Expected match: `{highest_pair['expected_match']}`"
    )

    lines.append("")

    lines.append(
        f"Lowest observed similarity: "
        f"**{score(float(lowest_pair['overall_similarity']))}**"
    )

    lines.append("")

    lines.append(
        f"- Resume: `{lowest_pair['resume']}`"
    )

    lines.append(
        f"- Job Description: `{lowest_pair['jd']}`"
    )

    lines.append(
        f"- Expected match: `{lowest_pair['expected_match']}`"
    )

    lines.append("")

    # --------------------------------------------------------
    # Limitations
    # --------------------------------------------------------

    lines.append(
        "## 9. Limitations"
    )

    lines.append("")

    lines.append(
        "The benchmark uses a controlled set of 60 "
        "resume–JD comparisons with five intended positive "
        "pairs. Therefore, the reported metrics describe "
        "performance on this evaluation dataset only."
    )

    lines.append("")

    lines.append(
        "The benchmark is not a representative sample of "
        "real-world recruitment data and should not be "
        "interpreted as a general ATS accuracy measurement."
    )

    lines.append("")

    lines.append(
        "The current validation also uses the complete "
        "resume text as contextual/project information because "
        "the existing resume parser does not yet expose a "
        "dedicated project field."
    )

    lines.append("")

    # --------------------------------------------------------
    # Conclusion
    # --------------------------------------------------------

    lines.append(
        "## 10. Conclusion"
    )

    lines.append("")

    lines.append(
        "The Day 12 semantic matching pipeline successfully "
        "converted resume and Job Description content into "
        "sentence embeddings, calculated section-level "
        "semantic similarities, generated weighted overall "
        "similarity scores, and evaluated threshold-based "
        "classification."
    )

    lines.append("")

    lines.append(
        "The threshold experiment demonstrated that changing "
        "the similarity cutoff changes the balance between "
        "precision and recall. This provides measurable "
        "evidence for threshold selection rather than relying "
        "on an arbitrary cutoff."
    )

    lines.append("")

    lines.append(
        "## 11. Generated Evidence Files"
    )

    lines.append("")

    lines.append(
        f"- `{COMPARISON_FILE}`"
    )

    lines.append(
        f"- `{THRESHOLD_FILE}`"
    )

    lines.append(
        f"- `{OUTPUT_FILE}`"
    )

    lines.append("")

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print("=" * 80)
    print(
        "DAY 12 - MATCHING ACCURACY REPORT GENERATOR"
    )
    print("=" * 80)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:

        report = generate_report()

        OUTPUT_FILE.write_text(
            report,
            encoding="utf-8",
        )

    except Exception as exc:

        print(
            f"\nERROR: {exc}"
        )

        return

    print(
        f"\nReport generated successfully:"
    )

    print(
        f"  {OUTPUT_FILE}"
    )

    print(
        "\nDAY 12 REPORT GENERATION COMPLETE"
    )


if __name__ == "__main__":
    main()