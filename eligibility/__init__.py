"""Day 21 Eligibility Decision Engine package."""
from .config import EligibilityRules, load_rules_for_role
from .decision_engine import evaluate_eligibility

__all__ = ["EligibilityRules", "load_rules_for_role", "evaluate_eligibility"]
