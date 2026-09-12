from parsers.experience_parser import ExperienceParser


def main():

    parser = ExperienceParser()

    work_experience = """
    AI Software Developer
    January 2024 to August 2025
    DeepTech Innovations — Northwood, OH
    Developed AI algorithms, boosting accuracy by 20%
    Implemented a new ML pipeline, reducing processing time
    Optimized neural networks, improving efficiency by 35%

    Machine Learning Engineer
    January 2022 to December 2023
    Quantum AI Systems — Cleveland, OH
    Designed ML models, increasing predictive power by 15%
    Integrated AI solutions into software, reducing errors by 40%
    Streamlined data processing, boosting throughput

    Data Scientist
    January 2020 to December 2021
    TechData Corp — Northwood, OH
    Analyzed datasets to uncover actionable business insights
    Led a team in predictive modeling initiatives
    Automated data workflows, improving reporting efficiency
    """

    result = parser.parse_experience(
        work_experience
    )

    parser.print_results(
        result
    )


if __name__ == "__main__":
    main()