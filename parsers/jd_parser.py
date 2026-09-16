import re


# ============================================================
# SUPPORTED SKILL VOCABULARY
# ============================================================

SKILL_KEYWORDS = [
    # Programming
    "Python",
    "Java",
    "JavaScript",
    "C++",
    "C#",

    # Web / Backend
    "Django",
    "Flask",
    "FastAPI",
    "REST API",
    "REST APIs",
    "API",
    "Web Development",

    # Frontend
    "React",
    "HTML",
    "CSS",

    # Databases
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",

    # Version control / DevOps
    "Git",
    "GitHub",
    "Docker",
    "Jenkins",
    "CI/CD",

    # Cloud
    "AWS",
    "Azure",
    "Google Cloud",

    # AI / ML
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "AI",
    "Neural Networks",
    "Supervised Learning",
    "Unsupervised Learning",
    "TensorFlow",
    "PyTorch",
    "Scikit-learn",
    "Pandas",
    "NumPy",
    "Data Science",
    "Data Analysis",
    "Feature Engineering",
    "Data Preprocessing",
    "Statistics",
    "Predictive Modeling",
    "Predictive Models",

    # Finance
    "Financial Modeling",
    "Financial Analysis",
    "Financial Reporting",
    "Financial Planning",
    "Budgeting",
    "Forecasting",
    "Reconciliation",
    "Accounting",
    "Financial Data",
    "Numerical Analysis",

    # Legal
    "Legal Research",
    "Legal Writing",
    "Legal Documentation",
    "Legal Principles",
    "Case Research",
    "Statute Research",
    "Case Preparation",
    "Legal Analysis",
    "Legal Information",

    # General professional skills
    "Communication",
    "Written Communication",
    "Verbal Communication",
    "Problem Solving",
    "Problem-Solving",
    "Teamwork",
    "Leadership",
    "Attention to Detail",
    "Analytical Skills",
    "Critical Thinking",
    "Debugging",
    "Unit Testing",
    "Software Development",
]


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize text for reliable case-insensitive matching.
    """

    if text is None:
        return ""

    text = str(text).lower()

    # Normalize different dash characters.
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Normalize whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_skills(text: str):
    """
    Extract known skills from a Job Description.

    Matching is case-insensitive.
    """

    normalized_text = normalize_text(text)

    detected_skills = []

    for skill in SKILL_KEYWORDS:

        normalized_skill = normalize_text(
            skill
        )

        if not normalized_skill:
            continue

        if normalized_skill in normalized_text:

            # Avoid duplicate API / REST API style overlaps.
            if (
                skill == "API"
                and (
                    "rest api" in normalized_text
                    or "rest apis" in normalized_text
                )
            ):
                continue

            if skill not in detected_skills:
                detected_skills.append(skill)

    return detected_skills


# ============================================================
# JOB DESCRIPTION PARSER
# ============================================================

def parse_job_description(text):
    """
    Convert raw job description text into structured requirements.
    """

    if text is None:
        text = ""

    lines = [
        line.strip()
        for line in str(text).splitlines()
        if line.strip()
    ]

    job = {
        "role": "",
        "required_skills": [],
        "experience": "",
        "education": "",
        "responsibilities": [],
    }

    # --------------------------------------------------------
    # Role
    # --------------------------------------------------------

    if lines:
        job["role"] = lines[0]

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    experience_patterns = [

        r"\d+\+?\s*years?\s+of\s+experience",

        r"\d+\s*-\s*\d+\s*years?\s+of\s+experience",

        r"\d+\+?\s*years?\s+experience",

        r"\d+\s*-\s*\d+\s*years?\s+experience",

        r"experience\s+with\s+\w+",

        r"prior\s+experience",

        r"professional\s+experience",

        r"work\s+experience",
    ]

    for line in lines:

        for pattern in experience_patterns:

            match = re.search(
                pattern,
                line,
                re.IGNORECASE,
            )

            if match:

                job["experience"] = line.strip()

                break

        if job["experience"]:
            break

    # --------------------------------------------------------
    # Required Skills
    # --------------------------------------------------------

    job["required_skills"] = extract_skills(
        text
    )

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    for line in lines:

        lower_line = line.lower()

        if (
            "bachelor" in lower_line
            or "master" in lower_line
            or "degree" in lower_line
            or "juris doctor" in lower_line
            or "phd" in lower_line
            or "doctorate" in lower_line
        ):

            job["education"] = line

            break

    # --------------------------------------------------------
    # Responsibilities
    # --------------------------------------------------------

    inside_responsibilities = False

    for line in lines:

        lower_line = line.lower()

        # Start responsibilities section.
        if "responsibilities" in lower_line:

            inside_responsibilities = True

            continue

        # Stop at another major section.
        if inside_responsibilities:

            if (
                lower_line.startswith("requirements")
                or lower_line.startswith("qualifications")
                or lower_line.startswith("education")
                or lower_line.startswith("skills")
            ):
                break

            if line.startswith("-"):

                responsibility = (
                    line.lstrip("- ")
                    .strip()
                )

                if responsibility:
                    job["responsibilities"].append(
                        responsibility
                    )

    return job


# ============================================================
# FILE READER
# ============================================================

def read_job_description(file_path):
    """
    Read a text-based Job Description file.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:

        return file.read()


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("JOB DESCRIPTION PARSER TEST")
    print("=" * 70)

    sample_text = """
    Finance Analyst

    Requirements:
    - Bachelor's degree in Finance or Accounting.
    - Experience with financial modeling and budgeting.
    - Knowledge of financial reporting and reconciliation.
    - Strong analytical and numerical skills.

    Responsibilities:
    - Analyze financial data.
    - Prepare budgets and financial models.
    - Support forecasting and financial planning.
    - Prepare reports for management.
    """

    result = parse_job_description(
        sample_text
    )

    print("\nRole:")
    print(result["role"])

    print("\nRequired skills:")
    for skill in result["required_skills"]:
        print("-", skill)

    print("\nExperience:")
    print(result["experience"])

    print("\nEducation:")
    print(result["education"])

    print("\nResponsibilities:")
    for responsibility in result["responsibilities"]:
        print("-", responsibility)

    print("\n" + "=" * 70)
    print("JOB DESCRIPTION PARSER TEST COMPLETE")
    print("=" * 70)