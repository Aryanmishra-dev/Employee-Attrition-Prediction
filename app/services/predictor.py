from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Mapping

import joblib
import numpy as np
import pandas as pd

from app.services.constants import BINARY_MAPPINGS, DISPLAY_LABELS, DROP_COLUMNS, NOMINAL_COLUMNS


def engineer_features(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.copy()
    enriched["IncomePerYear"] = enriched["MonthlyIncome"] / (
        enriched["TotalWorkingYears"] + 1
    )
    enriched["PromotionLag"] = (
        enriched["YearsAtCompany"] - enriched["YearsSinceLastPromotion"]
    )
    enriched["TenureRatio"] = enriched["YearsInCurrentRole"] / (
        enriched["YearsAtCompany"] + 1
    )
    enriched["SatisfactionScore"] = (
        enriched["JobSatisfaction"]
        + enriched["EnvironmentSatisfaction"]
        + enriched["WorkLifeBalance"]
    ) / 3
    enriched["IsOverworked"] = (
        (enriched["OverTime"] == 1) & (enriched["WorkLifeBalance"] <= 2)
    ).astype(int)
    enriched["ExperienceLevel"] = pd.cut(
        enriched["TotalWorkingYears"],
        bins=[0, 2, 5, 10, 20, 50],
        labels=[0, 1, 2, 3, 4],
        include_lowest=True,
    ).astype(int)
    return enriched


def build_model_frame(
    raw_frame: pd.DataFrame,
    drop_columns: list[str] | None = None,
    nominal_columns: list[str] | None = None,
    binary_mappings: Mapping[str, Mapping[str, int]] | None = None,
) -> pd.DataFrame:
    drop_columns = drop_columns or DROP_COLUMNS
    nominal_columns = nominal_columns or NOMINAL_COLUMNS
    binary_mappings = binary_mappings or BINARY_MAPPINGS

    frame = raw_frame.copy()
    if "Attrition" in frame.columns and frame["Attrition"].dtype == object:
        frame["Attrition"] = frame["Attrition"].map({"Yes": 1, "No": 0})

    frame = frame.drop(columns=drop_columns, errors="ignore")
    for column_name, mapping in binary_mappings.items():
        if column_name in frame.columns and frame[column_name].dtype == object:
            frame[column_name] = frame[column_name].map(mapping)

    available_nominal_columns = [
        column_name for column_name in nominal_columns if column_name in frame.columns
    ]
    frame = pd.get_dummies(
        frame, columns=available_nominal_columns, drop_first=True, dtype=int
    )
    frame = engineer_features(frame)
    return frame


def ensure_raw_input_frame(
    frame: pd.DataFrame,
    raw_input_columns: list[str],
    defaults: Mapping[str, Any],
) -> pd.DataFrame:
    normalized = frame.copy()
    for column_name in raw_input_columns:
        if column_name not in normalized.columns:
            normalized[column_name] = defaults.get(column_name)
        normalized[column_name] = normalized[column_name].replace("", np.nan)
        normalized[column_name] = normalized[column_name].fillna(defaults.get(column_name))
    return normalized[raw_input_columns]


class AttritionPredictor:
    def __init__(self, artifact_path: Path) -> None:
        if not artifact_path.exists():
            raise FileNotFoundError(
                f"Model artifact not found at {artifact_path}. Run scripts/train_model.py first."
            )

        self.artifact = joblib.load(artifact_path)
        self.raw_input_columns: list[str] = self.artifact["raw_input_columns"]
        self.feature_columns: list[str] = self.artifact["feature_columns"]
        self.scaler = self.artifact["scaler"]
        self.models: dict[str, Any] = self.artifact["models"]
        self.model_weights: dict[str, float] = self.artifact["model_weights"]
        self.defaults: dict[str, Any] = self.artifact["defaults"]
        self.feature_importances = self.artifact["feature_importances"]
        self.feature_directions: dict[str, float] = self.artifact["feature_directions"]
        self.department_income_medians = self.artifact["department_income_medians"]
        self.dataset_overview = self.artifact["dataset_overview"]
        self.metrics = self.artifact["metrics"]
        self.confusion_matrix = self.artifact["confusion_matrix"]
        self.training_notes = self.artifact["training_notes"]
        self.model_summary = self.artifact["model_summary"]
        self.classification_threshold = float(self.artifact["classification_threshold"])
        self.medium_risk_threshold = float(
            os.getenv("MEDIUM_RISK_THRESHOLD", self.artifact.get("medium_risk_threshold", 0.35))
        )
        self.high_risk_threshold = float(
            os.getenv("HIGH_RISK_THRESHOLD", self.artifact.get("high_risk_threshold", 0.65))
        )

    def get_form_defaults(self) -> dict[str, Any]:
        defaults = {
            key: value
            for key, value in self.defaults.items()
            if key in DISPLAY_LABELS or key == "EmployeeNumber"
        }
        defaults["EmployeeNumber"] = ""
        return defaults

    def hash_payload(self, payload: Mapping[str, Any]) -> str:
        serialized = "|".join(f"{key}={payload[key]}" for key in sorted(payload.keys()))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def risk_level(self, probability: float) -> str:
        if probability >= self.high_risk_threshold:
            return "High Risk"
        if probability >= self.medium_risk_threshold:
            return "Medium Risk"
        return "Low Risk"

    @staticmethod
    def confidence_score(probability: float) -> float:
        return max(probability, 1 - probability)

    def vectorize_records(
        self, records: list[dict[str, Any]] | pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        raw_frame = records.copy() if isinstance(records, pd.DataFrame) else pd.DataFrame(records)
        raw_frame = ensure_raw_input_frame(raw_frame, self.raw_input_columns, self.defaults)
        model_frame = build_model_frame(raw_frame)
        feature_frame = model_frame.reindex(columns=self.feature_columns, fill_value=0)
        
        # Manual Standard Scaling
        mean = np.array(self.scaler["mean"])
        scale = np.array(self.scaler["scale"])
        scaled_values = (feature_frame.values - mean) / scale
        
        scaled_frame = pd.DataFrame(
            scaled_values, columns=self.feature_columns, index=feature_frame.index
        )
        return raw_frame, feature_frame.astype(float), scaled_frame

    @staticmethod
    def _predict_probability(model: dict[str, list[float]], feature_frame: pd.DataFrame) -> np.ndarray:
        coef = np.array(model["coef"])
        intercept = model["intercept"]
        decision_scores = np.dot(feature_frame.values, coef) + intercept
        return 1.0 / (1.0 + np.exp(-decision_scores))

    def predict_records(
        self, records: list[dict[str, Any]] | pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        raw_frame, feature_frame, scaled_frame = self.vectorize_records(records)
        total_weight = sum(self.model_weights.values())
        blended_probability = np.zeros(len(scaled_frame), dtype=float)
        for model_name, model in self.models.items():
            model_probability = self._predict_probability(model, scaled_frame)
            blended_probability += self.model_weights.get(model_name, 0.0) * model_probability

        blended_probability = blended_probability / max(total_weight, 1e-9)

        result_frame = pd.DataFrame(index=raw_frame.index)
        result_frame["probability"] = blended_probability
        result_frame["confidence"] = result_frame["probability"].map(self.confidence_score)
        result_frame["risk_level"] = result_frame["probability"].map(self.risk_level)
        result_frame["binary_prediction"] = (
            result_frame["probability"] >= self.classification_threshold
        ).astype(int)
        return result_frame, raw_frame, scaled_frame
