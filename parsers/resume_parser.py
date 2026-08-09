def parse_resume_text(resume_text: str) -> dict:
    """
    Parse extracted resume text into structured candidate information.
    """

    # ==========================================
    # Clean Resume Text
    # ==========================================

    lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]

    full_text = " ".join(lines)

    # ==========================================
    # Candidate Structure
    # ==========================================

    candidate = {
        "name": "",
        "skills": [],
        "experience": "",
        "education": "",
        "certifications": [],
        "languages": []
    }

    # ==========================================
    # Candidate Name
    # ==========================================

    if lines:
        candidate["name"] = lines[0]

    # ==========================================
    # Find Resume Sections
    # ==========================================

    skills_index = -1
    work_index = -1
    education_index = -1
    certification_index = -1
    languages_index = -1

    for i, line in enumerate(lines):

        section = line.lower().strip()

        if section == "skills":
            skills_index = i

        elif section in ["work history", "experience"]:
            work_index = i

        elif section == "education":
            education_index = i

        elif section == "certifications":
            certification_index = i

        elif section == "languages":
            languages_index = i

    # ==========================================
    # Extract Explicit Skills
    # ==========================================

    explicit_skills = []

    if skills_index != -1:

        end = len(lines)

        for index in [
            work_index,
            education_index,
            certification_index,
            languages_index
        ]:
            if index > skills_index:
                end = min(end, index)

        explicit_skills = lines[skills_index + 1:end]

    # ==========================================
    # Detect Technical Skills From Resume
    # ==========================================

    known_skills = [
        "Python",
        "Java",
        "JavaScript",
        "C++",
        "C#",
        "Django",
        "Flask",
        "FastAPI",
        "React",
        "HTML",
        "CSS",
        "SQL",
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "REST API",
        "REST APIs",
        "Git",
        "GitHub",
        "Docker",
        "AWS",
        "Azure",
        "TensorFlow",
        "PyTorch",
        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",
        "Neural Networks",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "Matplotlib",
        "Data Science"
    ]

    detected_skills = []

    for skill in known_skills:

        if skill.lower() in full_text.lower():

            # Avoid duplicate REST API / REST APIs
            if skill == "REST API" and "REST APIs" in full_text:
                continue

            detected_skills.append(skill)

    # ==========================================
    # Combine Skills
    # ==========================================

    all_skills = explicit_skills + detected_skills

    # Remove duplicates while preserving order
    candidate["skills"] = list(dict.fromkeys(all_skills))

    # ==========================================
    # Extract Certifications
    # ==========================================

    if certification_index != -1:

        end = len(lines)

        for index in [
            education_index,
            languages_index
        ]:
            if index > certification_index:
                end = min(end, index)

        candidate["certifications"] = lines[
            certification_index + 1:end
        ]

    # ==========================================
    # Extract Education
    # ==========================================

    if education_index != -1:

        end = len(lines)

        if languages_index > education_index:
            end = languages_index

        candidate["education"] = " ".join(
            lines[education_index + 1:end]
        )

    # ==========================================
    # Extract Experience
    # ==========================================

    if work_index != -1:

        end = len(lines)

        for index in [
            education_index,
            certification_index,
            languages_index
        ]:
            if index > work_index:
                end = min(end, index)

        candidate["experience"] = " ".join(
            lines[work_index + 1:end]
        )

    # ==========================================
    # Extract Languages
    # ==========================================

    if languages_index != -1:

        candidate["languages"] = lines[
            languages_index + 1:
        ]

    # ==========================================
    # Return Structured Candidate
    # ==========================================

    return candidate