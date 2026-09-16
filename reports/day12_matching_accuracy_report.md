# Day 12 — Semantic Matching Accuracy Report

## 1. Objective

The purpose of this evaluation was to validate the embedding-based semantic matching engine across multiple resume and Job Description combinations.
The evaluation also examined how different semantic similarity thresholds affected classification metrics.

## 2. Evaluation Pipeline

```text
Resume (DOCX/PDF/TXT)
        ↓
Resume text extraction
        ↓
Structured resume parsing
        ↓
Sentence-transformer embeddings
        ↓
Section-level semantic similarity
        ↓
Weighted overall semantic score
        ↓
Threshold-based classification
```

## 3. Benchmark Dataset

- Total resume–JD comparisons: 60
- Intended positive pairs: 5
- Intended negative pairs: 55
- Resume formats tested: DOCX and PDF
- Benchmark JD domains: AI/ML, Data Science, Finance, Legal, and Software Engineering

## 4. Similarity Distribution

- Average positive-pair similarity: 0.5449
- Minimum positive-pair similarity: 0.4116
- Maximum positive-pair similarity: 0.6633
- Average negative-pair similarity: 0.1955
- Minimum negative-pair similarity: -0.0331
- Maximum negative-pair similarity: 0.5564

## 5. Threshold Evaluation

| Threshold | TP | TN | FP | FN | Accuracy | Precision | Recall | F1 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.40 | 5 | 52 | 3 | 0 | 95.00% | 62.50% | 100.00% | 76.92% |
| 0.45 | 4 | 53 | 2 | 1 | 95.00% | 66.67% | 80.00% | 72.73% |
| 0.50 | 3 | 54 | 1 | 2 | 95.00% | 75.00% | 60.00% | 66.67% |
| 0.55 | 3 | 54 | 1 | 2 | 95.00% | 75.00% | 60.00% | 66.67% |
| 0.60 | 2 | 55 | 0 | 3 | 95.00% | 100.00% | 40.00% | 57.14% |
| 0.65 | 1 | 55 | 0 | 4 | 93.33% | 100.00% | 20.00% | 33.33% |
| 0.70 | 0 | 55 | 0 | 5 | 91.67% | 0.00% | 0.00% | 0.00% |

## 6. Default Threshold Result

The configured default threshold was **0.55**.

- Accuracy: **95.00%**
- Precision: **75.00%**
- Recall: **60.00%**
- F1: **66.67%**
- True positives: 3
- True negatives: 54
- False positives: 1
- False negatives: 2

## 7. Threshold With Highest Observed F1

Within this controlled benchmark, the highest observed F1 was **76.92%** at threshold **0.40**.

This is a benchmark observation rather than a universal semantic-matching threshold.

## 8. Observed Score Extremes

Highest observed similarity: **0.6633**

- Resume: `ai-developer-resume.docx`
- Job Description: `ai_ml_engineer.txt`
- Expected match: `True`

Lowest observed similarity: **-0.0331**

- Resume: `asst-report-writter-resume.docx`
- Job Description: `software_engineer.txt`
- Expected match: `False`

## 9. Limitations

The benchmark uses a controlled set of 60 resume–JD comparisons with five intended positive pairs. Therefore, the reported metrics describe performance on this evaluation dataset only.

The benchmark is not a representative sample of real-world recruitment data and should not be interpreted as a general ATS accuracy measurement.

The current validation also uses the complete resume text as contextual/project information because the existing resume parser does not yet expose a dedicated project field.

## 10. Conclusion

The Day 12 semantic matching pipeline successfully converted resume and Job Description content into sentence embeddings, calculated section-level semantic similarities, generated weighted overall similarity scores, and evaluated threshold-based classification.

The threshold experiment demonstrated that changing the similarity cutoff changes the balance between precision and recall. This provides measurable evidence for threshold selection rather than relying on an arbitrary cutoff.

## 11. Generated Evidence Files

- `data\day12_benchmarks\day12_semantic_results.csv`
- `data\day12_benchmarks\day12_threshold_evaluation.csv`
- `reports\day12_matching_accuracy_report.md`
