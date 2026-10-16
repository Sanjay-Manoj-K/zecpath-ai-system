"""Day 21 eligibility rule configuration."""
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class EligibilityRules:
    """Recruiter-configurable rules for one job role."""

    role: str
    minimum_ats_score: float = 0.70
    mandatory_skills: List[str] = field(default_factory=list)
    min_experience_years: Optional[float] = None
    max_experience_years: Optional[float] = None
    allowed_locations: List[str] = field(default_factory=list)
    require_availability_confirmation: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.role, str) or not self.role.strip():
            raise ValueError("role must be a non-empty string")
        if not 0.0 <= self.minimum_ats_score <= 1.0:
            raise ValueError("minimum_ats_score must be between 0 and 1")
        if any(not isinstance(s, str) or not s.strip() for s in self.mandatory_skills):
            raise ValueError("mandatory_skills must contain non-empty strings")
        if any(not isinstance(s, str) or not s.strip() for s in self.allowed_locations):
            raise ValueError("allowed_locations must contain non-empty strings")
        if self.min_experience_years is not None and self.min_experience_years < 0:
            raise ValueError("Minimum experience cannot be negative")
        if self.max_experience_years is not None and self.max_experience_years < 0:
            raise ValueError("Maximum experience cannot be negative")
        if (
            self.min_experience_years is not None
            and self.max_experience_years is not None
            and self.min_experience_years > self.max_experience_years
        ):
            raise ValueError("Minimum experience cannot exceed maximum experience")

    @classmethod
    def from_dict(cls, role: str, data: Dict[str, Any]) -> "EligibilityRules":
        skills = data.get("mandatory_skills", [])
        locations = data.get("allowed_locations", [])
        if not isinstance(skills, list) or not isinstance(locations, list):
            raise ValueError("Skills and locations must be lists")

        def optional_float(value: Any) -> Optional[float]:
            if value is None:
                return None
            try:
                return float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError("Experience bounds must be numbers or null") from exc

        return cls(
            role=role,
            minimum_ats_score=float(data.get("minimum_ats_score", 0.70)),
            mandatory_skills=skills,
            min_experience_years=optional_float(data.get("min_experience_years")),
            max_experience_years=optional_float(data.get("max_experience_years")),
            allowed_locations=locations,
            require_availability_confirmation=bool(
                data.get("require_availability_confirmation", False)
            ),
        )


def load_rules_for_role(path: str, role: str) -> EligibilityRules:
    """Load and validate the requested role from a JSON rules file."""
    try:
        with Path(path).open("r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
    except OSError as exc:
        raise FileNotFoundError("Eligibility rules file not found: {}".format(path)) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("Eligibility rules file contains invalid JSON") from exc

    roles = payload.get("roles") if isinstance(payload, dict) else None
    if not isinstance(roles, dict):
        raise ValueError("Configuration must contain a 'roles' object")
    if role not in roles:
        raise KeyError("No rules configured for role: {}".format(role))
    if not isinstance(roles[role], dict):
        raise ValueError("Rules for the requested role must be an object")

    return EligibilityRules.from_dict(role, roles[role])
