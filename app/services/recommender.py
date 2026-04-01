from __future__ import annotations

from typing import Any, Mapping

from app.models.schemas import RecommendationItem


class RecommendationEngine:
    def __init__(self, department_income_medians: Mapping[str, float]) -> None:
        self.department_income_medians = department_income_medians

    def recommend(
        self, employee_record: Mapping[str, Any], risk_level: str
    ) -> list[RecommendationItem]:
        recommendations: list[tuple[int, str, str]] = []

        def add(priority: int, category: str, message: str) -> None:
            recommendations.append((priority, category, message))

        department = str(employee_record.get("Department", ""))
        department_median = float(self.department_income_medians.get(department, 0))

        if (
            str(employee_record.get("OverTime")) == "Yes"
            and int(employee_record.get("WorkLifeBalance", 3)) <= 2
        ):
            add(
                1,
                "wellbeing",
                "Immediate workload audit; consider overtime compensation review",
            )

        if (
            int(employee_record.get("YearsSinceLastPromotion", 0)) >= 4
            and int(employee_record.get("JobSatisfaction", 3)) <= 2
        ):
            add(
                2,
                "growth",
                "Schedule career development conversation; review promotion pipeline",
            )

        if (
            int(employee_record.get("MonthlyIncome", 0)) < department_median
            and int(employee_record.get("PercentSalaryHike", 0)) < 12
        ):
            add(
                3,
                "compensation",
                "Compensation benchmarking needed; flag for next review cycle",
            )

        if int(employee_record.get("EnvironmentSatisfaction", 3)) <= 2:
            add(
                4,
                "environment",
                "Conduct environment satisfaction survey; review team dynamics",
            )

        if (
            int(employee_record.get("NumCompaniesWorked", 0)) >= 5
            and int(employee_record.get("YearsAtCompany", 0)) <= 2
        ):
            add(
                5,
                "engagement",
                "Assign onboarding mentor; increase early engagement touchpoints",
            )

        if int(employee_record.get("TrainingTimesLastYear", 1)) == 0:
            add(
                6,
                "growth",
                "Enroll in at least one development program this quarter",
            )

        if risk_level == "High Risk":
            add(
                7,
                "engagement",
                "Schedule 1-on-1 check-in with direct manager within 30 days",
            )
        elif not recommendations and risk_level == "Medium Risk":
            add(
                8,
                "engagement",
                "Plan a retention-focused check-in this month and review near-term support needs",
            )
        elif not recommendations:
            add(
                9,
                "engagement",
                "Maintain current engagement rhythm and review retention signals quarterly",
            )

        recommendations.sort(key=lambda item: item[0])
        return [
            RecommendationItem(category=category, message=message, urgency=priority)
            for priority, category, message in recommendations
        ]
