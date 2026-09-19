"""
Day 14 - End-to-End Candidate Ranking Pipeline

Connects:
    Day 9  -> Skill Extraction
    Day 10 -> Experience Relevance
    Day 11 -> Education Alignment
    Day 12 -> Semantic Matching
    Day 13 -> ATS Scoring
    Day 14 -> Ranking + Shortlisting

Usage:

    python -m scoring.day14_end_to_end <jd_path> <resume1> <resume2> ...

Example:

    python -m scoring.day14_end_to_end data\\python_developer_jd.pdf data\\resume1.pdf data\\resume2.pdf
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from scoring import day13_candidate_score as day13
from scoring.resume_ranking_engine import (
    CandidateRankingEngine,
    RankingThresholds,
)


def score_candidate(
    resume_path: Path,
    jd_path: Path,
) -> Dict[str, Any]:
    """
    Execute the actual Day 13 scoring pipeline for one candidate.

    Returns:
        Day 13 ATS result enriched with basic candidate information.
    """

    print("\n" + "=" * 80)
    print("PROCESSING CANDIDATE")
    print("=" * 80)

    print(f"Resume: {resume_path}")

    # ------------------------------------------------------------------
    # Resume extraction
    # ------------------------------------------------------------------

    resume_text = day13.extract_resume_text(
        str(resume_path)
    )

    if not resume_text.strip():
        raise ValueError(
            f"Resume text is empty: {resume_path}"
        )

    # ------------------------------------------------------------------
    # Resume parsing
    # ------------------------------------------------------------------

    candidate = day13.parse_resume_text(
        resume_text
    )

    candidate_name = (
        candidate.get("name")
        or resume_path.stem
        or "Unknown Candidate"
    )

    print(f"Candidate: {candidate_name}")

    # ------------------------------------------------------------------
    # Job description parsing
    # ------------------------------------------------------------------

    jd_text = day13.read_job_description(
        str(jd_path)
    )

    job = day13.parse_job_description(
        jd_text
    )

    try:
        job_requirement = day13.JobRequirement(
            **job
        )
    except Exception as exc:
        raise ValueError(
            "JobRequirement validation failed: "
            f"{exc}"
        ) from exc

    print(
        f"Role: {job_requirement.role}"
    )

    # ------------------------------------------------------------------
    # DAY 9 - SKILL EXTRACTION
    # ------------------------------------------------------------------

    skill_engine = (
        day13.SkillExtractionEngine()
    )

    skill_result = (
        skill_engine.extract_skills(
            resume_text,
            source_section="resume",
        )
    )

    candidate_skills: List[str] = []

    for skill in skill_result.get(
        "skills",
        [],
    ):
        canonical = skill.get(
            "canonical",
            "",
        )

        if canonical:
            candidate_skills.append(
                canonical
            )

    candidate_skills = list(
        dict.fromkeys(
            candidate_skills
        )
    )

    required_skills = list(
        job_requirement.required_skills
    )

    skill_match = (
        day13.calculate_skill_match(
            candidate_skills,
            required_skills,
        )
    )

    # ------------------------------------------------------------------
    # DAY 10 - EXPERIENCE
    # ------------------------------------------------------------------

    work_experience_text = (
        day13.extract_work_experience_text(
            resume_text
        )
    )

    experience_parser = (
        day13.ExperienceParser()
    )

    experience_scorer = (
        day13.ExperienceRelevanceScorer(
            skill_engine=skill_engine
        )
    )

    (
        experience_relevance,
        experience_result,
    ) = day13.calculate_experience_relevance(
        experience_parser,
        experience_scorer,
        work_experience_text,
        job_requirement,
    )

    # ------------------------------------------------------------------
    # DAY 11 - EDUCATION
    # ------------------------------------------------------------------

    education_parser = (
        day13.EducationCertificationParser()
    )

    academic_profile = (
        education_parser.parse(
            resume_text
        )
    )

    education_alignment = (
        day13.calculate_education_alignment(
            academic_profile,
            job_requirement.education,
        )
    )

    # ------------------------------------------------------------------
    # DAY 12 - SEMANTIC MATCHING
    # ------------------------------------------------------------------

    semantic_engine = (
        day13.SemanticMatchingEngine()
    )

    semantic_experience_text = (
        work_experience_text
        or candidate.get(
            "experience",
            "",
        )
    )

    semantic_result = (
        semantic_engine.match(
            " ".join(candidate_skills),
            " ".join(required_skills),
            semantic_experience_text,
            job_requirement.experience,
            resume_text,
            "\n".join(
                job_requirement.responsibilities
            ),
        )
    )

    semantic_similarity = (
        semantic_result.overall_similarity
    )

    # ------------------------------------------------------------------
    # DAY 13 - ATS SCORING
    # ------------------------------------------------------------------

    ats_engine = (
        day13.ATSScoringEngine()
    )

    signals = {
        "skill_match": skill_match,
        "experience_relevance": experience_relevance,
        "education_alignment": education_alignment,
        "semantic_similarity": semantic_similarity,
    }

    ats_result = (
        ats_engine.generate_candidate_score(
            candidate_id=(
                candidate_name
                or "candidate"
            ),
            role=job_requirement.role,
            signals=signals,
        )
    )

    # ------------------------------------------------------------------
    # Build Day 14 candidate record
    # ------------------------------------------------------------------

    candidate_result = {
        **ats_result,

        "candidate_name": candidate_name,

        "resume_path": str(
            resume_path
        ),

        "job_description_path": str(
            jd_path
        ),

        "candidate_skills": candidate_skills,

        "required_skills": required_skills,

        "skill_match": skill_match,

        "experience_relevance": (
            experience_relevance
        ),

        "education_alignment": (
            education_alignment
        ),

        "semantic_similarity": (
            semantic_similarity
        ),

        "experience_years": (
            experience_result.get(
                "total_experience_years",
                0.0,
            )
        ),

        "experience_records": (
            experience_result.get(
                "experiences",
                [],
            )
        ),

        "semantic_matched": (
            semantic_result.matched
        ),
    }

    print(
        f"Day 13 ATS Score: "
        f"{ats_result['final_score'] * 100:.2f}%"
    )

    return candidate_result


def print_ranked_candidates(
    ranked_candidates: List[Dict[str, Any]],
) -> None:
    """
    Print recruiter-friendly ranked candidates.
    """

    print("\n" + "=" * 90)
    print("DAY 14 - REAL CANDIDATE RANKING")
    print("=" * 90)

    print(
        f"{'Rank':<8}"
        f"{'Candidate':<28}"
        f"{'ATS Score':<15}"
        f"{'Status':<12}"
        f"{'Role':<25}"
    )

    print("-" * 90)

    for candidate in ranked_candidates:

        rank = candidate.get(
            "rank",
            "-",
        )

        name = candidate.get(
            "candidate_name",
            candidate.get(
                "candidate_id",
                "Unknown",
            ),
        )

        score = candidate.get(
            "score_percentage",
            candidate.get(
                "final_score",
                0.0,
            ) * 100,
        )

        status = candidate.get(
            "status",
            "UNKNOWN",
        )

        role = candidate.get(
            "role",
            "N/A",
        )

        print(
            f"{rank:<8}"
            f"{str(name):<28}"
            f"{float(score):>7.2f}%       "
            f"{status:<12}"
            f"{str(role):<25}"
        )


def print_zone(
    title: str,
    candidates: List[Dict[str, Any]],
) -> None:
    """
    Print candidates belonging to a decision zone.
    """

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    if not candidates:
        print("No candidates.")
        return

    for candidate in candidates:

        print(
            f"Rank #{candidate.get('rank', '-')}"
            f" | {candidate.get('candidate_name', 'Unknown')}"
            f" | {candidate.get('score_percentage', 0):.2f}%"
        )


def print_top_candidates(
    candidates: List[Dict[str, Any]],
) -> None:
    """
    Print Top-N candidates.
    """

    print("\n" + "=" * 80)
    print("TOP CANDIDATES")
    print("=" * 80)

    if not candidates:
        print("No candidates.")
        return

    for candidate in candidates:

        print(
            f"#{candidate.get('rank', '-')}"
            f" {candidate.get('candidate_name', 'Unknown')}"
            f" - "
            f"{candidate.get('score_percentage', 0):.2f}%"
            f" - "
            f"{candidate.get('status', 'UNKNOWN')}"
        )


def save_output(
    result: Dict[str, Any],
    output_path: str = (
        "outputs/day14_real_ranked_candidates.json"
    ),
) -> Path:
    """
    Save complete Day 14 results as JSON.
    """

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False,
            default=str,
        )

    return path


def main() -> None:
    """
    Execute real Day 13 -> Day 14 pipeline.
    """

    if len(sys.argv) < 3:

        print(
            "\nUsage:"
        )

        print(
            "python -m scoring.day14_end_to_end "
            "<jd_path> <resume1> <resume2> ..."
        )

        print(
            "\nExample:"
        )

        print(
            "python -m scoring.day14_end_to_end "
            "data\\job_description.pdf "
            "data\\resume1.pdf "
            "data\\resume2.pdf"
        )

        sys.exit(1)

    jd_path = Path(
        sys.argv[1]
    )

    resume_paths = [
        Path(path)
        for path in sys.argv[2:]
    ]

    if not jd_path.exists():

        print(
            f"\nERROR: Job description not found:"
            f" {jd_path}"
        )

        sys.exit(1)

    missing_resumes = [
        path
        for path in resume_paths
        if not path.exists()
    ]

    if missing_resumes:

        print(
            "\nERROR: The following resume files "
            "were not found:"
        )

        for path in missing_resumes:
            print(
                f"  - {path}"
            )

        sys.exit(1)

    print("\n" + "=" * 90)
    print("ZECPATH AI SYSTEM - DAY 13 → DAY 14")
    print("=" * 90)

    print(
        f"\nJob Description:"
        f" {jd_path}"
    )

    print(
        f"Resumes to process:"
        f" {len(resume_paths)}"
    )

    # ------------------------------------------------------------------
    # Step 1 - Generate real Day 13 scores
    # ------------------------------------------------------------------

    candidate_results: List[Dict[str, Any]] = []

    for resume_path in resume_paths:

        try:

            result = score_candidate(
                resume_path,
                jd_path,
            )

            candidate_results.append(
                result
            )

        except Exception as exc:

            print("\nERROR processing:")
            print(
                f"  Resume: {resume_path}"
            )
            print(
                f"  Reason: {exc}"
            )

    if not candidate_results:

        print(
            "\nERROR: No candidates could be processed."
        )

        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 2 - Day 14 ranking
    # ------------------------------------------------------------------

    thresholds = RankingThresholds(
        shortlist=0.70,
        review=0.50,
    )

    ranking_engine = CandidateRankingEngine(
        thresholds=thresholds
    )

    day14_result = (
        ranking_engine.process_candidates(
            candidates=candidate_results,
            score_key="final_score",
            top_n=5,
        )
    )

    # ------------------------------------------------------------------
    # Step 3 - Recruiter output
    # ------------------------------------------------------------------

    print_ranked_candidates(
        day14_result[
            "ranked_candidates"
        ]
    )

    print_zone(
        "SHORTLISTED CANDIDATES",
        day14_result[
            "shortlisted_candidates"
        ],
    )

    print_zone(
        "REVIEW QUEUE",
        day14_result[
            "review_candidates"
        ],
    )

    print_zone(
        "AUTO-REJECTION QUEUE",
        day14_result[
            "rejected_candidates"
        ],
    )

    print_top_candidates(
        day14_result[
            "top_candidates"
        ]
    )

    # ------------------------------------------------------------------
    # Step 4 - Summary
    # ------------------------------------------------------------------

    summary = day14_result[
        "recruiter_summary"
    ]

    print("\n" + "=" * 80)
    print("RECRUITER SUMMARY")
    print("=" * 80)

    print(
        f"Total candidates : "
        f"{summary['total_candidates']}"
    )

    print(
        f"Shortlisted      : "
        f"{summary['shortlisted_count']}"
    )

    print(
        f"Review required  : "
        f"{summary['review_count']}"
    )

    print(
        f"Auto-rejected    : "
        f"{summary['rejected_count']}"
    )

    top_candidate = summary.get(
        "top_candidate"
    )

    if top_candidate:

        print(
            f"Top-ranked       : "
            f"{top_candidate['candidate_name']} "
            f"("
            f"{top_candidate['score_percentage']:.2f}%"
            f")"
        )

    print(
        f"Shortlist limit  : "
        f"{thresholds.shortlist * 100:.0f}%"
    )

    print(
        f"Review limit     : "
        f"{thresholds.review * 100:.0f}%"
    )

    # ------------------------------------------------------------------
    # Step 5 - Save output
    # ------------------------------------------------------------------

    output = {
        "job_description": str(
            jd_path
        ),
        "thresholds": {
            "shortlist": (
                thresholds.shortlist
            ),
            "review": (
                thresholds.review
            ),
        },
        **day14_result,
    }

    output_path = save_output(
        output
    )

    print("\n" + "=" * 80)
    print("DAY 14 END-TO-END OUTPUT")
    print("=" * 80)

    print(
        f"JSON output: {output_path}"
    )

    print("\n" + "=" * 80)
    print(
        "DAY 14 END-TO-END PIPELINE COMPLETE"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()