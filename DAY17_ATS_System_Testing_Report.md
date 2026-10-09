# Zecpath AI System — Day 17 ATS System Testing

**Submitted By:** Sanjay Manoj K
**Organization:** Zecser Technology
**Project:** AI-Based Applicant Tracking System

## 1. Executive Summary

Day 17 validated the existing Day 13 -> Day 14 ATS pipeline against **5 job descriptions x 12 resumes = 60 controlled test cases**. The final run observed all 60 cases. **59 cases produced valid ATS predictions and 1 case failed during scoring.**

On the 59 valid predictions:
- Accuracy: **93.22%**
- Precision: **100.00%**
- Recall: **20.00%**
- F1: **33.33%**
- Prediction coverage: **98.33%**
- Execution error rate: **1.67%**

The single failed case was retained as `EXECUTION_ERROR` and was not assigned an artificial ATS decision.

## 2. Test Coverage

- **Tech roles:** AI/ML Engineer, Data Scientist, Software Engineer
- **Non-tech roles:** Finance Analyst, Legal Intern
- **Fresher / entry-level:** the corpus includes an explicitly titled Entry-Level Data Scientist resume and student/internship-oriented profiles.
- **Experienced profiles:** the corpus includes multi-year professional histories, including Sophia Martinez (5.67 years in verified Day 7 evidence) and Sam Saviour (6.25 years in verified Day 14 evidence).

The current Day 17 result schema does not include an explicit `profile_level` field, so numeric fresher-vs-senior subgroup metrics have not been invented. Adding that controlled field is included in the backlog.

## 3. Overall Metrics

| Metric | Result |
|---|---:|
| Total test cases | 60 |
| Valid ATS predictions | 59 |
| Execution errors | 1 |
| True positives | 1 |
| True negatives | 54 |
| False positives | 0 |
| False negatives | 4 |
| Accuracy | 93.22% |
| Precision | 100.00% |
| Recall | 20.00% |
| F1 | 33.33% |
| Prediction coverage | 98.33% |
| Execution error rate | 1.67% |

## 4. Role-wise Metrics

| Role | Cases | Valid | Errors | Accuracy | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|
| AI/ML Engineer | 12 | 12 | 0 | 100.00% | 100.00% | 100.00% |
| Data Scientist | 12 | 12 | 0 | 91.67% | 0.00% | 0.00% |
| Finance Analyst | 12 | 11 | 1 | 90.91% | 0.00% | 0.00% |
| Legal Intern | 12 | 12 | 0 | 91.67% | 0.00% | 0.00% |
| Software Engineer | 12 | 12 | 0 | 91.67% | 0.00% | 0.00% |

## 5. Mismatch Cases

| Candidate | Role | ATS | Manual | AI | Outcome |
|---|---|---:|---|---|---|
| Entry-Level Data Scientist | Data Scientist | 29.35% | Suitable | REJECT | False negative |
| Sanskar Sankar | Finance Analyst | 29.50% | Suitable | REJECT | False negative |
| Albin Abhraham | Legal Intern | 15.64% | Suitable | REJECT | False negative |
| Vyshnavi K | Software Engineer | 39.07% | Suitable | REJECT | False negative |

## 6. Reliability Failure

**Finance Analyst x legal-resume.docx — Albin Abhraham**

Error: `Scores must be between 0 and 1.`

Day 17 records this as `EXECUTION_ERROR`, with no ATS score and no artificial classification.

## 7. Improvement Backlog

| Priority | Issue | Evidence | Improvement |
|---|---|---|---|
| High | Semantic scoring contract mismatch | Albin case failed with score-range error | Add an explicit Day 12 -> Day 13 score-domain adapter while preserving `None` for missing values. |
| High | Low recall / false negatives | Recall 20.00%; 4 false negatives | Review role-specific weights and thresholds using a larger labeled set. |
| High | Weak non-tech domain coverage | Finance and Legal show low positive capture | Expand finance/legal requirement and skill extraction. |
| Medium | Profile-tier instrumentation | No explicit `profile_level` in Day 17 schema | Add controlled fresher / mid / senior labels and subgroup metrics. |
| Medium | Semantic model runtime | Model loaded repeatedly in batch execution | Reuse one model instance per batch. |
| Low | Benchmark size | Only 5 positive manual labels | Expand the labeled benchmark across more roles, seniority levels and formats. |

## 8. Final Status

**DAY 17 — TEST EXECUTION COMPLETE, METRICS VERIFIED, MISMATCHES ANALYZED, RELIABILITY FAILURE RECORDED, AND IMPROVEMENT BACKLOG DOCUMENTED.**
