from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _optional_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _bool_env(name: str, default: bool) -> bool:
    value = _optional_env(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    value = _optional_env(name)
    if value is None:
        return default
    return int(value)


def _float_env(name: str, default: float) -> float:
    value = _optional_env(name)
    if value is None:
        return default
    return float(value)


def _csv_env(name: str, default: list[str]) -> list[str]:
    value = _optional_env(name)
    if value is None:
        return default
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or default


def _resolve_path(root_dir: Path, raw_path: str | None, default: Path) -> Path:
    if raw_path is None:
        return default
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = root_dir / path
    return path


@dataclass(frozen=True)
class Settings:
    root_dir: Path
    app_dir: Path
    model_path: Path
    public_dir: Path
    dataset_path: Path
    data_dir: Path
    medium_risk_threshold: float
    high_risk_threshold: float
    max_upload_bytes: int
    max_batch_rows: int
    max_note_chars: int
    store_raw_prediction_inputs: bool
    allowed_hosts: list[str]
    allowed_origins: list[str]
    auth_token: str | None
    auth_username: str | None
    auth_password: str | None
    docs_enabled: bool

    @property
    def auth_enabled(self) -> bool:
        return bool(self.auth_token or (self.auth_username and self.auth_password))

    @classmethod
    def from_env(cls) -> "Settings":
        root_dir = Path(__file__).resolve().parents[3]
        app_dir = root_dir / "app"
        medium_risk_threshold = _float_env("MEDIUM_RISK_THRESHOLD", 0.35)
        high_risk_threshold = _float_env("HIGH_RISK_THRESHOLD", 0.65)

        if not 0 <= medium_risk_threshold <= high_risk_threshold <= 1:
            raise ValueError(
                "Risk thresholds must satisfy "
                "0 <= MEDIUM_RISK_THRESHOLD <= HIGH_RISK_THRESHOLD <= 1."
            )

        return cls(
            root_dir=root_dir,
            app_dir=app_dir,
            model_path=root_dir / "ml" / "models" / "model.pkl",
            public_dir=root_dir / "frontend" / "public",
            dataset_path=root_dir
            / "IBM-HR-Analytics-Employee-Attrition-and-Performance.csv",
            data_dir=_resolve_path(
                root_dir,
                _optional_env("APP_RUNTIME_DATA_DIR"),
                app_dir / "data",
            ),
            medium_risk_threshold=medium_risk_threshold,
            high_risk_threshold=high_risk_threshold,
            max_upload_bytes=_int_env("APP_MAX_UPLOAD_BYTES", 2_000_000),
            max_batch_rows=_int_env("APP_MAX_BATCH_ROWS", 5_000),
            max_note_chars=_int_env("APP_MAX_NOTE_CHARS", 2_000),
            store_raw_prediction_inputs=_bool_env("APP_STORE_RAW_PREDICTION_INPUTS", True),
            allowed_hosts=_csv_env("APP_ALLOWED_HOSTS", ["*"]),
            allowed_origins=_csv_env("APP_ALLOWED_ORIGINS", []),
            auth_token=_optional_env("APP_AUTH_TOKEN"),
            auth_username=_optional_env("APP_AUTH_USERNAME"),
            auth_password=_optional_env("APP_AUTH_PASSWORD"),
            docs_enabled=_bool_env("APP_ENABLE_DOCS", True),
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
