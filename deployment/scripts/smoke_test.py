from __future__ import annotations

import io
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "backend"))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ["APP_RUNTIME_DATA_DIR"] = tempfile.mkdtemp(prefix="attrition-smoke-")

from app.main import app


def assert_status(response, expected: int, label: str) -> None:
    if response.status_code != expected:
        raise AssertionError(
            f"{label} returned {response.status_code}: {response.text[:300]}"
        )


def check_pages(client: TestClient, employee_id: str) -> None:
    page_paths = [
        "/",
        "/predict",
        "/batch-predict",
        "/analytics",
        "/model-info",
        f"/employee/{employee_id}",
        "/app.js",
        "/health",
    ]
    for path in page_paths:
        response = client.get(path)
        assert_status(response, 200, path)


def check_json_endpoints(client: TestClient, sample_payload: dict[str, object]) -> None:
    response = client.post("/api/predict", json=sample_payload)
    assert_status(response, 200, "/api/predict")

    for path in [
        "/api/analytics/summary",
        "/api/analytics/department",
        "/api/analytics/trends",
        f"/api/employee/{int(sample_payload['EmployeeNumber'])}",
    ]:
        response = client.get(path)
        assert_status(response, 200, path)


def check_htmx_partials(client: TestClient) -> None:
    partial_paths = [
        "/api/analytics/trends?partial=1",
        "/api/analytics/department?partial=heatmap",
        "/api/analytics/top-features?partial=1",
        "/api/analytics/age-groups?partial=1",
        "/api/analytics/income-scatter?partial=1",
        "/modal/predict",
    ]
    for path in partial_paths:
        response = client.get(path, headers={"HX-Request": "true"})
        assert_status(response, 200, path)


def check_batch_routes(client: TestClient, batch_frame: pd.DataFrame) -> None:
    csv_bytes = batch_frame.to_csv(index=False).encode("utf-8")
    upload = {"file": ("sample.csv", io.BytesIO(csv_bytes), "text/csv")}

    preview = client.post(
        "/api/batch-preview",
        files=upload,
        headers={"HX-Request": "true"},
    )
    assert_status(preview, 200, "/api/batch-preview")

    upload = {"file": ("sample.csv", io.BytesIO(csv_bytes), "text/csv")}
    batch_response = client.post(
        "/api/batch-predict",
        files=upload,
        headers={"HX-Request": "true"},
    )
    assert_status(batch_response, 200, "/api/batch-predict")


def check_form_routes(client: TestClient) -> None:
    options = client.get(
        "/api/options/job-roles",
        params={"department": "Sales", "wrapper_id": "job-role-wrapper-page"},
    )
    assert_status(options, 200, "/api/options/job-roles")

    notes = client.post(
        "/api/employee/1/notes",
        data={"note": "Smoke test note", "author": "QA"},
        headers={"HX-Request": "true"},
    )
    assert_status(notes, 200, "/api/employee/{id}/notes")


def main() -> None:
    dataset = pd.read_csv("IBM-HR-Analytics-Employee-Attrition-and-Performance.csv")
    sample_payload = dataset.iloc[0].drop(labels=["Attrition"]).to_dict()
    batch_frame = dataset.head(3).drop(columns=["Attrition"])
    employee_id = str(int(sample_payload["EmployeeNumber"]))

    with TestClient(app) as client:
        check_pages(client, employee_id)
        check_json_endpoints(client, sample_payload)
        check_htmx_partials(client)
        check_batch_routes(client, batch_frame)
        check_form_routes(client)

    print("Smoke test passed: pages, APIs, HTMX partials, batch flows, and notes endpoint responded successfully.")


if __name__ == "__main__":
    main()
