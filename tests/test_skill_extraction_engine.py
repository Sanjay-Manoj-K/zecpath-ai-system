from parsers.skill_extraction_engine import SkillExtractionEngine


def main():

    engine = SkillExtractionEngine()

    sections = {
        "skills": [
            """
            Python
            Python3
            ReactJS
            Tensor Flow
            Git
            MERN
            Figma
            """
        ],

        "work_experience": [
            """
            Developed applications using Django,
            PostgreSQL and AWS.
            """
        ],

        "projects": [
            """
            Built a machine learning project using
            PyTorch and Scikit Learn.
            """
        ],

        "summary": [
            """
            AI developer with experience in
            JavaScript and Docker.
            """
        ]
    }

    result = engine.extract_from_sections(sections)

    engine.print_results(result)

    engine.print_skill_summary(result)


if __name__ == "__main__":
    main()