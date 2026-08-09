from pathlib import Path

def read_job_description(file_path):
    """
    Read a job description from a text file.
    """

    file_path = Path(file_path)

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    return text