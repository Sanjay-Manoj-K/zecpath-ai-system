
"""
Day 18 - ATS Performance Baseline

Purpose:
- Measure current resume text extraction time.
- Measure semantic model initialization time.
- Measure semantic matching time.
- Measure full Day 13 candidate scoring time.
- Capture Python memory allocation with tracemalloc.

Run from the Zecpath project root:

    python day18/day18_baseline_benchmark.py

The script intentionally does NOT modify ATS logic.
"""

from __future__ import annotations

import gc
import sys
import time
import tracemalloc
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RESUME_FILES = [
    PROJECT_ROOT / "data" / "resumes" / "ai-developer-resume.docx",
    PROJECT_ROOT / "data" / "resumes" / "data-scientist-resume.pdf",
    PROJECT_ROOT / "data" / "resumes" / "finance-resume.docx",
]

JD_FILE = PROJECT_ROOT / "data" / "day12_benchmarks" / "ai_ml_engineer.txt"


def timed_call(label: str, func):
    start = time.perf_counter()
    result = func()
    elapsed = time.perf_counter() - start
    print(f"{label:<42} {elapsed:>10.4f} s")
    return result, elapsed


def memory_call(label: str, func):
    gc.collect()
    tracemalloc.start()

    result = func()

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(
        f"{label:<42} current={current / 1024 / 1024:>7.2f} MB"
        f" | peak={peak / 1024 / 1024:>7.2f} MB"
    )
    return result, current, peak


def main() -> int:
    print("=" * 80)
    print("DAY 18 - ATS PERFORMANCE BASELINE")
    print("=" * 80)
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Python       : {sys.version.split()[0]}")
    print()

    if not JD_FILE.exists():
        print(f"ERROR: JD file not found: {JD_FILE}")
        return 1

    missing_resumes = [p for p in RESUME_FILES if not p.exists()]
    if missing_resumes:
        print("ERROR: Resume file(s) not found:")
        for path in missing_resumes:
            print(f"  - {path}")
        return 1

    # ------------------------------------------------------------------
    # 1. Resume text extraction baseline
    # ------------------------------------------------------------------
    from parsers.resume_text_extractor import extract_resume_text

    print("1. TEXT EXTRACTION")
    extraction_times = []

    for resume_path in RESUME_FILES:
        _, elapsed = timed_call(
            f"{resume_path.name}",
            lambda p=resume_path: extract_resume_text(str(p)),
        )
        extraction_times.append(elapsed)

    print(
        f"{'Average extraction time':<42}"
        f"{sum(extraction_times) / len(extraction_times):>10.4f} s"
    )
    print()

    # ------------------------------------------------------------------
    # 2. Semantic engine initialization baseline
    # ------------------------------------------------------------------
    print("2. SEMANTIC MODEL INITIALIZATION")

    from scoring.semantic_matching import SemanticMatchingEngine

    semantic_engine, model_init_time = timed_call(
        "SemanticMatchingEngine()",
        lambda: SemanticMatchingEngine(),
    )
    print()

    # ------------------------------------------------------------------
    # 3. Semantic matching baseline
    # ------------------------------------------------------------------
    print("3. SEMANTIC MATCHING")

    resume_text = extract_resume_text(str(RESUME_FILES[0]))
    jd_text = JD_FILE.read_text(encoding="utf-8", errors="replace")

    semantic_time_samples = []

    # Use the existing public interface used by Day 13.
    for i in range(3):
        _, elapsed = timed_call(
            f"Semantic match run {i + 1}",
            lambda: semantic_engine.match(
                "Python Machine Learning Artificial Intelligence",
                "Python Machine Learning",
                "",
                "",
                resume_text,
                jd_text,
            ),
        )
        semantic_time_samples.append(elapsed)

    print(
        f"{'Average semantic match time':<42}"
        f"{sum(semantic_time_samples) / len(semantic_time_samples):>10.4f} s"
    )
    print()

    # ------------------------------------------------------------------
    # 4. Memory baseline
    # ------------------------------------------------------------------
    print("4. MEMORY BASELINE")

    _, current, peak = memory_call(
        "Semantic engine + one matching run",
        lambda: SemanticMatchingEngine().match(
            "Python Machine Learning Artificial Intelligence",
            "Python Machine Learning",
            "",
            "",
            resume_text,
            jd_text,
        ),
    )

    print()
    print("Memory figures above are Python allocation measurements from")
    print("tracemalloc; they are not the complete operating-system RSS.")
    print()

    # ------------------------------------------------------------------
    # 5. Full Day 14 end-to-end baseline
    # ------------------------------------------------------------------
    print("5. FULL ATS PIPELINE")

    import os
    import subprocess

    full_times = []

    for resume_path in RESUME_FILES:
        command = [
            sys.executable,
            "-X",
            "utf8",
            "-m",
            "scoring.day14_end_to_end",
            str(JD_FILE),
            str(resume_path),
        ]

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        start = time.perf_counter()
        completed = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            env=env,
            capture_output=True,
            text=True,
        )
        elapsed = time.perf_counter() - start
        full_times.append(elapsed)

        status = "PASS" if completed.returncode == 0 else "ERROR"
        print(
            f"{resume_path.name:<32} "
            f"{elapsed:>10.4f} s  {status}"
        )

        if completed.returncode != 0:
            print(
                f"  Error: {completed.stderr.strip()[-300:]}"
            )

    if full_times:
        print(
            f"{'Average full ATS pipeline time':<42}"
            f"{sum(full_times) / len(full_times):>10.4f} s"
        )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print()
    print("=" * 80)
    print("BASELINE SUMMARY")
    print("=" * 80)
    print(f"Model initialization time : {model_init_time:.4f} s")
    print(
        f"Average extraction time   : "
        f"{sum(extraction_times) / len(extraction_times):.4f} s"
    )
    print(
        f"Average semantic time     : "
        f"{sum(semantic_time_samples) / len(semantic_time_samples):.4f} s"
    )
    if full_times:
        print(
            f"Average full scoring time : "
            f"{sum(full_times) / len(full_times):.4f} s"
        )
    print(f"Peak traced allocation    : {peak / 1024 / 1024:.2f} MB")
    print("=" * 80)
    print()
    print("BASELINE ONLY - NO ATS LOGIC WAS CHANGED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
