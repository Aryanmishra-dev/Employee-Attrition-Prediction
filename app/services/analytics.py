from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.models.schemas import PredictionResponse
from app.services.constants import PROFILE_INFO_FIELDS, SATISFACTION_DIMENSIONS
from app.services.explainer import AttritionExplainer
from app.services.predictor import AttritionPredictor
from app.services.recommender import RecommendationEngine
from app.services.storage import AppStorage


class AnalyticsService:
    def __init__(
        self,
        dataset_path: Path,
        predictor: AttritionPredictor,
        explainer: AttritionExplainer,
        recommender: RecommendationEngine,
        storage: AppStorage,
    ) -> None:
        self.dataset_path = dataset_path
        self.predictor = predictor
        self.explainer = explainer
        self.recommender = recommender
        self.storage = storage
        self.refresh()

    def refresh(self) -> None:
        self.dataset = pd.read_csv(self.dataset_path)
        baseline_inputs = self.dataset.drop(columns=["Attrition"])
        prediction_frame, raw_frame, _scaled_frame = self.predictor.predict_records(
            baseline_inputs
        )
        self.bootstrap_timestamp = datetime.now(UTC).isoformat()
        self.baseline_predictions = raw_frame.copy()
        self.baseline_predictions["probability"] = prediction_frame["probability"]
        self.baseline_predictions["confidence"] = prediction_frame["confidence"]
        self.baseline_predictions["risk_level"] = prediction_frame["risk_level"]
        self.baseline_predictions["binary_prediction"] = prediction_frame["binary_prediction"]
        self.baseline_predictions["prediction_timestamp"] = self.bootstrap_timestamp
        self.baseline_predictions["source"] = "baseline"
        self.baseline_predictions["employee_id"] = (
            self.baseline_predictions["EmployeeNumber"].fillna(0).astype(int).astype(str)
        )
        self.baseline_predictions["ActualAttrition"] = self.dataset["Attrition"].map(
            {"Yes": 1, "No": 0}
        )
        self.company_average_satisfaction = {
            field_name: round(float(self.dataset[field_name].mean()), 2)
            for field_name in SATISFACTION_DIMENSIONS
        }

    def _flatten_logs(self) -> pd.DataFrame:
        log_records = self.storage.load_prediction_logs()
        if not log_records:
            return pd.DataFrame()

        rows: list[dict[str, Any]] = []
        for entry in log_records:
            output = entry.get("output", {})
            raw_input = entry.get("raw_input", {})
            rows.append(
                {
                    "employee_id": str(output.get("employee_id", raw_input.get("EmployeeNumber", ""))),
                    "Department": raw_input.get("Department"),
                    "JobRole": raw_input.get("JobRole"),
                    "Age": raw_input.get("Age"),
                    "MonthlyIncome": raw_input.get("MonthlyIncome"),
                    "probability": output.get("probability"),
                    "confidence": output.get("confidence"),
                    "risk_level": output.get("risk_level"),
                    "prediction_timestamp": entry.get("timestamp"),
                    "source": entry.get("source", "single"),
                    "key_risk_factors": ", ".join(
                        item["label"] for item in output.get("top_features", [])[:3]
                    ),
                }
            )

        return pd.DataFrame(rows)

    def combined_predictions(self) -> pd.DataFrame:
        baseline = self.baseline_predictions[
            [
                "employee_id",
                "Department",
                "JobRole",
                "Age",
                "MonthlyIncome",
                "probability",
                "confidence",
                "risk_level",
                "prediction_timestamp",
                "source",
            ]
        ].copy()
        baseline["key_risk_factors"] = ""
        logs = self._flatten_logs()
        if logs.empty:
            return baseline
        return pd.concat([baseline, logs], ignore_index=True, sort=False)

    def get_dashboard_context(self) -> dict[str, Any]:
        combined = self.combined_predictions()
        summary = {
            "total_employees": int(len(combined)),
            "high_risk_count": int((combined["risk_level"] == "High Risk").sum()),
            "medium_risk_count": int((combined["risk_level"] == "Medium Risk").sum()),
            "retention_rate": round((1 - combined["probability"].mean()) * 100, 1),
        }

        risk_distribution = {
            "labels": ["Low Risk", "Medium Risk", "High Risk"],
            "values": [
                int((combined["risk_level"] == "Low Risk").sum()),
                int((combined["risk_level"] == "Medium Risk").sum()),
                int((combined["risk_level"] == "High Risk").sum()),
            ],
        }

        department_chart = (
            combined.groupby("Department", dropna=False)["probability"]
            .mean()
            .mul(100)
            .round(1)
            .reset_index()
        )

        logs = self._flatten_logs()
        if logs.empty:
            recent = self.baseline_predictions.sort_values(
                by="probability", ascending=False
            ).head(10)
            recent_rows = [
                {
                    "employee_id": row["employee_id"],
                    "department": row["Department"],
                    "job_role": row["JobRole"],
                    "risk_level": row["risk_level"],
                    "confidence": round(float(row["confidence"]) * 100, 1),
                }
                for _, row in recent.iterrows()
            ]
        else:
            recent = logs.sort_values("prediction_timestamp", ascending=False).head(10)
            recent_rows = [
                {
                    "employee_id": row["employee_id"],
                    "department": row["Department"],
                    "job_role": row["JobRole"],
                    "risk_level": row["risk_level"],
                    "confidence": round(float(row["confidence"]) * 100, 1),
                }
                for _, row in recent.iterrows()
            ]

        return {
            "summary_stats": summary,
            "risk_distribution": risk_distribution,
            "department_chart": {
                "labels": department_chart["Department"].fillna("Unknown").tolist(),
                "values": department_chart["probability"].tolist(),
            },
            "recent_predictions": recent_rows,
        }

    def get_summary_payload(self) -> dict[str, Any]:
        return self.get_dashboard_context()["summary_stats"]

    def get_department_payload(self) -> dict[str, Any]:
        combined = self.combined_predictions()
        grouped = (
            combined.groupby(["Department", "risk_level"]).size().unstack(fill_value=0)
        )
        rows = []
        for department_name in grouped.index.tolist():
            row = grouped.loc[department_name]
            rows.append(
                {
                    "department": department_name,
                    "low_risk": int(row.get("Low Risk", 0)),
                    "medium_risk": int(row.get("Medium Risk", 0)),
                    "high_risk": int(row.get("High Risk", 0)),
                }
            )
        return {"departments": rows}

    def get_trends_payload(self) -> dict[str, Any]:
        logs = self._flatten_logs()
        if logs.empty:
            return {
                "labels": [datetime.now(UTC).strftime("%Y-%m-%d")],
                "probability": [
                    round(float(self.baseline_predictions["probability"].mean() * 100), 1)
                ],
                "volume": [int(len(self.baseline_predictions))],
            }

        logs["prediction_date"] = pd.to_datetime(logs["prediction_timestamp"]).dt.date
        grouped = (
            logs.groupby("prediction_date")
            .agg(probability=("probability", "mean"), volume=("employee_id", "count"))
            .reset_index()
        )
        return {
            "labels": [str(value) for value in grouped["prediction_date"].tolist()],
            "probability": [round(float(value * 100), 1) for value in grouped["probability"]],
            "volume": grouped["volume"].astype(int).tolist(),
        }

    def get_top_features_payload(self, limit: int = 10) -> dict[str, Any]:
        feature_rows = self.predictor.feature_importances[:limit]
        return {
            "labels": [self.explainer._label_for_feature(item["feature"]) for item in feature_rows],
            "values": [round(float(item["importance"]) * 100, 2) for item in feature_rows],
        }

    def get_age_groups_payload(self) -> dict[str, Any]:
        frame = self.baseline_predictions.copy()
        frame["Age Group"] = pd.cut(
            frame["Age"],
            bins=[17, 25, 35, 45, 60],
            labels=["18-25", "26-35", "36-45", "46-60"],
        )
        grouped = (
            frame.groupby("Age Group", observed=True)
            .agg(
                predicted_probability=("probability", "mean"),
                actual_attrition_rate=("ActualAttrition", "mean"),
            )
            .reset_index()
        )
        return {
            "labels": grouped["Age Group"].astype(str).tolist(),
            "predicted": [
                round(float(value * 100), 1)
                for value in grouped["predicted_probability"].tolist()
            ],
            "actual": [
                round(float(value * 100), 1)
                for value in grouped["actual_attrition_rate"].tolist()
            ],
        }

    def get_income_scatter_payload(self, sample_size: int = 220) -> dict[str, Any]:
        frame = self.combined_predictions().copy()
        if len(frame) > sample_size:
            frame = frame.sample(sample_size, random_state=42)

        grouped_points: dict[str, list[dict[str, Any]]] = {
            "Low Risk": [],
            "Medium Risk": [],
            "High Risk": [],
        }
        for _, row in frame.iterrows():
            grouped_points[row["risk_level"]].append(
                {
                    "x": float(row["MonthlyIncome"]),
                    "y": round(float(row["probability"] * 100), 2),
                    "employee_id": row["employee_id"],
                }
            )

        return {"datasets": grouped_points}

    def get_heatmap_payload(self) -> dict[str, Any]:
        grouped = (
            self.baseline_predictions.groupby(["Department", "risk_level"])
            .size()
            .unstack(fill_value=0)
            .reindex(columns=["Low Risk", "Medium Risk", "High Risk"], fill_value=0)
        )
        max_value = max(int(grouped.max().max()), 1)
        risk_palette = {
            "Low Risk": ("16, 185, 129"),
            "Medium Risk": ("245, 158, 11"),
            "High Risk": ("244, 63, 94"),
        }
        rows = []
        for department_name in grouped.index.tolist():
            cells = []
            for risk_level in grouped.columns.tolist():
                value = int(grouped.loc[department_name, risk_level])
                alpha = round(0.15 + (value / max_value) * 0.7, 2)
                cells.append(
                    {
                        "label": risk_level,
                        "value": value,
                        "style": f"background-color: rgba({risk_palette[risk_level]}, {alpha});",
                    }
                )
            rows.append({"department": department_name, "cells": cells})
        return {"rows": rows, "columns": grouped.columns.tolist()}

    def get_model_info_context(self) -> dict[str, Any]:
        feature_rows = [
            {
                "feature": item["feature"],
                "importance": item["importance"],
                "label": self.explainer._label_for_feature(item["feature"]),
            }
            for item in self.predictor.feature_importances[:20]
        ]
        return {
            "model_summary": self.predictor.model_summary,
            "metrics": self.predictor.metrics,
            "confusion_matrix": self.predictor.confusion_matrix,
            "feature_importances": feature_rows,
            "dataset_overview": self.predictor.dataset_overview,
            "training_notes": self.predictor.training_notes,
            "classification_threshold": self.predictor.classification_threshold,
            "medium_risk_threshold": self.predictor.medium_risk_threshold,
            "high_risk_threshold": self.predictor.high_risk_threshold,
            "explainer": self.explainer,
        }

    def get_employee_profile(self, employee_id: str) -> dict[str, Any] | None:
        log_records = self.storage.load_prediction_logs()
        matching_logs = [
            entry
            for entry in log_records
            if str(entry.get("output", {}).get("employee_id")) == str(employee_id)
        ]
        if matching_logs:
            source_record = matching_logs[-1]["raw_input"]
        else:
            match = self.dataset[
                self.dataset["EmployeeNumber"].astype(str) == str(employee_id)
            ]
            if match.empty:
                return None
            source_record = match.iloc[0].drop(labels=["Attrition"]).to_dict()

        prediction_frame, raw_frame, scaled_frame = self.predictor.predict_records(
            [source_record]
        )
        raw_record = raw_frame.iloc[0].to_dict()
        explanation = self.explainer.explain_row(raw_record, scaled_frame.iloc[0], top_n=8)
        response = PredictionResponse(
            employee_id=str(
                int(raw_record["EmployeeNumber"]) if raw_record["EmployeeNumber"] else employee_id
            ),
            risk_level=prediction_frame.iloc[0]["risk_level"],
            probability=float(prediction_frame.iloc[0]["probability"]),
            confidence=float(prediction_frame.iloc[0]["confidence"]),
            binary_prediction=int(prediction_frame.iloc[0]["binary_prediction"]),
            top_features=explanation[:5],
            recommendations=self.recommender.recommend(
                raw_record, prediction_frame.iloc[0]["risk_level"]
            ),
            profile_url=f"/employee/{employee_id}",
        )

        return {
            "employee": {
                "employee_id": response.employee_id,
                "details": [
                    {
                        "label": label,
                        "value": raw_record.get(field_name, "-"),
                    }
                    for field_name, label in PROFILE_INFO_FIELDS
                ],
            },
            "prediction": response,
            "contributions": explanation,
            "contribution_payload": [
                {
                    "label": item.label,
                    "signed_impact": round(
                        item.impact if item.direction == "toward_attrition" else -item.impact,
                        4,
                    ),
                }
                for item in explanation
            ],
            "radar": {
                "labels": [
                    "Environment",
                    "Job Satisfaction",
                    "Relationships",
                    "Work-Life Balance",
                    "Involvement",
                ],
                "employee_values": [
                    float(raw_record["EnvironmentSatisfaction"]),
                    float(raw_record["JobSatisfaction"]),
                    float(raw_record["RelationshipSatisfaction"]),
                    float(raw_record["WorkLifeBalance"]),
                    float(raw_record["JobInvolvement"]),
                ],
                "company_values": [
                    self.company_average_satisfaction["EnvironmentSatisfaction"],
                    self.company_average_satisfaction["JobSatisfaction"],
                    self.company_average_satisfaction["RelationshipSatisfaction"],
                    self.company_average_satisfaction["WorkLifeBalance"],
                    self.company_average_satisfaction["JobInvolvement"],
                ],
            },
            "notes": self.storage.load_employee_notes(str(employee_id)),
        }
