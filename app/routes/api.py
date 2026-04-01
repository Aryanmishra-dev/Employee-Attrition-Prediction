from __future__ import annotations

import io
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.models.schemas import (
    BatchPredictionRecord,
    BatchPredictionResponse,
    EmployeePredictionInput,
    PredictionResponse,
)
from app.services.constants import BATCH_REQUIRED_COLUMNS, build_form_sections, get_job_role_options

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parents[1] / "templates")
)


def is_htmx(request: Request) -> bool:
    return request.headers.get("HX-Request", "false").lower() == "true"


def error_response(status_code: int, error: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "detail": detail},
    )


def compact_validation_error(exc: ValidationError) -> str:
    chunks = []
    for item in exc.errors():
        field_path = ".".join(str(part) for part in item["loc"])
        chunks.append(f"{field_path}: {item['msg']}")
    return "; ".join(chunks)


def clean_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in payload.items():
        if value == "":
            continue
        normalized[key] = value
    return normalized


def build_prediction_entry(
    predictor_output: PredictionResponse,
    raw_input: dict[str, Any],
    source: str,
    input_hash: str,
) -> dict[str, Any]:
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "source": source,
        "input_hash": input_hash,
        "raw_input": raw_input,
        "output": predictor_output.model_dump(mode="json"),
    }


async def parse_single_prediction_payload(request: Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        payload = await request.json()
    else:
        form_data = await request.form()
        payload = dict(form_data)
    return clean_payload(payload)


def preview_frame_from_upload(csv_file: UploadFile) -> pd.DataFrame:
    if not csv_file.filename or not csv_file.filename.lower().endswith(".csv"):
        raise ValueError("Only .csv uploads are supported for batch prediction.")

    file_bytes = csv_file.file.read()
    csv_file.file.seek(0)
    return pd.read_csv(io.BytesIO(file_bytes))


def validate_batch_columns(frame: pd.DataFrame) -> list[str]:
    return [column_name for column_name in BATCH_REQUIRED_COLUMNS if column_name not in frame.columns]


@router.post("/predict", response_model=None)
async def predict_employee(request: Request) -> HTMLResponse | JSONResponse:
    payload = await parse_single_prediction_payload(request)
    try:
        employee = EmployeePredictionInput.model_validate(payload)
    except ValidationError as exc:
        return error_response(422, "Validation Error", compact_validation_error(exc))

    predictor = request.app.state.predictor
    explainer = request.app.state.explainer
    recommender = request.app.state.recommender
    storage = request.app.state.storage

    employee_payload = employee.model_dump()
    result_frame, raw_frame, scaled_frame = predictor.predict_records([employee_payload])
    raw_record = raw_frame.iloc[0].to_dict()
    contributions = explainer.explain_row(raw_record, scaled_frame.iloc[0], top_n=5)
    recommendations = recommender.recommend(raw_record, result_frame.iloc[0]["risk_level"])

    employee_id = (
        str(int(raw_record["EmployeeNumber"]))
        if int(raw_record["EmployeeNumber"]) > 0
        else predictor.hash_payload(raw_record)[:10].upper()
    )

    response = PredictionResponse(
        employee_id=employee_id,
        risk_level=result_frame.iloc[0]["risk_level"],
        probability=float(result_frame.iloc[0]["probability"]),
        confidence=float(result_frame.iloc[0]["confidence"]),
        binary_prediction=int(result_frame.iloc[0]["binary_prediction"]),
        top_features=contributions,
        recommendations=recommendations,
        profile_url=f"/employee/{employee_id}",
    )

    storage.append_prediction_logs(
        [
            build_prediction_entry(
                response,
                raw_record,
                source="single",
                input_hash=predictor.hash_payload(raw_record),
            )
        ]
    )

    if is_htmx(request):
        context = {"request": request, "prediction": response}
        return templates.TemplateResponse(request, "partials/prediction_result.html", context)
    return JSONResponse(content=response.model_dump(mode="json"))


@router.post("/batch-preview", response_class=HTMLResponse, response_model=None)
async def batch_preview(request: Request, file: UploadFile = File(...)) -> HTMLResponse | JSONResponse:
    try:
        frame = preview_frame_from_upload(file)
    except ValueError as exc:
        return error_response(422, "Invalid Upload", str(exc))
    except pd.errors.ParserError:
        return error_response(422, "Invalid CSV", "Unable to parse the uploaded CSV file.")

    missing_columns = validate_batch_columns(frame)
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        return error_response(
            422,
            "CSV Schema Mismatch",
            f"Missing columns: {missing_text}",
        )

    preview = frame.head(5).fillna("")
    context = {
        "request": request,
        "preview_columns": preview.columns.tolist(),
        "preview_rows": preview.to_dict(orient="records"),
        "row_count": len(frame),
        "column_count": len(frame.columns),
    }
    return templates.TemplateResponse(request, "partials/batch_preview.html", context)


@router.post("/batch-predict", response_model=None)
async def batch_predict(request: Request, file: UploadFile = File(...)) -> HTMLResponse | JSONResponse:
    try:
        frame = preview_frame_from_upload(file)
    except ValueError as exc:
        return error_response(422, "Invalid Upload", str(exc))
    except pd.errors.ParserError:
        return error_response(422, "Invalid CSV", "Unable to parse the uploaded CSV file.")

    missing_columns = validate_batch_columns(frame)
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        return error_response(
            422,
            "CSV Schema Mismatch",
            f"Missing columns: {missing_text}",
        )

    validated_rows: list[dict[str, Any]] = []
    row_errors: list[str] = []
    for row_index, row in frame.iterrows():
        cleaned_row = {
            key: (None if pd.isna(value) else value)
            for key, value in row.to_dict().items()
        }
        try:
            validated_rows.append(EmployeePredictionInput.model_validate(cleaned_row).model_dump())
        except ValidationError as exc:
            row_errors.append(f"Row {row_index + 2}: {compact_validation_error(exc)}")

    if row_errors:
        message = "; ".join(row_errors[:5])
        if len(row_errors) > 5:
            message = f"{message}; plus {len(row_errors) - 5} more validation issues"
        return error_response(422, "CSV Validation Error", message)

    predictor = request.app.state.predictor
    explainer = request.app.state.explainer
    recommender = request.app.state.recommender
    storage = request.app.state.storage

    result_frame, raw_frame, scaled_frame = predictor.predict_records(validated_rows)

    batch_rows: list[BatchPredictionRecord] = []
    log_entries: list[dict[str, Any]] = []
    export_rows: list[dict[str, Any]] = []

    for row_index in range(len(raw_frame)):
        raw_record = raw_frame.iloc[row_index].to_dict()
        risk_level = result_frame.iloc[row_index]["risk_level"]
        contributions = explainer.explain_row(raw_record, scaled_frame.iloc[row_index], top_n=5)
        recommendations = recommender.recommend(raw_record, risk_level)
        employee_id = (
            str(int(raw_record["EmployeeNumber"]))
            if int(raw_record["EmployeeNumber"]) > 0
            else f"BATCH-{row_index + 1:03d}"
        )
        prediction = PredictionResponse(
            employee_id=employee_id,
            risk_level=risk_level,
            probability=float(result_frame.iloc[row_index]["probability"]),
            confidence=float(result_frame.iloc[row_index]["confidence"]),
            binary_prediction=int(result_frame.iloc[row_index]["binary_prediction"]),
            top_features=contributions,
            recommendations=recommendations,
            profile_url=f"/employee/{employee_id}",
        )
        key_risk_factors = [item.label for item in contributions[:3]]
        batch_rows.append(
            BatchPredictionRecord(
                employee_id=employee_id,
                department=str(raw_record["Department"]),
                job_role=str(raw_record["JobRole"]),
                risk_level=risk_level,
                probability=prediction.probability,
                confidence=prediction.confidence,
                key_risk_factors=key_risk_factors,
                profile_url=prediction.profile_url,
            )
        )
        log_entries.append(
            build_prediction_entry(
                prediction,
                raw_record,
                source="batch",
                input_hash=predictor.hash_payload(raw_record),
            )
        )
        export_rows.append(
            {
                "Employee ID": employee_id,
                "Department": raw_record["Department"],
                "Job Role": raw_record["JobRole"],
                "Risk Level": risk_level,
                "Probability Score": round(prediction.probability * 100, 2),
                "Confidence Score": round(prediction.confidence * 100, 2),
                "Key Risk Factors": ", ".join(key_risk_factors),
                "Recommendations": " | ".join(
                    f"[{item.category}] {item.message}" for item in recommendations
                ),
            }
        )

    storage.append_prediction_logs(log_entries)
    batch_id = storage.save_batch_results(pd.DataFrame(export_rows))
    response = BatchPredictionResponse(
        batch_id=batch_id,
        total_processed=len(batch_rows),
        high_risk_count=sum(row.risk_level == "High Risk" for row in batch_rows),
        medium_risk_count=sum(row.risk_level == "Medium Risk" for row in batch_rows),
        low_risk_count=sum(row.risk_level == "Low Risk" for row in batch_rows),
        average_attrition_probability=sum(row.probability for row in batch_rows) / len(batch_rows),
        records=batch_rows,
        download_url=f"/api/batch-results/{batch_id}/download",
    )

    if is_htmx(request):
        context = {"request": request, "batch": response}
        return templates.TemplateResponse(request, "partials/batch_results.html", context)
    return JSONResponse(content=response.model_dump(mode="json"))


@router.get("/batch-results/{batch_id}/download", response_model=None)
async def download_batch_results(batch_id: str, request: Request) -> FileResponse | JSONResponse:
    output_path = request.app.state.storage.get_batch_results_path(batch_id)
    if not output_path.exists():
        return error_response(404, "Batch Not Found", "Requested batch result file does not exist.")
    return FileResponse(
        output_path,
        media_type="text/csv",
        filename=f"employee-attrition-batch-{batch_id}.csv",
    )


@router.get("/employee/{employee_id}")
async def employee_profile_api(employee_id: str, request: Request) -> JSONResponse:
    profile = request.app.state.analytics.get_employee_profile(employee_id)
    if profile is None:
        return error_response(404, "Profile Not Found", "No prediction profile was found for that employee.")

    prediction = profile["prediction"].model_dump(mode="json")
    return JSONResponse(
        content={
            "employee": profile["employee"],
            "prediction": prediction,
            "contributions": [item.model_dump(mode="json") for item in profile["contributions"]],
            "notes": profile["notes"],
        }
    )


@router.post("/employee/{employee_id}/notes", response_class=HTMLResponse, response_model=None)
async def add_employee_note(
    employee_id: str,
    request: Request,
    note: str = Form(...),
    author: str = Form("HR Partner"),
) -> HTMLResponse | JSONResponse:
    if not note.strip():
        return error_response(422, "Validation Error", "Note content cannot be empty.")

    notes = request.app.state.storage.add_employee_note(employee_id, note, author=author)
    context = {"request": request, "notes": notes}
    return templates.TemplateResponse(request, "partials/employee_notes.html", context)


@router.get("/options/job-roles", response_class=HTMLResponse)
async def job_role_options(
    request: Request,
    department: str,
    wrapper_id: str = "job-role-wrapper-page",
    selected: str | None = None,
) -> HTMLResponse:
    defaults = request.app.state.predictor.get_form_defaults()
    selected_value = selected if selected else defaults.get("JobRole")
    context = {
        "request": request,
        "wrapper_id": wrapper_id,
        "job_roles": get_job_role_options(department),
        "selected_value": selected_value,
    }
    return templates.TemplateResponse(request, "partials/job_role_select.html", context)


@router.get("/analytics/summary")
async def analytics_summary(request: Request) -> JSONResponse:
    return JSONResponse(content=request.app.state.analytics.get_summary_payload())


@router.get("/analytics/department", response_model=None)
async def analytics_department(
    request: Request, partial: str | None = None
) -> HTMLResponse | JSONResponse:
    if partial == "heatmap":
        context = {"request": request, "heatmap": request.app.state.analytics.get_heatmap_payload()}
        return templates.TemplateResponse(request, "partials/analytics_heatmap.html", context)
    return JSONResponse(content=request.app.state.analytics.get_department_payload())


@router.get("/analytics/trends", response_model=None)
async def analytics_trends(
    request: Request, partial: int | None = None
) -> HTMLResponse | JSONResponse:
    payload = request.app.state.analytics.get_trends_payload()
    if partial:
        return templates.TemplateResponse(
            request,
            "partials/analytics_trends.html",
            {"request": request, "payload": payload},
        )
    return JSONResponse(content=payload)


@router.get("/analytics/top-features", response_model=None)
async def analytics_top_features(
    request: Request, partial: int | None = None
) -> HTMLResponse | JSONResponse:
    payload = request.app.state.analytics.get_top_features_payload()
    if partial:
        return templates.TemplateResponse(
            request,
            "partials/analytics_top_features.html",
            {"request": request, "payload": payload},
        )
    return JSONResponse(content=payload)


@router.get("/analytics/age-groups", response_model=None)
async def analytics_age_groups(
    request: Request, partial: int | None = None
) -> HTMLResponse | JSONResponse:
    payload = request.app.state.analytics.get_age_groups_payload()
    if partial:
        return templates.TemplateResponse(
            request,
            "partials/analytics_age_groups.html",
            {"request": request, "payload": payload},
        )
    return JSONResponse(content=payload)


@router.get("/analytics/income-scatter", response_model=None)
async def analytics_income_scatter(
    request: Request, partial: int | None = None
) -> HTMLResponse | JSONResponse:
    payload = request.app.state.analytics.get_income_scatter_payload()
    if partial:
        return templates.TemplateResponse(
            request,
            "partials/analytics_income_scatter.html",
            {"request": request, "payload": payload},
        )
    return JSONResponse(content=payload)
