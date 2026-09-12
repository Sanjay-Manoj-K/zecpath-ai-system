from pathlib import Path
import sys

from parsers.resume_text_extractor import extract_resume_text
from parsers.resume_section_classifier import ResumeSectionClassifier
from parsers.experience_parser import ExperienceParser


# ================================================================
# INPUT
# ================================================================

if len(sys.argv) < 2:
    print(
        "Usage:"
    )
    print(
        "python tests/debug_experience_detection.py "
        "<resume_file>"
    )
    sys.exit(1)


resume_path = Path(
    sys.argv[1]
)


# ================================================================
# CHECK FILE
# ================================================================

if not resume_path.exists():
    print(
        f"ERROR: File not found: {resume_path}"
    )
    sys.exit(1)


# ================================================================
# TEXT EXTRACTION
# ================================================================

print(
    "\n"
    + "=" * 80
)

print(
    "===== EXPERIENCE DETECTION DIAGNOSTIC ====="
)

print(
    "=" * 80
)

print(
    f"\nResume: {resume_path}"
)

resume_text = extract_resume_text(
    resume_path
)

print(
    f"\nExtracted characters: "
    f"{len(resume_text)}"
)

print(
    f"Extracted lines: "
    f"{len(resume_text.splitlines())}"
)


# ================================================================
# RAW EXTRACTED TEXT
# ================================================================

print(
    "\n"
    + "=" * 80
)

print(
    "===== EXTRACTED TEXT ====="
)

print(
    "=" * 80
)

print(
    resume_text
)


# ================================================================
# DAY 8 SECTION CLASSIFICATION
# ================================================================

classifier = ResumeSectionClassifier()

try:
    sections = classifier.segment(
        resume_text
    )
except Exception as error:
    print(
        "\nERROR during section classification:"
    )
    print(
        f"{type(error).__name__}: {error}"
    )
    sys.exit(1)


print(
    "\n"
    + "=" * 80
)

print(
    "===== DAY 8 SECTIONS ====="
)

print(
    "=" * 80
)


if not isinstance(
    sections,
    dict,
):
    print(
        "Section classifier did not return a dictionary."
    )

    print(
        f"Returned type: "
        f"{type(sections).__name__}"
    )

    sections = {}


print(
    f"\nSections detected: "
    f"{len(sections)}"
)


for section_name, section_content in sections.items():

    print(
        "\n"
        + "-" * 70
    )

    print(
        f"SECTION: {section_name}"
    )

    print(
        "-" * 70
    )

    if isinstance(
        section_content,
        list,
    ):
        for item in section_content:
            print(
                item
            )
    else:
        print(
            section_content
        )


# ================================================================
# FIND EXPERIENCE-LIKE SECTIONS
# ================================================================

print(
    "\n"
    + "=" * 80
)

print(
    "===== EXPERIENCE-LIKE SECTION SEARCH ====="
)

print(
    "=" * 80
)

experience_terms = [
    "experience",
    "work experience",
    "professional experience",
    "relevant experience",
    "employment",
    "employment history",
    "work history",
    "professional history",
    "career history",
    "relevant work experience",
]


experience_sections = []

for section_name in sections.keys():

    normalized = (
        str(section_name)
        .lower()
        .strip()
    )

    if any(
        term in normalized
        for term in experience_terms
    ):
        experience_sections.append(
            section_name
        )


if experience_sections:

    print(
        "Experience-related sections found:"
    )

    for section_name in experience_sections:
        print(
            f"  - {section_name}"
        )

else:

    print(
        "NO EXPERIENCE-RELATED SECTION DETECTED."
    )


# ================================================================
# DAY 10 EXPERIENCE PARSER
# ================================================================

print(
    "\n"
    + "=" * 80
)

print(
    "===== DAY 10 EXPERIENCE PARSER ====="
)

print(
    "=" * 80
)

parser = ExperienceParser()

try:

    result = parser.parse_experience(
        resume_text
    )

except Exception as error:

    print(
        "ERROR during experience parsing:"
    )

    print(
        f"{type(error).__name__}: {error}"
    )

    sys.exit(1)


experiences = result.get(
    "experiences",
    [],
)

print(
    f"\nExperience records found: "
    f"{len(experiences)}"
)

for index, experience in enumerate(
    experiences,
    start=1,
):

    print(
        "\n"
        + "-" * 70
    )

    print(
        f"EXPERIENCE {index}"
    )

    print(
        "-" * 70
    )

    print(
        f"Job Title : "
        f"{experience.get('job_title', '')}"
    )

    print(
        f"Company   : "
        f"{experience.get('company', '')}"
    )

    print(
        f"Start     : "
        f"{experience.get('start_date')}"
    )

    print(
        f"End       : "
        f"{experience.get('end_date')}"
    )

    print(
        f"Duration  : "
        f"{experience.get('duration_months', 0)} months"
    )

    responsibilities = (
        experience.get(
            "responsibilities",
            [],
        )
    )

    print(
        f"Responsibilities: "
        f"{len(responsibilities)}"
    )

    for responsibility in responsibilities:
        print(
            f"  - {responsibility}"
        )


# ================================================================
# SUMMARY
# ================================================================

print(
    "\n"
    + "=" * 80
)

print(
    "===== DIAGNOSTIC SUMMARY ====="
)

print(
    "=" * 80
)

print(
    f"Extracted text       : {len(resume_text)} characters"
)

print(
    f"Sections detected    : {len(sections)}"
)

print(
    f"Experience sections  : {len(experience_sections)}"
)

print(
    f"Experience records   : {len(experiences)}"
)

print(
    f"Known experience     : "
    f"{result.get('total_experience_years', 0):.2f} years"
)

print(
    f"Gaps                 : "
    f"{len(result.get('gaps', []))}"
)

print(
    f"Overlaps             : "
    f"{len(result.get('overlaps', []))}"
)

print(
    "\nDiagnostic completed."
)