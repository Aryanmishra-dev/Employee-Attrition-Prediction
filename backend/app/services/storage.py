from __future__ import annotations

import json
import re
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

BATCH_ID_PATTERN = re.compile(r"^[a-f0-9]{12}$")


def _json_default(value: Any) -> Any:
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "item"):
        return value.item()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable.")


class AppStorage:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.logs_path = self.data_dir / "prediction_logs.jsonl"
        self.notes_path = self.data_dir / "employee_notes.json"
        self.batches_dir = self.data_dir / "batches"
        self._lock = threading.Lock()
        self._ensure_files()

    def _ensure_files(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.batches_dir.mkdir(parents=True, exist_ok=True)
        if not self.logs_path.exists():
            self.logs_path.write_text("", encoding="utf-8")
        if not self.notes_path.exists():
            self.notes_path.write_text("{}", encoding="utf-8")

    def append_prediction_logs(self, entries: Iterable[dict[str, Any]]) -> None:
        lines = [
            json.dumps(entry, default=_json_default, ensure_ascii=True) for entry in entries
        ]
        if not lines:
            return
        with self._lock:
            with self.logs_path.open("a", encoding="utf-8") as handle:
                for line in lines:
                    handle.write(f"{line}\n")

    def load_prediction_logs(self) -> list[dict[str, Any]]:
        if not self.logs_path.exists():
            return []
        records: list[dict[str, Any]] = []
        with self.logs_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return records

    def load_employee_notes(self, employee_id: str) -> list[dict[str, str]]:
        payload = self._load_notes_payload()
        return payload.get(str(employee_id), [])

    def _load_notes_payload(self) -> dict[str, list[dict[str, str]]]:
        if not self.notes_path.exists():
            return {}
        with self.notes_path.open("r", encoding="utf-8") as handle:
            try:
                payload = json.load(handle)
            except json.JSONDecodeError:
                return {}
        return payload if isinstance(payload, dict) else {}

    def _write_notes_payload(self, payload: dict[str, list[dict[str, str]]]) -> None:
        temp_path = self.notes_path.with_name(
            f".{self.notes_path.name}.{uuid.uuid4().hex}.tmp"
        )
        temp_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        temp_path.replace(self.notes_path)

    def add_employee_note(
        self, employee_id: str, note: str, author: str = "HR Partner"
    ) -> list[dict[str, str]]:
        note_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "author": author,
            "note": note.strip(),
        }
        with self._lock:
            payload = self._load_notes_payload()
            payload.setdefault(str(employee_id), []).append(note_entry)
            self._write_notes_payload(payload)
        return payload[str(employee_id)]

    def save_batch_results(self, frame: pd.DataFrame) -> str:
        batch_id = uuid.uuid4().hex[:12]
        output_path = self.batches_dir / f"{batch_id}.csv"
        frame.to_csv(output_path, index=False)
        return batch_id

    def get_batch_results_path(self, batch_id: str) -> Path:
        if not BATCH_ID_PATTERN.fullmatch(batch_id):
            raise ValueError("Invalid batch identifier.")
        return self.batches_dir / f"{batch_id}.csv"
