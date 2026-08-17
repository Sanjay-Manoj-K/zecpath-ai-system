import sys
import os

# Add project root to Python path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from parsers.resume_section_classifier import ResumeSectionClassifier


def main():

    resume_text = """
Sophia Martinez
Northwood, OH
Sophia.Martinez@example.com

Professional Summary
Innovative AI Software Developer with expertise in machine learning,
Python and TensorFlow.

Work History
AI Software Developer
January 2024 to August 2025
DeepTech Innovations
Developed AI algorithms and optimized neural networks.

Machine Learning Engineer
January 2022 to December 2023
Quantum AI Systems
Designed machine learning models.

Skills
Python
TensorFlow
Machine Learning
Artificial Intelligence
Neural Networks
Data Science

Certifications
Certified AI Practitioner
Machine Learning Specialist

Education
Master of Science: Computer Science
Stanford University

Bachelor of Science: Data Science
University of California, Berkeley

Projects
AI Resume Screening System
Developed a Python-based resume analysis application.
"""

    classifier = ResumeSectionClassifier()

    sections = classifier.segment(resume_text)

    classifier.print_sections(sections)

    print("\n========================================")
    print("===== DETAILED BLOCK CLASSIFICATION =====")
    print("========================================")

    results = classifier.classify_blocks(resume_text)

    for result in results:

        print(
            f"\nBlock {result['block_id']}"
        )

        print(
            f"Section    : {result['section']}"
        )

        print(
            f"Method     : {result['method']}"
        )

        print(
            f"Confidence : {result['confidence']}"
        )

        print(
            f"Text       : {result['text'][:100]}"
        )


if __name__ == "__main__":
    main()