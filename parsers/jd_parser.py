import re


def parse_job_description(text):
    """
    Convert raw job description text into structured requirements.
    """

    job = {
        "role": "",
        "required_skills": [],
        "experience": "",
        "education": "",
        "responsibilities": []
    }

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # -------------------------
    # Role
    # -------------------------
    if lines:
        job["role"] = lines[0]

    # -------------------------
    # Experience
    # -------------------------
    experience_patterns = [
        r"\d+\+?\s*years?\s+of\s+experience",
        r"\d+\s*-\s*\d+\s*years?\s+of\s+experience"
    ]

    for line in lines:
        for pattern in experience_patterns:
            match = re.search(pattern, line, re.IGNORECASE)

            if match:
                job["experience"] = match.group()
                break

        if job["experience"]:
            break

    # -------------------------
    # Required Skills
    # -------------------------
    skill_keywords = [
        "Python",
        "Django",
        "REST APIs",
        "SQL",
        "Git",
        "Java",
        "JavaScript",
        "React",
        "FastAPI",
        "Flask",
        "Machine Learning",
        "AWS",
        "Docker",
        "TensorFlow"
    ]

    jd_lower = text.lower()

    for skill in skill_keywords:
        if skill.lower() in jd_lower:
            job["required_skills"].append(skill)

    # -------------------------
    # Education
    # -------------------------
    for line in lines:
        if (
            "bachelor" in line.lower()
            or "master" in line.lower()
            or "degree" in line.lower()
        ):
            job["education"] = line
            break

    # -------------------------
    # Responsibilities
    # -------------------------
    inside_responsibilities = False

    for line in lines:

        if "responsibilities" in line.lower():
            inside_responsibilities = True
            continue

        if inside_responsibilities:

            if line.lower().startswith("requirements"):
                break

            if line.startswith("-"):
                job["responsibilities"].append(
                    line.lstrip("- ").strip()
                )

    return job


def read_job_description(file_path):
    """
    Read a text-based Job Description file.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()