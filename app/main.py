from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.routes.api import router as api_router
from app.routes.pages import router as pages_router
from app.services.analytics import AnalyticsService
from app.services.constants import DATASET_FILENAME
from app.services.explainer import AttritionExplainer
from app.services.predictor import AttritionPredictor
from app.services.recommender import RecommendationEngine
from app.services.storage import AppStorage

ROOT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = ROOT_DIR / "app"
MODEL_PATH = APP_DIR / "ml_model" / "model.pkl"
PUBLIC_DIR = ROOT_DIR / "public"
DATASET_PATH = ROOT_DIR / DATASET_FILENAME
runtime_data_dir = os.getenv("APP_RUNTIME_DATA_DIR")
if runtime_data_dir:
    DATA_DIR = Path(runtime_data_dir)
else:
    DATA_DIR = APP_DIR / "data"


@asynccontextmanager
async def lifespan(app: FastAPI):
    predictor = AttritionPredictor(MODEL_PATH)
    storage = AppStorage(DATA_DIR)
    explainer = AttritionExplainer(predictor.artifact)
    recommender = RecommendationEngine(predictor.department_income_medians)
    analytics = AnalyticsService(
        dataset_path=DATASET_PATH,
        predictor=predictor,
        explainer=explainer,
        recommender=recommender,
        storage=storage,
    )

    app.state.predictor = predictor
    app.state.storage = storage
    app.state.explainer = explainer
    app.state.recommender = recommender
    app.state.analytics = analytics
    yield


app = FastAPI(
    title="Employee Attrition Prediction",
    description="FastAPI + HTMX attrition risk dashboard for HR teams.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(pages_router)
app.include_router(api_router, prefix="/api", tags=["api"])


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/app.js", include_in_schema=False)
async def app_script() -> FileResponse:
    return FileResponse(PUBLIC_DIR / "app.js", media_type="text/javascript")
