from pydantic import BaseModel
from typing import List


class CandidateProfile(BaseModel):
    """
    Structured representation of a candidate resume.
    """

    name: str
    skills: List[str]
    experience: str
    education: str
    certifications: List[str]
    languages: List[str]