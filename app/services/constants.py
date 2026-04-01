from __future__ import annotations

from typing import Any, Mapping

DATASET_FILENAME = "IBM-HR-Analytics-Employee-Attrition-and-Performance.csv"

DROP_COLUMNS = ["EmployeeCount", "EmployeeNumber", "Over18", "StandardHours"]
NOMINAL_COLUMNS = [
    "BusinessTravel",
    "Department",
    "EducationField",
    "JobRole",
    "MaritalStatus",
]
BINARY_MAPPINGS = {
    "Gender": {"Male": 1, "Female": 0},
    "OverTime": {"Yes": 1, "No": 0},
}

PRIMARY_NAV = [
    {"label": "Dashboard", "path": "/", "icon": "home"},
    {"label": "Single Prediction", "path": "/predict", "icon": "sparkles"},
    {"label": "Batch Prediction", "path": "/batch-predict", "icon": "table"},
    {"label": "Analytics", "path": "/analytics", "icon": "chart"},
    {"label": "Model Info", "path": "/model-info", "icon": "shield"},
]

GENDER_OPTIONS = ["Female", "Male"]
OVERTIME_OPTIONS = ["No", "Yes"]
DEPARTMENT_OPTIONS = ["Human Resources", "Research & Development", "Sales"]
JOB_ROLE_OPTIONS = [
    "Healthcare Representative",
    "Human Resources",
    "Laboratory Technician",
    "Manager",
    "Manufacturing Director",
    "Research Director",
    "Research Scientist",
    "Sales Executive",
    "Sales Representative",
]
JOB_ROLE_BY_DEPARTMENT = {
    "Human Resources": ["Human Resources", "Manager"],
    "Research & Development": [
        "Healthcare Representative",
        "Laboratory Technician",
        "Manager",
        "Manufacturing Director",
        "Research Director",
        "Research Scientist",
    ],
    "Sales": ["Manager", "Sales Executive", "Sales Representative"],
}
EDUCATION_FIELD_OPTIONS = [
    "Human Resources",
    "Life Sciences",
    "Marketing",
    "Medical",
    "Other",
    "Technical Degree",
]
BUSINESS_TRAVEL_OPTIONS = ["Non-Travel", "Travel_Frequently", "Travel_Rarely"]
MARITAL_STATUS_OPTIONS = ["Divorced", "Married", "Single"]

VISIBLE_FORM_FIELDS = [
    "EmployeeNumber",
    "Age",
    "Gender",
    "MaritalStatus",
    "Education",
    "EducationField",
    "DistanceFromHome",
    "Department",
    "JobRole",
    "JobLevel",
    "BusinessTravel",
    "OverTime",
    "YearsAtCompany",
    "YearsInCurrentRole",
    "YearsSinceLastPromotion",
    "YearsWithCurrManager",
    "MonthlyIncome",
    "PercentSalaryHike",
    "StockOptionLevel",
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "RelationshipSatisfaction",
    "WorkLifeBalance",
    "JobInvolvement",
    "PerformanceRating",
    "TrainingTimesLastYear",
    "NumCompaniesWorked",
    "TotalWorkingYears",
]

BATCH_REQUIRED_COLUMNS = [
    field_name for field_name in VISIBLE_FORM_FIELDS if field_name != "EmployeeNumber"
]

SATISFACTION_DIMENSIONS = [
    "EnvironmentSatisfaction",
    "JobSatisfaction",
    "RelationshipSatisfaction",
    "WorkLifeBalance",
    "JobInvolvement",
]

PROFILE_INFO_FIELDS = [
    ("EmployeeNumber", "Employee ID"),
    ("Department", "Department"),
    ("JobRole", "Job Role"),
    ("JobLevel", "Job Level"),
    ("BusinessTravel", "Business Travel"),
    ("YearsAtCompany", "Years at Company"),
    ("YearsInCurrentRole", "Years in Current Role"),
    ("OverTime", "Overtime"),
]

DISPLAY_LABELS = {
    "Age": "Age",
    "BusinessTravel": "Business Travel",
    "DailyRate": "Daily Rate",
    "Department": "Department",
    "DistanceFromHome": "Distance From Home",
    "Education": "Education",
    "EducationField": "Education Field",
    "EmployeeNumber": "Employee ID",
    "EnvironmentSatisfaction": "Environment Satisfaction",
    "Gender": "Gender",
    "HourlyRate": "Hourly Rate",
    "JobInvolvement": "Job Involvement",
    "JobLevel": "Job Level",
    "JobRole": "Job Role",
    "JobSatisfaction": "Job Satisfaction",
    "MaritalStatus": "Marital Status",
    "MonthlyIncome": "Monthly Income",
    "MonthlyRate": "Monthly Rate",
    "NumCompaniesWorked": "Companies Worked",
    "OverTime": "Overtime",
    "PercentSalaryHike": "Salary Hike %",
    "PerformanceRating": "Performance Rating",
    "RelationshipSatisfaction": "Relationship Satisfaction",
    "StockOptionLevel": "Stock Option Level",
    "TotalWorkingYears": "Total Working Years",
    "TrainingTimesLastYear": "Training Times Last Year",
    "WorkLifeBalance": "Work-Life Balance",
    "YearsAtCompany": "Years at Company",
    "YearsInCurrentRole": "Years in Current Role",
    "YearsSinceLastPromotion": "Years Since Last Promotion",
    "YearsWithCurrManager": "Years With Current Manager",
    "IncomePerYear": "Income Per Year of Experience",
    "PromotionLag": "Promotion Lag",
    "TenureRatio": "Role Tenure Ratio",
    "SatisfactionScore": "Satisfaction Score",
    "IsOverworked": "Overwork Signal",
    "ExperienceLevel": "Experience Level",
}


def humanize_value(value: str) -> str:
    return value.replace("_", " ")


def select_options(values: list[str]) -> list[dict[str, str]]:
    return [{"value": value, "label": humanize_value(value)} for value in values]


def get_job_role_options(department: str | None) -> list[str]:
    if department and department in JOB_ROLE_BY_DEPARTMENT:
        return JOB_ROLE_BY_DEPARTMENT[department]
    return JOB_ROLE_OPTIONS


def build_form_sections(
    defaults: Mapping[str, Any],
    department: str | None = None,
    selected_job_role: str | None = None,
) -> list[dict[str, Any]]:
    active_department = str(department or defaults.get("Department") or DEPARTMENT_OPTIONS[1])
    job_roles = get_job_role_options(active_department)
    active_job_role = (
        selected_job_role
        if selected_job_role in job_roles
        else str(defaults.get("JobRole") or job_roles[0])
    )

    def number_field(
        name: str,
        label: str,
        minimum: int,
        maximum: int,
        required: bool = True,
        helper: str = "",
    ) -> dict[str, Any]:
        return {
            "name": name,
            "label": label,
            "type": "number",
            "required": required,
            "min": minimum,
            "max": maximum,
            "step": 1,
            "value": defaults.get(name, ""),
            "helper": helper,
        }

    def select_field(
        name: str,
        label: str,
        options: list[str],
        value: str,
        required: bool = True,
    ) -> dict[str, Any]:
        return {
            "name": name,
            "label": label,
            "type": "select",
            "required": required,
            "options": select_options(options),
            "value": value,
        }

    return [
        {
            "title": "Section A - Personal Demographics",
            "description": "Core employee context captured before reviewing job factors.",
            "fields": [
                {
                    "name": "EmployeeNumber",
                    "label": "Employee ID",
                    "type": "number",
                    "required": False,
                    "min": 1,
                    "max": 999999,
                    "step": 1,
                    "value": defaults.get("EmployeeNumber", ""),
                    "helper": "Optional. Leave blank to generate a profile identifier automatically.",
                },
                number_field("Age", "Age", 18, 65),
                select_field(
                    "Gender",
                    "Gender",
                    GENDER_OPTIONS,
                    str(defaults.get("Gender", GENDER_OPTIONS[0])),
                ),
                select_field(
                    "MaritalStatus",
                    "Marital Status",
                    MARITAL_STATUS_OPTIONS,
                    str(defaults.get("MaritalStatus", MARITAL_STATUS_OPTIONS[0])),
                ),
                number_field("Education", "Education", 1, 5),
                select_field(
                    "EducationField",
                    "Education Field",
                    EDUCATION_FIELD_OPTIONS,
                    str(defaults.get("EducationField", EDUCATION_FIELD_OPTIONS[1])),
                ),
                number_field("DistanceFromHome", "Distance From Home", 1, 29),
            ],
        },
        {
            "title": "Section B - Job Details",
            "description": "Role structure, travel requirements, and tenure indicators.",
            "fields": [
                select_field(
                    "Department",
                    "Department",
                    DEPARTMENT_OPTIONS,
                    active_department,
                ),
                select_field("JobRole", "Job Role", job_roles, active_job_role),
                number_field("JobLevel", "Job Level", 1, 5),
                select_field(
                    "BusinessTravel",
                    "Business Travel",
                    BUSINESS_TRAVEL_OPTIONS,
                    str(defaults.get("BusinessTravel", BUSINESS_TRAVEL_OPTIONS[2])),
                ),
                select_field(
                    "OverTime",
                    "Overtime",
                    OVERTIME_OPTIONS,
                    str(defaults.get("OverTime", OVERTIME_OPTIONS[0])),
                ),
                number_field("YearsAtCompany", "Years At Company", 0, 40),
                number_field("YearsInCurrentRole", "Years In Current Role", 0, 18),
                number_field(
                    "YearsSinceLastPromotion", "Years Since Last Promotion", 0, 15
                ),
                number_field("YearsWithCurrManager", "Years With Current Manager", 0, 17),
            ],
        },
        {
            "title": "Section C - Compensation & Satisfaction",
            "description": "Signals tied to pay progression, sentiment, and reward structure.",
            "fields": [
                number_field("MonthlyIncome", "Monthly Income", 1009, 19999),
                number_field("PercentSalaryHike", "Percent Salary Hike", 11, 25),
                number_field("StockOptionLevel", "Stock Option Level", 0, 3),
                number_field("JobSatisfaction", "Job Satisfaction", 1, 4),
                number_field(
                    "EnvironmentSatisfaction", "Environment Satisfaction", 1, 4
                ),
                number_field(
                    "RelationshipSatisfaction", "Relationship Satisfaction", 1, 4
                ),
                number_field("WorkLifeBalance", "Work-Life Balance", 1, 4),
            ],
        },
        {
            "title": "Section D - Performance & Engagement",
            "description": "Recent performance signals and long-term career trajectory.",
            "fields": [
                number_field("JobInvolvement", "Job Involvement", 1, 4),
                number_field("PerformanceRating", "Performance Rating", 3, 4),
                number_field("TrainingTimesLastYear", "Training Times Last Year", 0, 6),
                number_field("NumCompaniesWorked", "Number of Companies Worked", 0, 9),
                number_field("TotalWorkingYears", "Total Working Years", 0, 40),
            ],
        },
    ]
