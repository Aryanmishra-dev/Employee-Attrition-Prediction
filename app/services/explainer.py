from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from app.models.schemas import FeatureContribution
from app.services.constants import DISPLAY_LABELS, humanize_value


class AttritionExplainer:
    def __init__(self, artifact: Mapping[str, Any]) -> None:
        self.importance_map = {
            item["feature"]: float(item["importance"])
            for item in artifact["feature_importances"]
        }
        self.direction_map = {
            key: float(value) for key, value in artifact["feature_directions"].items()
        }

    def _label_for_feature(self, feature_name: str) -> str:
        if feature_name in DISPLAY_LABELS:
            return DISPLAY_LABELS[feature_name]

        prefixes = (
            "BusinessTravel_",
            "Department_",
            "EducationField_",
            "JobRole_",
            "MaritalStatus_",
        )
        for prefix in prefixes:
            if feature_name.startswith(prefix):
                category = prefix.rstrip("_")
                value = feature_name.replace(prefix, "", 1)
                return f"{DISPLAY_LABELS.get(category, category)}: {humanize_value(value)}"

        return humanize_value(feature_name)

    def _display_value(self, feature_name: str, raw_row: Mapping[str, Any]) -> str:
        if feature_name in raw_row:
            return str(raw_row[feature_name])

        if "_" in feature_name:
            return humanize_value(feature_name.split("_", 1)[1])
        return "-"

    def explain_row(
        self,
        raw_row: Mapping[str, Any],
        scaled_row: pd.Series,
        top_n: int = 5,
    ) -> list[FeatureContribution]:
        contributions: list[FeatureContribution] = []

        for feature_name, scaled_value in scaled_row.items():
            importance = self.importance_map.get(feature_name, 0.0)
            direction = self.direction_map.get(feature_name, 0.0)
            if importance <= 0 or direction == 0:
                continue

            signed_impact = float(scaled_value) * direction * importance
            if abs(signed_impact) < 0.0005:
                continue

            contributions.append(
                FeatureContribution(
                    feature=feature_name,
                    label=self._label_for_feature(feature_name),
                    value=self._display_value(feature_name, raw_row),
                    impact=round(abs(signed_impact), 4),
                    direction=(
                        "toward_attrition"
                        if signed_impact >= 0
                        else "toward_retention"
                    ),
                )
            )

        contributions.sort(key=lambda item: item.impact, reverse=True)
        return contributions[:top_n]
