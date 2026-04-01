from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.constants import PRIMARY_NAV, build_form_sections

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parents[1] / "templates")
)


def base_context(request: Request, title: str, subtitle: str) -> dict[str, object]:
    return {
        "request": request,
        "page_title": title,
        "page_subtitle": subtitle,
        "nav_items": PRIMARY_NAV,
        "current_path": request.url.path,
    }


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    dashboard_context = request.app.state.analytics.get_dashboard_context()
    context = base_context(
        request,
        "Attrition Command Center",
        "Monitor portfolio risk, recent predictions, and department-level signals in one place.",
    )
    context.update(dashboard_context)
    return templates.TemplateResponse(request, "dashboard.html", context)


@router.get("/predict", response_class=HTMLResponse)
async def predict_page(request: Request) -> HTMLResponse:
    defaults = request.app.state.predictor.get_form_defaults()
    context = base_context(
        request,
        "Single Employee Prediction",
        "Run a structured, HTMX-powered attrition assessment for one employee.",
    )
    context.update(
        {
            "form_sections": build_form_sections(defaults),
            "job_role_wrapper_id": "job-role-wrapper-page",
            "result_target": "prediction-result",
            "indicator_id": "predict-indicator-page",
        }
    )
    return templates.TemplateResponse(request, "predict.html", context)


@router.get("/batch-predict", response_class=HTMLResponse)
async def batch_predict_page(request: Request) -> HTMLResponse:
    context = base_context(
        request,
        "Batch Prediction",
        "Upload a CSV, preview the first rows, and score attrition risk at scale.",
    )
    return templates.TemplateResponse(request, "batch_predict.html", context)


@router.get("/employee/{employee_id}", response_class=HTMLResponse)
async def employee_profile_page(request: Request, employee_id: str) -> HTMLResponse:
    profile = request.app.state.analytics.get_employee_profile(employee_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Employee profile not found.")

    context = base_context(
        request,
        f"Employee {profile['employee']['employee_id']} Profile",
        "Review risk drivers, compare satisfaction signals to the company baseline, and capture HR notes.",
    )
    context.update(profile)
    return templates.TemplateResponse(request, "employee_profile.html", context)


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request) -> HTMLResponse:
    dashboard_context = request.app.state.analytics.get_dashboard_context()
    context = base_context(
        request,
        "Analytics",
        "Explore aggregate attrition trends, feature signals, and prediction history.",
    )
    context["summary_stats"] = dashboard_context["summary_stats"]
    return templates.TemplateResponse(request, "analytics.html", context)


@router.get("/model-info", response_class=HTMLResponse)
async def model_info_page(request: Request) -> HTMLResponse:
    context = base_context(
        request,
        "Model Info",
        "Transparent documentation for stakeholders reviewing the ensemble and its performance.",
    )
    context.update(request.app.state.analytics.get_model_info_context())
    return templates.TemplateResponse(request, "model_info.html", context)


@router.get("/modal/predict", response_class=HTMLResponse)
async def quick_predict_modal(request: Request) -> HTMLResponse:
    defaults = request.app.state.predictor.get_form_defaults()
    context = {
        "request": request,
        "form_sections": build_form_sections(defaults),
        "job_role_wrapper_id": "job-role-wrapper-modal",
        "result_target": "prediction-result-modal",
        "indicator_id": "predict-indicator-modal",
    }
    return templates.TemplateResponse(request, "partials/quick_predict_modal.html", context)
