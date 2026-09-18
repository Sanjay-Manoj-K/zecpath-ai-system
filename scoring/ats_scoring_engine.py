from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Any


@dataclass
class ScoreComponent:
    name: str
    raw_score: Optional[float]
    base_weight: float
    effective_weight: float
    contribution: float
    available: bool


class ATSScoringEngine:
    """
    Transparent ATS scoring engine.

    Combines:
        - skill match
        - experience relevance
        - education alignment
        - semantic similarity

    Missing signals are excluded from the calculation and the
    remaining weights are dynamically normalized.
    """

    DEFAULT_WEIGHTS = {
        "default": {
            "skill_match": 0.35,
            "experience_relevance": 0.20,
            "education_alignment": 0.15,
            "semantic_similarity": 0.30,
        },

        "software_engineering": {
            "skill_match": 0.35,
            "experience_relevance": 0.20,
            "education_alignment": 0.10,
            "semantic_similarity": 0.35,
        },

        "ai_ml": {
            "skill_match": 0.30,
            "experience_relevance": 0.20,
            "education_alignment": 0.10,
            "semantic_similarity": 0.40,
        },

        "data_science": {
            "skill_match": 0.30,
            "experience_relevance": 0.20,
            "education_alignment": 0.10,
            "semantic_similarity": 0.40,
        },

        "finance": {
            "skill_match": 0.40,
            "experience_relevance": 0.20,
            "education_alignment": 0.15,
            "semantic_similarity": 0.25,
        },

        "legal": {
            "skill_match": 0.40,
            "experience_relevance": 0.20,
            "education_alignment": 0.15,
            "semantic_similarity": 0.25,
        },
    }

    SIGNALS = (
        "skill_match",
        "experience_relevance",
        "education_alignment",
        "semantic_similarity",
    )

    ROLE_ALIASES = {
        "software engineer": "software_engineering",
        "software developer": "software_engineering",
        "python developer": "software_engineering",
        "backend developer": "software_engineering",
        "ai/ml engineer": "ai_ml",
        "ai ml engineer": "ai_ml",
        "machine learning engineer": "ai_ml",
        "data scientist": "data_science",
        "finance analyst": "finance",
        "financial analyst": "finance",
        "legal intern": "legal",
        "law intern": "legal",
    }

    def __init__(
        self,
        role_weights: Optional[Dict[str, Dict[str, float]]] = None,
    ):
        self.role_weights = role_weights or self.DEFAULT_WEIGHTS
        self._validate_weights()

    def _validate_weights(self) -> None:
        for role, weights in self.role_weights.items():
            missing = set(self.SIGNALS) - set(weights)

            if missing:
                raise ValueError(
                    f"Role '{role}' is missing weights: {sorted(missing)}"
                )

            total = sum(weights.values())

            if total <= 0:
                raise ValueError(
                    f"Weights for role '{role}' must have a positive total."
                )

    def normalize_role(self, role: str) -> str:
        role_key = role.strip().lower()

        if role_key in self.role_weights:
            return role_key

        return self.ROLE_ALIASES.get(role_key, "default")

    def get_weights(self, role: str) -> Dict[str, float]:
        normalized_role = self.normalize_role(role)

        return dict(
            self.role_weights.get(
                normalized_role,
                self.role_weights["default"],
            )
        )

    @staticmethod
    def _validate_score(value: float) -> float:
        if not isinstance(value, (int, float)):
            raise TypeError("Scores must be numeric.")

        if value < 0 or value > 1:
            raise ValueError(
                "Scores must be between 0 and 1."
            )

        return float(value)

    def calculate_score(
        self,
        *,
        role: str,
        skill_match: Optional[float],
        experience_relevance: Optional[float],
        education_alignment: Optional[float],
        semantic_similarity: Optional[float],
        candidate_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        values = {
            "skill_match": skill_match,
            "experience_relevance": experience_relevance,
            "education_alignment": education_alignment,
            "semantic_similarity": semantic_similarity,
        }

        base_weights = self.get_weights(role)

        available = {
            key: self._validate_score(value)
            for key, value in values.items()
            if value is not None
        }

        if not available:
            raise ValueError(
                "At least one scoring signal must be available."
            )

        available_weight_total = sum(
            base_weights[key]
            for key in available
        )

        if available_weight_total <= 0:
            raise ValueError(
                "Available scoring signals have zero total weight."
            )

        components = {}

        weighted_sum = 0.0

        for key in self.SIGNALS:

            raw_score = available.get(key)
            is_available = raw_score is not None

            if is_available:
                effective_weight = (
                    base_weights[key]
                    / available_weight_total
                )

                contribution = (
                    raw_score * effective_weight
                )

                weighted_sum += contribution

            else:
                effective_weight = 0.0
                contribution = 0.0

            components[key] = ScoreComponent(
                name=key,
                raw_score=raw_score,
                base_weight=base_weights[key],
                effective_weight=effective_weight,
                contribution=contribution,
                available=is_available,
            )

        final_score = round(weighted_sum, 4)

        return {
            "candidate_id": candidate_id,
            "role": role,
            "normalized_role": self.normalize_role(role),
            "final_score": final_score,
            "final_percentage": round(final_score * 100, 2),
            "available_signals": list(available.keys()),
            "missing_signals": [
                key
                for key in self.SIGNALS
                if key not in available
            ],
            "components": {
                key: {
                    "score": value.raw_score,
                    "base_weight": round(
                        value.base_weight, 4
                    ),
                    "effective_weight": round(
                        value.effective_weight, 4
                    ),
                    "contribution": round(
                        value.contribution, 4
                    ),
                    "available": value.available,
                }
                for key, value in components.items()
            },
        }

    def generate_candidate_score(
        self,
        candidate_id: str,
        role: str,
        signals: Dict[str, Optional[float]],
    ) -> Dict[str, Any]:

        return self.calculate_score(
            role=role,
            skill_match=signals.get("skill_match"),
            experience_relevance=signals.get(
                "experience_relevance"
            ),
            education_alignment=signals.get(
                "education_alignment"
            ),
            semantic_similarity=signals.get(
                "semantic_similarity"
            ),
            candidate_id=candidate_id,
        )


if __name__ == "__main__":

    engine = ATSScoringEngine()

    result = engine.generate_candidate_score(
        candidate_id="candidate_001",
        role="Python Developer",
        signals={
            "skill_match": 0.80,
            "experience_relevance": 0.70,
            "education_alignment": 1.00,
            "semantic_similarity": 0.66,
        },
    )

    print("=" * 70)
    print("DAY 13 - ATS SCORING ENGINE TEST")
    print("=" * 70)

    print(f"Role           : {result['role']}")
    print(f"Normalized role: {result['normalized_role']}")
    print(f"Final score    : {result['final_percentage']}%")

    print("\nComponent Breakdown:")

    for name, component in result["components"].items():
        print(f"\n{name}")
        print(f"  Score             : {component['score']}")
        print(f"  Base weight       : {component['base_weight']}")
        print(f"  Effective weight  : {component['effective_weight']}")
        print(f"  Contribution      : {component['contribution']}")
        print(f"  Available         : {component['available']}")

    print("\nAvailable signals:")
    print(result["available_signals"])

    print("\nMissing signals:")
    print(result["missing_signals"])

    print("=" * 70)