from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.services.constants import JOB_ROLE_BY_DEPARTMENT


class EmployeePredictionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    EmployeeNumber: Annotated[int, Field(default=0, ge=0)]
    Age: Annotated[int, Field(ge=18, le=65)]
    BusinessTravel: Literal["Non-Travel", "Travel_Frequently", "Travel_Rarely"]
    DailyRate: Annotated[int, Field(default=802, ge=102, le=1499)]
    Department: Literal["Human Resources", "Research & Development", "Sales"]
    DistanceFromHome: Annotated[int, Field(ge=1, le=29)]
    Education: Annotated[int, Field(ge=1, le=5)]
    EducationField: Literal[
        "Human Resources",
        "Life Sciences",
        "Marketing",
        "Medical",
        "Other",
        "Technical Degree",
    ]
    EmployeeCount: Annotated[int, Field(default=1, ge=1, le=1)]
    EnvironmentSatisfaction: Annotated[int, Field(ge=1, le=4)]
    Gender: Literal["Female", "Male"]
    HourlyRate: Annotated[int, Field(default=66, ge=30, le=100)]
    JobInvolvement: Annotated[int, Field(ge=1, le=4)]
    JobLevel: Annotated[int, Field(ge=1, le=5)]
    JobRole: Literal[
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
    JobSatisfaction: Annotated[int, Field(ge=1, le=4)]
    MaritalStatus: Literal["Divorced", "Married", "Single"]
    MonthlyIncome: Annotated[int, Field(ge=1009, le=19999)]
    MonthlyRate: Annotated[int, Field(default=14236, ge=2094, le=26999)]
    NumCompaniesWorked: Annotated[int, Field(ge=0, le=9)]
    Over18: Literal["Y"] = "Y"
    OverTime: Literal["No", "Yes"]
    PercentSalaryHike: Annotated[int, Field(ge=11, le=25)]
    PerformanceRating: Annotated[int, Field(ge=3, le=4)]
    RelationshipSatisfaction: Annotated[int, Field(ge=1, le=4)]
    StandardHours: Annotated[int, Field(default=80, ge=80, le=80)]
    StockOptionLevel: Annotated[int, Field(ge=0, le=3)]
    TotalWorkingYears: Annotated[int, Field(ge=0, le=40)]
    TrainingTimesLastYear: Annotated[int, Field(ge=0, le=6)]
    WorkLifeBalance: Annotated[int, Field(ge=1, le=4)]
    YearsAtCompany: Annotated[int, Field(ge=0, le=40)]
    YearsInCurrentRole: Annotated[int, Field(ge=0, le=18)]
    YearsSinceLastPromotion: Annotated[int, Field(ge=0, le=15)]
    YearsWithCurrManager: Annotated[int, Field(ge=0, le=17)]

    @model_validator(mode="after")
    def validate_role_for_department(self) -> "EmployeePredictionInput":
        if self.JobRole not in JOB_ROLE_BY_DEPARTMENT[self.Department]:
            allowed = ", ".join(JOB_ROLE_BY_DEPARTMENT[self.Department])
            raise ValueError(
                f"JobRole '{self.JobRole}' is invalid for Department '{self.Department}'. "
                f"Allowed values: {allowed}."
            )
        return self


class RecommendationItem(BaseModel):
    category: Literal[
        "compensation",
        "growth",
        "wellbeing",
        "engagement",
        "environment",
    ]
    message: str
    urgency: int


class FeatureContribution(BaseModel):
    feature: str
    label: str
    value: str
    impact: float
    direction: Literal["toward_attrition", "toward_retention"]


class PredictionResponse(BaseModel):
    employee_id: str
    risk_level: Literal["Low Risk", "Medium Risk", "High Risk"]
    probability: float
    confidence: float
    binary_prediction: int
    top_features: list[FeatureContribution]
    recommendations: list[RecommendationItem]
    profile_url: str


class BatchPredictionRecord(BaseModel):
    employee_id: str
    department: str
    job_role: str
    risk_level: str
    probability: float
    confidence: float
    key_risk_factors: list[str]
    profile_url: str


class BatchPredictionResponse(BaseModel):
    batch_id: str
    total_processed: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    average_attrition_probability: float
    records: list[BatchPredictionRecord]
    download_url: str


class EmployeeNote(BaseModel):
    timestamp: str
    author: str
    note: str
