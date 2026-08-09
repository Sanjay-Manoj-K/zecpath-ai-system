from pydantic import BaseModel
from typing import List


class JobRequirement(BaseModel):
    """
    Structured representation of a Job Description.
    """

    role: str
    required_skills: List[str]
    experience: str
    education: str
    responsibilities: List[str]