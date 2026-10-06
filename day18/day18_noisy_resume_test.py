"""
Day 18 - Noisy Resume & Stability Regression Test

Purpose:
    Validate that the Day 18 resume-quality layer can normalize noisy
    extracted resume text without changing the core ATS scoring logic.

What this test does:
    1. Loads the existing clean benchmark resume.
    2. Extracts its text using the existing extractor.
    3. Creates a deliberately noisy TXT version by adding:
       - non-breaking spaces
       - zero-width characters
       - Unicode dash variants
       - duplicated lines
    4. Runs Day 18 preprocessing/entity detection.
    5. Runs the clean and noisy resumes through the same Day 14 scoring
       components and reports score/name differences.

This is a regression test only. It does not modify ATS formulas or thresholds.
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scoring import day13_candidate_score as day13
from scoring.day18_resume_quality import prepare_resume
from scoring.day14_end_to_end import score_candidate


JD_PATH = PROJECT_ROOT / "data" / "day12_benchmarks" / "ai_ml_engineer.txt"
CLEAN_RESUME = PROJECT_ROOT / "data" / "resumes" / "ai-developer-resume.docx"


def build_noisy_text(clean_text: str) -> str:
    """Create deterministic formatting noise without changing the content."""
    lines = clean_text.splitlines()
    noisy_lines: list[str] = []

    for index, line in enumerate(lines):
        noisy = line

        # Non-breaking spaces on selected lines.
        if index % 3 == 0:
            noisy = noisy.replace(" ", "\u00A0")

        # Zero-width characters at selected positions.
        if index % 5 == 0 and noisy:
            noisy = "\u200B" + noisy + "\u200D"

        # Unicode dash noise.
        noisy = noisy.replace("-", "–")
        noisy = noisy.replace("—", "−")

        noisy_lines.append(noisy)

        # Duplicate a few lines to simulate extraction duplication.
        if index in {2, 10, 20} and noisy.strip():
            noisy_lines.append(noisy)

    return "\n".join(noisy_lines)


def to_float_score(value):
    if value is None:
        return None
    return float(value)


def main() -> int:
    print("=" * 88)
    print("DAY 18 - NOISY RESUME & STABILITY REGRESSION TEST")
    print("=" * 88)
    print(f"Clean resume : {CLEAN_RESUME}")
    print(f"JD           : {JD_PATH}")

    if not CLEAN_RESUME.exists():
        print("ERROR: Clean benchmark resume was not found.")
        return 1

    if not JD_PATH.exists():
        print("ERROR: Job description was not found.")
        return 1

    # ------------------------------------------------------------------
    # 1. Extract clean text with the existing extractor.
    # ------------------------------------------------------------------
    print("\n1. Extracting clean resume text...")
    clean_text = day13.extract_resume_text(str(CLEAN_RESUME))

    if not clean_text.strip():
        print("ERROR: Clean resume extraction returned empty text.")
        return 1

    # ------------------------------------------------------------------
    # 2. Create deliberately noisy resume text in a temporary TXT file.
    # ------------------------------------------------------------------
    noisy_text = build_noisy_text(clean_text)

    temp_dir = Path(tempfile.mkdtemp(prefix="day18_noisy_resume_"))
    noisy_resume = temp_dir / "ai-developer-resume-noisy.txt"
    noisy_resume.write_text(noisy_text, encoding="utf-8")

    print(f"Temporary noisy resume: {noisy_resume}")

    # ------------------------------------------------------------------
    # 3. Validate the Day 18 preprocessing/entity layer directly.
    # ------------------------------------------------------------------
    print("\n2. Testing Day 18 normalization and entity detection...")
    normalized_text, entities = prepare_resume(noisy_text)

    checks = {
        "text_not_empty": bool(normalized_text.strip()),
        "nbsp_removed": "\u00A0" not in normalized_text,
        "zero_width_removed": not re.search(r"[\u200B\u200C\u200D\uFEFF]", normalized_text),
        "candidate_name_detected": bool(entities.candidate_name),
        "email_detected": bool(entities.email),
        "urls_is_list": isinstance(entities.urls, list),
    }

    for name, passed in checks.items():
        print(f"{name:28} {'PASS' if passed else 'FAIL'}")

    if not all(checks.values()):
        print("\nERROR: Day 18 preprocessing/entity regression failed.")
        return 1

    print(f"Detected name  : {entities.candidate_name}")
    print(f"Detected email : {entities.email}")
    print(f"Detected URLs  : {entities.urls}")

    # ------------------------------------------------------------------
    # 4. Reuse the same engines/components for both candidates.
    # ------------------------------------------------------------------
    print("\n3. Initializing reusable ATS components...")
    job_text = day13.read_job_description(str(JD_PATH))
    job_data = day13.parse_job_description(job_text)
    job_requirement = day13.JobRequirement(**job_data)

    skill_engine = day13.SkillExtractionEngine()
    semantic_engine = day13.SemanticMatchingEngine()
    experience_parser = day13.ExperienceParser()
    experience_scorer = day13.ExperienceRelevanceScorer(skill_engine=skill_engine)
    education_parser = day13.EducationCertificationParser()
    ats_engine = day13.ATSScoringEngine()

    # ------------------------------------------------------------------
    # 5. Score clean and noisy versions through the real Day 14 pipeline.
    # ------------------------------------------------------------------
    print("\n4. Running clean resume through Day 14 scoring...")
    clean_result = score_candidate(
        CLEAN_RESUME,
        JD_PATH,
        job_requirement=job_requirement,
        skill_engine=skill_engine,
        semantic_engine=semantic_engine,
        experience_parser=experience_parser,
        experience_scorer=experience_scorer,
        education_parser=education_parser,
        ats_engine=ats_engine,
    )

    print("\n5. Running noisy resume through Day 14 scoring...")
    noisy_result = score_candidate(
        noisy_resume,
        JD_PATH,
        job_requirement=job_requirement,
        skill_engine=skill_engine,
        semantic_engine=semantic_engine,
        experience_parser=experience_parser,
        experience_scorer=experience_scorer,
        education_parser=education_parser,
        ats_engine=ats_engine,
    )

    clean_name = clean_result.get("candidate_name") or clean_result.get("candidate", {}).get("name")
    noisy_name = noisy_result.get("candidate_name") or noisy_result.get("candidate", {}).get("name")

    clean_score = to_float_score(clean_result.get("final_score"))
    noisy_score = to_float_score(noisy_result.get("final_score"))

    print("\n" + "=" * 88)
    print("REGRESSION RESULT")
    print("=" * 88)
    print(f"Clean candidate name : {clean_name}")
    print(f"Noisy candidate name : {noisy_name}")
    print(f"Clean ATS score      : {clean_score:.4f}" if clean_score is not None else "Clean ATS score      : None")
    print(f"Noisy ATS score      : {noisy_score:.4f}" if noisy_score is not None else "Noisy ATS score      : None")

    if clean_score is not None and noisy_score is not None:
        score_delta = abs(clean_score - noisy_score)
        print(f"Absolute score diff  : {score_delta:.4f}")

    name_match = clean_name == noisy_name and noisy_name is not None
    score_available = clean_score is not None and noisy_score is not None

    print(f"Candidate identity   : {'PASS' if name_match else 'FAIL'}")
    print(f"Pipeline execution   : {'PASS' if score_available else 'FAIL'}")

    passed = name_match and score_available

    print("\n" + "=" * 88)
    print("DAY 18 NOISY RESUME TEST " + ("PASSED" if passed else "FAILED"))
    print("=" * 88)

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
