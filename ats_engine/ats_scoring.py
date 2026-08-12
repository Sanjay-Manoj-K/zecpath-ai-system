import re


class ATSScore:
    """
    Calculates the compatibility between a candidate profile
    and a job requirement.
    """

    def __init__(self, candidate, job):
        self.candidate = candidate
        self.job = job

    # =========================================================
    # SKILL SCORING
    # =========================================================

    def calculate_skill_score(self):
        """
        Calculate skill matching percentage.
        """

        required_skills = [
            skill.lower().strip()
            for skill in self.job.required_skills
        ]

        candidate_skills = [
            skill.lower().strip()
            for skill in self.candidate.skills
        ]

        if not required_skills:
            return 0

        matched_skills = [
            skill
            for skill in required_skills
            if skill in candidate_skills
        ]

        score = (
            len(matched_skills)
            / len(required_skills)
        ) * 100

        return round(score, 2)

    # =========================================================
    # MATCHED SKILLS
    # =========================================================

    def get_matched_skills(self):
        """
        Return skills required by the job
        that are present in the candidate profile.
        """

        candidate_skills = [
            skill.lower().strip()
            for skill in self.candidate.skills
        ]

        matched = [
            skill
            for skill in self.job.required_skills
            if skill.lower().strip() in candidate_skills
        ]

        return matched

    # =========================================================
    # MISSING SKILLS
    # =========================================================

    def get_missing_skills(self):
        """
        Return required skills that are missing
        from the candidate profile.
        """

        candidate_skills = [
            skill.lower().strip()
            for skill in self.candidate.skills
        ]

        missing = [
            skill
            for skill in self.job.required_skills
            if skill.lower().strip() not in candidate_skills
        ]

        return missing

    # =========================================================
    # EXPERIENCE EXTRACTION
    # =========================================================

    def extract_years(self, text):
        """
        Extract the number of years from experience text.

        Examples:
            '2+ years of experience' -> 2
            '3 years experience' -> 3
        """

        if not text:
            return 0

        match = re.search(
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
            text.lower()
        )

        if match:
            return float(match.group(1))

        return 0

    # =========================================================
    # EXPERIENCE DATE RANGE EXTRACTION
    # =========================================================

    def extract_experience_ranges(self, text):
        """
        Extract employment date ranges from resume text.

        Supported examples:

            January 2024 to August 2025
            January 2022 to December 2023
            January 2020 to December 2021

        Returns:

            [
                (2024, 1, 2025, 8),
                (2022, 1, 2023, 12),
                (2020, 1, 2021, 12)
            ]
        """

        if not text:
            return []

        pattern = (
            r"(January|February|March|April|May|June|July|August|"
            r"September|October|November|December)\s+"
            r"(20\d{2})\s+"
            r"(?:to|-)\s+"
            r"(January|February|March|April|May|June|July|August|"
            r"September|October|November|December)\s+"
            r"(20\d{2})"
        )

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        month_map = {
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12
        }

        ranges = []

        for start_month, start_year, end_month, end_year in matches:

            start_month_number = month_map[
                start_month.lower()
            ]

            end_month_number = month_map[
                end_month.lower()
            ]

            ranges.append(
                (
                    int(start_year),
                    start_month_number,
                    int(end_year),
                    end_month_number
                )
            )

        return ranges

    # =========================================================
    # EXPERIENCE MONTH CALCULATION
    # =========================================================

    def calculate_experience_months(self):
        """
        Calculate total professional experience in months.

        Each employment period is converted into months.

        Example:

            January 2024 to August 2025
            = 20 months

            January 2022 to December 2023
            = 24 months

            January 2020 to December 2021
            = 24 months

        Total = 68 months
        """

        candidate_experience = self.candidate.experience

        ranges = self.extract_experience_ranges(
            candidate_experience
        )

        if not ranges:
            return 0

        total_months = 0

        for start_year, start_month, end_year, end_month in ranges:

            months = (
                (end_year - start_year) * 12
                + (end_month - start_month)
                + 1
            )

            if months > 0:
                total_months += months

        return total_months

    # =========================================================
    # TOTAL EXPERIENCE IN YEARS
    # =========================================================

    def calculate_total_experience_years(self):
        """
        Calculate total professional experience in years.

        Returns a decimal value.

        Example:

            68 months -> 5.67 years
        """

        total_months = self.calculate_experience_months()

        if total_months == 0:
            return 0.0

        return round(total_months / 12, 2)

    # =========================================================
    # EXPERIENCE SCORING
    # =========================================================

    def calculate_experience_score(self):
        """
        Calculate experience score based on:

        Required experience
        vs
        Candidate's total experience.
        """

        required_experience = self.job.experience

        required_years = self.extract_years(
            required_experience
        )

        if required_years <= 0:
            return 0

        candidate_years = (
            self.calculate_total_experience_years()
        )

        if candidate_years <= 0:
            return 0

        if candidate_years >= required_years:
            return 100

        score = (
            candidate_years / required_years
        ) * 100

        return round(score, 2)

    # =========================================================
    # EDUCATION SCORING
    # =========================================================

    def calculate_education_score(self):
        """
        Calculate education matching score.
        """

        candidate_education = (
            self.candidate.education.lower()
        )

        required_education = (
            self.job.education.lower()
        )

        if not candidate_education:
            return 0

        # Bachelor's degree requirement
        if "bachelor" in required_education:

            if (
                "bachelor" in candidate_education
                or "master" in candidate_education
                or "phd" in candidate_education
            ):
                return 100

            return 0

        # Master's degree requirement
        if "master" in required_education:

            if (
                "master" in candidate_education
                or "phd" in candidate_education
            ):
                return 100

            return 0

        # No specific degree requirement
        return 100

    # =========================================================
    # OVERALL ATS SCORE
    # =========================================================

    def calculate_overall_score(self):
        """
        Calculate the overall ATS score.

        Weight:

            Skills      = 60%
            Experience  = 20%
            Education   = 20%
        """

        skill_score = (
            self.calculate_skill_score()
        )

        experience_score = (
            self.calculate_experience_score()
        )

        education_score = (
            self.calculate_education_score()
        )

        overall_score = (
            skill_score * 0.60
            + experience_score * 0.20
            + education_score * 0.20
        )

        return round(overall_score, 2)

    # =========================================================
    # COMPLETE ATS REPORT
    # =========================================================

    def generate_report(self):
        """
        Generate a complete ATS matching report.
        """

        total_experience_years = (
            self.calculate_total_experience_years()
        )

        return {
            "overall_score":
                self.calculate_overall_score(),

            "skill_score":
                self.calculate_skill_score(),

            "experience_score":
                self.calculate_experience_score(),

            "education_score":
                self.calculate_education_score(),

            "total_experience_years":
                total_experience_years,

            "matched_skills":
                self.get_matched_skills(),

            "missing_skills":
                self.get_missing_skills()
        }