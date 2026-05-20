from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.core.security import configure_security
from app.core.config import get_settings
from app.api.v1.routes.api import router as api_router
from app.api.v1.routes.pages import router as pages_router
from app.services.analytics import AnalyticsService
from app.services.explainer import AttritionExplainer
from app.services.predictor import AttritionPredictor
from app.services.recommender import RecommendationEngine
from app.services.storage import AppStorage

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    predictor = AttritionPredictor(
        settings.model_path,
        medium_risk_threshold=settings.medium_risk_threshold,
        high_risk_threshold=settings.high_risk_threshold,
    )
    storage = AppStorage(settings.data_dir)
    explainer = AttritionExplainer(predictor.artifact)
    recommender = RecommendationEngine(predictor.department_income_medians)
    analytics = AnalyticsService(
        dataset_path=settings.dataset_path,
        predictor=predictor,
        explainer=explainer,
        recommender=recommender,
        storage=storage,
    )

    app.state.settings = settings
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
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)
configure_security(app, settings)

app.include_router(pages_router)
app.include_router(api_router, prefix="/api", tags=["api"])


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/app.js", include_in_schema=False)
async def app_script() -> FileResponse:
    return FileResponse(settings.public_dir / "app.js", media_type="text/javascript")
