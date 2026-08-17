"""
Day 9 - Skill Extraction Engine

Extracts technical, business and creative skills from resume text.

Features:
1. Master skill dictionary
2. Skill categories
3. Skill synonym normalization
4. Spelling variation handling
5. Skill stack expansion
6. Evidence-based confidence scoring
7. Deduplication
8. Section-aware extraction
9. CandidateProfile fallback skill merging
10. Structured skill output
11. Compact skill summary
"""

import re
from typing import Dict, List


class SkillExtractionEngine:
    """
    Extract skills from resume text using:

    - Master skill dictionary
    - Synonym normalization
    - Regex-based recognition
    - Skill-stack expansion
    - Section-aware confidence scoring
    - Deduplication
    - CandidateProfile fallback
    """

    # ============================================================
    # MASTER SKILL DICTIONARY
    # ============================================================

    MASTER_SKILLS = {

        # --------------------------------------------------------
        # PROGRAMMING LANGUAGES
        # --------------------------------------------------------

        "programming_languages": {
            "Python",
            "Java",
            "JavaScript",
            "TypeScript",
            "C",
            "C++",
            "C#",
            "Go",
            "Rust",
            "PHP",
            "Ruby",
            "Kotlin",
            "Swift",
            "Dart",
            "R",
            "MATLAB",
        },

        # --------------------------------------------------------
        # WEB DEVELOPMENT
        # --------------------------------------------------------

        "web_development": {
            "HTML",
            "CSS",
            "React",
            "Angular",
            "Vue.js",
            "Next.js",
            "Node.js",
            "Express.js",
            "Django",
            "Flask",
            "FastAPI",
            "Spring",
            "Spring Boot",
            "Laravel",
            "ASP.NET",
            "Nginx",
            "Apache",
        },

        # --------------------------------------------------------
        # DATABASES
        # --------------------------------------------------------

        "databases": {
            "SQL",
            "MySQL",
            "PostgreSQL",
            "MongoDB",
            "Oracle",
            "SQLite",
            "Redis",
            "Firebase",
            "DynamoDB",
            "MariaDB",
            "Cassandra",
        },

        # --------------------------------------------------------
        # AI / MACHINE LEARNING
        # --------------------------------------------------------

        "ai_ml": {
            "Artificial Intelligence",
            "Machine Learning",
            "Deep Learning",
            "Natural Language Processing",
            "Computer Vision",
            "Neural Networks",
            "TensorFlow",
            "PyTorch",
            "Scikit-learn",
            "Keras",
            "OpenCV",
            "Hugging Face",
            "Transformers",
            "Generative AI",
            "Large Language Models",
            "LLM",
        },

        # --------------------------------------------------------
        # DATA / ANALYTICS
        # --------------------------------------------------------

        "data": {
            "Data Science",
            "Data Analysis",
            "Data Visualization",
            "Pandas",
            "NumPy",
            "Matplotlib",
            "Seaborn",
            "Power BI",
            "Tableau",
            "Excel",
            "Statistics",
            "Data Mining",
        },

        # --------------------------------------------------------
        # DEVOPS / CLOUD
        # --------------------------------------------------------

        "devops_cloud": {
            "Git",
            "GitHub",
            "GitLab",
            "Docker",
            "Kubernetes",
            "Jenkins",
            "CI/CD",
            "Terraform",
            "Ansible",
            "AWS",
            "Azure",
            "Google Cloud",
            "GCP",
            "Linux",
            "Bash",
            "CloudFormation",
            "CodeDeploy",
            "Lambda",
        },

        # --------------------------------------------------------
        # MOBILE DEVELOPMENT
        # --------------------------------------------------------

        "mobile": {
            "Flutter",
            "Android",
            "iOS",
            "React Native",
            "SwiftUI",
            "Jetpack Compose",
        },

        # --------------------------------------------------------
        # CREATIVE / DESIGN
        # --------------------------------------------------------

        "creative": {
            "UI Design",
            "UX Design",
            "UI/UX Design",
            "Figma",
            "Adobe Photoshop",
            "Adobe Illustrator",
            "Adobe XD",
            "Graphic Design",
            "Wireframing",
            "Prototyping",
            "Visual Design",
            "Brand Design",
            "Typography",
            "Motion Graphics",
            "Video Editing",
        },

        # --------------------------------------------------------
        # BUSINESS / SOFT SKILLS
        # --------------------------------------------------------

        "business": {
            "Project Management",
            "Product Management",
            "Business Analysis",
            "Business Intelligence",
            "Market Research",
            "Digital Marketing",
            "SEO",
            "Content Marketing",
            "Sales",
            "Customer Relationship Management",
            "CRM",
            "Leadership",
            "Team Management",
            "Communication",
            "Presentation",
            "Problem Solving",
            "Time Management",
        },
    }

    # ============================================================
    # SYNONYMS / SPELLING VARIATIONS
    # ============================================================

    SYNONYMS = {

        # Python
        "python3": "Python",
        "python 3": "Python",
        "python 3.x": "Python",
        "py": "Python",

        # JavaScript
        "js": "JavaScript",
        "javascript es6": "JavaScript",
        "javascript es2015": "JavaScript",
        "ecmascript": "JavaScript",

        # TypeScript
        "ts": "TypeScript",

        # React
        "reactjs": "React",
        "react js": "React",
        "react.js": "React",

        # Node.js
        "node": "Node.js",
        "nodejs": "Node.js",
        "node js": "Node.js",
        "node.js": "Node.js",

        # Vue
        "vuejs": "Vue.js",
        "vue js": "Vue.js",
        "vue.js": "Vue.js",

        # Angular
        "angularjs": "Angular",
        "angular js": "Angular",

        # Databases
        "postgres": "PostgreSQL",
        "postgresql database": "PostgreSQL",
        "postgres database": "PostgreSQL",
        "mysql database": "MySQL",
        "mongo": "MongoDB",
        "mongodb database": "MongoDB",
        "mariadb database": "MariaDB",

        # AI / ML
        "ai": "Artificial Intelligence",
        "ml": "Machine Learning",
        "machine-learning": "Machine Learning",
        "dl": "Deep Learning",
        "deep-learning": "Deep Learning",
        "nlp": "Natural Language Processing",
        "natural-language processing":
            "Natural Language Processing",
        "cv": "Computer Vision",
        "computer-vision": "Computer Vision",

        # TensorFlow
        "tensorflow 2": "TensorFlow",
        "tensorflow2": "TensorFlow",
        "tensorflow 2.x": "TensorFlow",
        "tensor flow": "TensorFlow",
        "tensor-flow": "TensorFlow",
        "tensorflow": "TensorFlow",

        # Scikit-learn
        "sklearn": "Scikit-learn",
        "scikit learn": "Scikit-learn",
        "scikitlearn": "Scikit-learn",
        "scikit-learn": "Scikit-learn",

        # PyTorch
        "pytorch framework": "PyTorch",

        # Git
        "git version control": "Git",
        "git vcs": "Git",
        "version control": "Git",

        # GitHub
        "github repository": "GitHub",
        "github repos": "GitHub",

        # AWS
        "amazon web services": "AWS",
        "amazon aws": "AWS",

        # Azure
        "microsoft azure": "Azure",

        # Google Cloud
        "google cloud platform": "Google Cloud",
        "gcp cloud": "Google Cloud",

        # CI/CD
        "continuous integration": "CI/CD",
        "continuous deployment": "CI/CD",
        "continuous integration and deployment":
            "CI/CD",
        "continuous integration continuous deployment":
            "CI/CD",

        # UI / UX
        "ui ux": "UI/UX Design",
        "ui/ux": "UI/UX Design",
        "ui ux design": "UI/UX Design",
        "user interface design": "UI Design",
        "user experience design": "UX Design",

        # Design
        "figma design": "Figma",
        "adobe photoshop": "Adobe Photoshop",
        "adobe illustrator": "Adobe Illustrator",
    }

    # ============================================================
    # SKILL STACKS
    # ============================================================

    SKILL_STACKS = {

        "MERN": [
            "MongoDB",
            "Express.js",
            "React",
            "Node.js",
        ],

        "MEAN": [
            "MongoDB",
            "Express.js",
            "Angular",
            "Node.js",
        ],

        "MEVN": [
            "MongoDB",
            "Express.js",
            "Vue.js",
            "Node.js",
        ],

        "LAMP": [
            "Linux",
            "Apache",
            "MySQL",
            "PHP",
        ],

        "LEMP": [
            "Linux",
            "Nginx",
            "MySQL",
            "PHP",
        ],
    }

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self):
        self.skill_lookup = self._build_skill_lookup()

    # ============================================================
    # NORMALIZATION
    # ============================================================

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for skill comparison.
        """

        if not text:
            return ""

        text = text.lower().strip()

        text = text.replace("–", "-")
        text = text.replace("—", "-")
        text = text.replace("&", " and ")

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        text = re.sub(
            r"\s*/\s*",
            "/",
            text
        )

        text = re.sub(
            r"\s*\+\s*",
            "+",
            text
        )

        text = re.sub(
            r"\s*-\s*",
            "-",
            text
        )

        return text.strip()

    # ============================================================
    # BUILD LOOKUP
    # ============================================================

    def _build_skill_lookup(
        self
    ) -> Dict[str, str]:
        """
        Build normalized skill lookup.
        """

        lookup = {}

        for category_skills in (
            self.MASTER_SKILLS.values()
        ):

            for skill in category_skills:

                normalized = self.normalize_text(
                    skill
                )

                lookup[normalized] = skill

        for synonym, canonical in (
            self.SYNONYMS.items()
        ):

            normalized = self.normalize_text(
                synonym
            )

            lookup[normalized] = canonical

        return lookup

    # ============================================================
    # CATEGORY LOOKUP
    # ============================================================

    def get_skill_category(
        self,
        skill: str
    ) -> str:
        """
        Return category of a canonical skill.
        """

        for category, skills in (
            self.MASTER_SKILLS.items()
        ):

            if skill in skills:
                return category

        return "other"

    # ============================================================
    # SKILL STACK EXPANSION
    # ============================================================

    def expand_skill_stack(
        self,
        skill: str
    ) -> List[str]:
        """
        Expand technology stack.
        """

        normalized = self.normalize_text(
            skill
        )

        for stack, components in (
            self.SKILL_STACKS.items()
        ):

            if normalized == stack.lower():
                return components.copy()

        return []

    # ============================================================
    # SEARCH TERMS
    # ============================================================

    def _get_skill_terms(self) -> List[str]:
        """
        Return all canonical skills,
        synonyms and stacks.
        """

        terms = set()

        for category_skills in (
            self.MASTER_SKILLS.values()
        ):

            for skill in category_skills:

                terms.add(
                    self.normalize_text(skill)
                )

        for synonym in self.SYNONYMS:

            terms.add(
                self.normalize_text(synonym)
            )

        for stack in self.SKILL_STACKS:

            terms.add(
                self.normalize_text(stack)
            )

        return sorted(
            terms,
            key=len,
            reverse=True
        )

    # ============================================================
    # TERM MATCHING
    # ============================================================

    @staticmethod
    def _contains_term(
        text: str,
        term: str
    ) -> bool:
        """
        Detect a skill phrase inside text.
        """

        if not text or not term:
            return False

        pattern = (
            rf"(?<!\w){re.escape(term)}(?!\w)"
        )

        return bool(
            re.search(
                pattern,
                text,
                re.IGNORECASE
            )
        )

    # ============================================================
    # CONFIDENCE
    # ============================================================

    @staticmethod
    def calculate_confidence(
        detection_type: str,
        section: str
    ) -> float:
        """
        Evidence-based confidence scoring.
        """

        if detection_type == "skill_stack":
            return 0.96

        if detection_type == "derived":
            return 0.84

        if detection_type == "candidate_profile":
            return 0.80

        if detection_type == "canonical":

            confidence_map = {
                "skills": 0.98,
                "work_experience": 0.91,
                "projects": 0.88,
                "summary": 0.86,
                "unknown": 0.90,
            }

            return confidence_map.get(
                section,
                0.90
            )

        if detection_type == "synonym":

            confidence_map = {
                "skills": 0.94,
                "work_experience": 0.88,
                "projects": 0.85,
                "summary": 0.83,
                "unknown": 0.86,
            }

            return confidence_map.get(
                section,
                0.86
            )

        return 0.70

    # ============================================================
    # FIND SKILL MATCHES
    # ============================================================

    def _find_skill_matches(
        self,
        text: str,
        source_section: str = "unknown"
    ) -> List[Dict]:
        """
        Find skill mentions and calculate confidence.
        """

        matches = []

        normalized_text = self.normalize_text(
            text
        )

        for term in self._get_skill_terms():

            if not self._contains_term(
                normalized_text,
                term
            ):
                continue

            normalized_term = self.normalize_text(
                term
            )

            # ----------------------------------------------------
            # Skill Stack
            # ----------------------------------------------------

            if term.upper() in self.SKILL_STACKS:

                components = self.expand_skill_stack(
                    term
                )

                matches.append({
                    "name": term.upper(),
                    "canonical": term.upper(),
                    "category": "stack",
                    "confidence": self.calculate_confidence(
                        "skill_stack",
                        source_section
                    ),
                    "source": "skill_stack",
                    "section": source_section,
                    "derived_skills": components,
                })

                continue

            # ----------------------------------------------------
            # Canonical / synonym
            # ----------------------------------------------------

            canonical = self.skill_lookup.get(
                normalized_term
            )

            if not canonical:
                continue

            canonical_normalized = (
                self.normalize_text(
                    canonical
                )
            )

            is_exact_canonical = (
                normalized_term
                == canonical_normalized
            )

            detection_type = (
                "canonical"
                if is_exact_canonical
                else "synonym"
            )

            confidence = (
                self.calculate_confidence(
                    detection_type,
                    source_section
                )
            )

            matches.append({
                "name": canonical,
                "canonical": canonical,
                "category": self.get_skill_category(
                    canonical
                ),
                "confidence": confidence,
                "source": detection_type,
                "section": source_section,
            })

        return matches

    # ============================================================
    # DEDUPLICATION
    # ============================================================

    def deduplicate_skills(
        self,
        skills: List[Dict]
    ) -> List[Dict]:
        """
        Deduplicate normalized skills.

        Highest-confidence evidence wins.
        """

        best = {}

        for skill in skills:

            canonical = skill[
                "canonical"
            ]

            current = best.get(
                canonical
            )

            if (
                current is None
                or skill["confidence"]
                > current["confidence"]
            ):

                best[canonical] = skill

        return list(
            best.values()
        )

    # ============================================================
    # STACK COMPONENT EXPANSION
    # ============================================================

    def merge_stack_components(
        self,
        skills: List[Dict]
    ) -> List[Dict]:
        """
        Add individual technologies represented
        by detected stack names.
        """

        expanded = list(skills)

        for skill in skills:

            if skill["source"] != "skill_stack":
                continue

            components = skill.get(
                "derived_skills",
                []
            )

            for component in components:

                expanded.append({
                    "name": component,
                    "canonical": component,
                    "category": (
                        self.get_skill_category(
                            component
                        )
                    ),
                    "confidence": (
                        self.calculate_confidence(
                            "derived",
                            skill.get(
                                "section",
                                "unknown"
                            )
                        )
                    ),
                    "source": (
                        f"derived_from_"
                        f"{skill['canonical']}"
                    ),
                    "section": skill.get(
                        "section",
                        "unknown"
                    ),
                })

        return expanded

    # ============================================================
    # MAIN EXTRACTION
    # ============================================================

    def extract_skills(
        self,
        text: str,
        source_section: str = "unknown"
    ) -> Dict:
        """
        Extract skills from raw resume text.
        """

        if not text:

            return {
                "skills": [],
                "total_skills": 0,
            }

        detected = self._find_skill_matches(
            text,
            source_section
        )

        detected = self.merge_stack_components(
            detected
        )

        detected = self.deduplicate_skills(
            detected
        )

        detected.sort(
            key=lambda item:
            item["canonical"].lower()
        )

        return {
            "skills": detected,
            "total_skills": len(detected),
        }

    # ============================================================
    # EXTRACT FROM DAY 8 SECTIONS
    # ============================================================

    def extract_from_sections(
        self,
        sections: Dict[str, List[str]]
    ) -> Dict:
        """
        Extract skills section-by-section.

        Priority:
        1. Skills
        2. Work Experience
        3. Projects
        4. Summary
        """

        preferred_sections = [
            "skills",
            "work_experience",
            "projects",
            "summary",
        ]

        all_detected = []

        for section in preferred_sections:

            contents = sections.get(
                section,
                []
            )

            if not contents:
                continue

            section_text = "\n".join(
                contents
            )

            result = self.extract_skills(
                section_text,
                source_section=section
            )

            all_detected.extend(
                result["skills"]
            )

        all_detected = self.deduplicate_skills(
            all_detected
        )

        all_detected.sort(
            key=lambda item:
            item["canonical"].lower()
        )

        return {
            "skills": all_detected,
            "total_skills": len(all_detected),
        }

    # ============================================================
    # MERGE CANDIDATE PROFILE SKILLS
    # ============================================================

    def merge_candidate_skills(
        self,
        extracted_result: Dict,
        candidate_skills: List[str]
    ) -> Dict:
        """
        Merge Day 9 section-based extraction with
        skills already identified by CandidateProfile.

        CandidateProfile acts as fallback evidence when
        resume formatting causes a skill to be missed
        by section-based extraction.
        """

        combined = list(
            extracted_result.get(
                "skills",
                []
            )
        )

        for raw_skill in candidate_skills:

            if not raw_skill:
                continue

            normalized_raw = self.normalize_text(
                raw_skill
            )

            canonical = self.skill_lookup.get(
                normalized_raw
            )

            # ----------------------------------------------------
            # Known skill
            # ----------------------------------------------------

            if canonical:

                already_detected = any(
                    skill["canonical"].lower()
                    == canonical.lower()
                    for skill in combined
                )

                if already_detected:
                    continue

                combined.append({
                    "name": canonical,
                    "canonical": canonical,
                    "category": self.get_skill_category(
                        canonical
                    ),
                    "confidence": self.calculate_confidence(
                        "candidate_profile",
                        "candidate_profile"
                    ),
                    "source": "candidate_profile",
                    "section": "candidate_profile",
                })

            # ----------------------------------------------------
            # Unknown skill
            # ----------------------------------------------------

            else:

                already_detected = any(
                    skill["canonical"].lower()
                    == normalized_raw.lower()
                    for skill in combined
                )

                if already_detected:
                    continue

                display_name = raw_skill.strip()

                combined.append({
                    "name": display_name,
                    "canonical": display_name,
                    "category": "other",
                    "confidence": 0.70,
                    "source": "candidate_profile",
                    "section": "candidate_profile",
                })

        combined = self.deduplicate_skills(
            combined
        )

        combined.sort(
            key=lambda item:
            item["canonical"].lower()
        )

        return {
            "skills": combined,
            "total_skills": len(combined),
        }

    # ============================================================
    # DISPLAY DETAILED RESULTS
    # ============================================================

    def print_results(
        self,
        result: Dict
    ) -> None:
        """
        Print detailed structured skill results.
        """

        print("\n========================================")
        print("===== DAY 9 - SKILL EXTRACTION =====")
        print("========================================")

        print(
            f"\nTotal Skills: "
            f"{result['total_skills']}"
        )

        for skill in result["skills"]:

            print(
                f"\nSkill       : "
                f"{skill['canonical']}"
            )

            print(
                f"Category    : "
                f"{skill['category']}"
            )

            print(
                f"Confidence  : "
                f"{skill['confidence']:.2f}"
            )

            print(
                f"Source      : "
                f"{skill['source']}"
            )

            if skill.get("section"):

                print(
                    f"Section     : "
                    f"{skill['section']}"
                )

            if skill.get("derived_skills"):

                print(
                    "Derived     : "
                    + ", ".join(
                        skill["derived_skills"]
                    )
                )

    # ============================================================
    # COMPACT SKILL SUMMARY
    # ============================================================

    def print_skill_summary(
        self,
        result: Dict
    ) -> None:
        """
        Print all extracted skills in a compact
        table-like terminal format.
        """

        print(
            "\n=============================================="
        )

        print(
            "===== DAY 9 - SKILL SUMMARY ====="
        )

        print(
            "=============================================="
        )

        print(
            f"\nTotal Skills: "
            f"{result['total_skills']}\n"
        )

        print(
            f"{'Skill':<25}"
            f"{'Category':<22}"
            f"{'Confidence':<12}"
            f"{'Source':<25}"
        )

        print("-" * 84)

        for skill in result["skills"]:

            print(
                f"{skill['canonical']:<25}"
                f"{skill['category']:<22}"
                f"{skill['confidence']:<12.2f}"
                f"{skill['source']:<25}"
            )

        print("-" * 84)

        print(
            "\nSection-aware skill evidence:"
        )

        for skill in result["skills"]:

            section = skill.get(
                "section",
                "unknown"
            )

            print(
                f"  {skill['canonical']:<25}"
                f"→ {section}"
            )