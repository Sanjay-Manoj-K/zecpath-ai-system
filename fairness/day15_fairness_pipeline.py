"""
Day 15 - Integrated Fairness Pipeline

Integrates the Day 15 fairness components:

    1. Resume normalization
    2. Personal attribute masking
    3. Reduced keyword dependence
    4. Day 13 ATS scoring
    5. Score normalization

The original Day 13 score is preserved separately from the
fairness-adjusted score.

No original resume file is modified.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from fairness.resume_normalizer import (
    normalize_resume_text,
)

from fairness.personal_attribute_masker import (
    PersonalAttributeMasker,
)

from fairness.keyword_dependence_reducer import (
    KeywordDependenceReducer,
)

from fairness.score_normalizer import (
    ScoreNormalizer,
)


class Day15FairnessPipeline:
    """
    Integrate Day 15 fairness components around the existing
    ATS scoring workflow.
    """

    def __init__(
        self,
        exact_weight: float = 0.40,
        semantic_weight: float = 0.60,
        similarity_threshold: float = 0.65,
    ) -> None:

        self.masker = (
            PersonalAttributeMasker()
        )

        self.skill_matcher = (
            KeywordDependenceReducer(
                exact_weight=exact_weight,
                semantic_weight=semantic_weight,
                similarity_threshold=similarity_threshold,
            )
        )

        self.score_normalizer = (
            ScoreNormalizer()
        )

    # --------------------------------------------------------------
    # Resume preparation
    # --------------------------------------------------------------

    def prepare_resume(
        self,
        resume_text: str,
    ) -> Dict[str, Any]:
        """
        Normalize and mask a resume before evaluation.
        """

        normalized_text = normalize_resume_text(
            resume_text
        )

        detected_attributes = (
            self.masker.detect_attributes(
                normalized_text
            )
        )

        masked_text = self.masker.mask_text(
            normalized_text
        )

        return {
            "normalized_text": normalized_text,
            "masked_text": masked_text,
            "detected_attributes":
                detected_attributes,
        }

    # --------------------------------------------------------------
    # Fair skill scoring
    # --------------------------------------------------------------

    def calculate_fair_skill_score(
        self,
        candidate_skills: Iterable[str],
        required_skills: Iterable[str],
    ) -> Dict[str, Any]:
        """
        Calculate hybrid skill relevance using both exact and
        semantic matching.
        """

        result = (
            self.skill_matcher.calculate_hybrid_match(
                candidate_skills,
                required_skills,
            )
        )

        return result.to_dict()

    # --------------------------------------------------------------
    # Fairness score adjustment
    # --------------------------------------------------------------

    def calculate_adjusted_signals(
        self,
        original_signals: Dict[str, Any],
        candidate_skills: Iterable[str],
        required_skills: Iterable[str],
    ) -> Dict[str, Any]:
        """
        Replace only the skill-match signal with the Day 15
        hybrid score.

        Other Day 13 signals remain unchanged.
        """

        hybrid_result = (
            self.calculate_fair_skill_score(
                candidate_skills,
                required_skills,
            )
        )

        adjusted_signals = dict(
            original_signals
        )

        adjusted_signals[
            "skill_match"
        ] = hybrid_result[
            "hybrid_match_score"
        ]

        return {
            "original_signals": original_signals,
            "adjusted_signals": adjusted_signals,
            "skill_analysis": hybrid_result,
        }

    # --------------------------------------------------------------
    # Candidate score comparison
    # --------------------------------------------------------------

    def compare_scores(
        self,
        candidates: Iterable[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Compare original ATS scores with fairness-adjusted scores.

        Expected candidate structure:

            {
                "candidate_id": "...",
                "final_score": 0.60,
                "signals": {
                    "skill_match": 0.40,
                    "experience_relevance": 0.60,
                    "education_alignment": 1.0,
                    "semantic_similarity": 0.55
                },
                "candidate_skills": [...],
                "required_skills": [...]
            }
        """

        candidate_list = list(
            candidates
        )

        results: List[
            Dict[str, Any]
        ] = []

        # The existing Day 13 engine is imported lazily so this
        # module can still be tested independently.
        from scoring.ats_scoring_engine import (
            ATSScoringEngine,
        )

        ats_engine = (
            ATSScoringEngine()
        )

        for candidate in candidate_list:

            if not isinstance(candidate, dict):
                raise TypeError(
                    "Each candidate must be a dictionary."
                )

            if "final_score" not in candidate:
                raise KeyError(
                    "Candidate is missing 'final_score'."
                )

            if "signals" not in candidate:
                raise KeyError(
                    "Candidate is missing 'signals'."
                )

            original_signals = dict(
                candidate["signals"]
            )

            candidate_skills = (
                candidate.get(
                    "candidate_skills",
                    [],
                )
            )

            required_skills = (
                candidate.get(
                    "required_skills",
                    [],
                )
            )

            adjusted = (
                self.calculate_adjusted_signals(
                    original_signals,
                    candidate_skills,
                    required_skills,
                )
            )

            candidate_id = candidate.get(
                "candidate_id",
                "candidate",
            )

            role = candidate.get(
                "role",
                "unknown",
            )

            adjusted_result = (
                ats_engine.generate_candidate_score(
                    candidate_id=candidate_id,
                    role=role,
                    signals=adjusted[
                        "adjusted_signals"
                    ],
                )
            )

            result = {
                **candidate,

                "original_final_score": (
                    candidate["final_score"]
                ),

                "fairness_adjusted_score": (
                    adjusted_result[
                        "final_score"
                    ]
                ),

                "fairness_adjusted_percentage": (
                    adjusted_result[
                        "final_percentage"
                    ]
                ),

                "original_skill_match": (
                    original_signals.get(
                        "skill_match"
                    )
                ),

                "hybrid_skill_match": (
                    adjusted[
                        "skill_analysis"
                    ][
                        "hybrid_match_score"
                    ]
                ),

                "exact_skill_match": (
                    adjusted[
                        "skill_analysis"
                    ][
                        "exact_match_score"
                    ]
                ),

                "semantic_skill_match": (
                    adjusted[
                        "skill_analysis"
                    ][
                        "semantic_match_score"
                    ]
                ),

                "fairness_skill_analysis": (
                    adjusted[
                        "skill_analysis"
                    ]
                ),
            }

            results.append(result)

        return results

    # --------------------------------------------------------------
    # Batch score normalization
    # --------------------------------------------------------------

    def normalize_fairness_scores(
        self,
        candidates: Iterable[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Normalize fairness-adjusted scores across the candidate set.
        """

        candidate_list = list(
            candidates
        )

        prepared = []

        for candidate in candidate_list:

            if "fairness_adjusted_score" not in candidate:
                raise KeyError(
                    "Candidate is missing "
                    "'fairness_adjusted_score'."
                )

            prepared.append(
                dict(candidate)
            )

        normalized = (
            self.score_normalizer.normalize_candidates(
                prepared,
                score_key="fairness_adjusted_score",
                normalized_key="fairness_normalized_score",
            )
        )

        return normalized