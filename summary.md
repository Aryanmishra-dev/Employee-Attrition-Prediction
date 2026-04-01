# Employee Attrition Prediction - Project Summary

Last updated: 2 April 2026

## Executive Summary

This project has progressed from a notebook-based machine learning flow into a production-style web application for employee attrition risk assessment. It now includes:

- A trained and serialized model artifact
- A FastAPI backend with page and API routes
- HTMX + Jinja2 UI for interactive workflows
- Single and batch prediction pipelines
- Explainability, recommendations, and employee notes
- Analytics dashboards and model transparency pages
- Containerization and deployment configuration
- Smoke testing for core paths

The system is currently in a deployable, demo-ready state for internal HR analytics workflows.

## What Has Been Done So Far (Step by Step)

1. Defined the project scope and dataset
- Selected the IBM HR analytics dataset as the training and inference foundation.
- Established the project objective: predict employee attrition risk and support HR intervention decisions.

2. Implemented the model training pipeline
- Built a training script in scripts/train_model.py.
- Added preprocessing logic for:
  - Binary mappings (for fields such as Gender and OverTime)
  - One-hot encoding for nominal fields
  - Engineered features (IncomePerYear, PromotionLag, TenureRatio, SatisfactionScore, IsOverworked, ExperienceLevel)
- Trained a Logistic Regression model with balanced class weighting.
- Added threshold selection logic tuned to favor recall while keeping acceptable accuracy.

3. Built and serialized the deployable model artifact
- Saved model coefficients, scaler statistics, thresholds, and metadata into app/ml_model/model.pkl.
- Included model metrics, confusion matrix, feature importance values, and training notes in the artifact.
- Preserved default form values and dataset overview metadata for runtime UX and reporting.

4. Created a lightweight runtime inference engine
- Implemented inference in app/services/predictor.py.
- Reused the same feature engineering and encoding path as training.
- Applied manual NumPy-based scaling and probability computation at runtime for lean deployment.
- Added risk level categorization (Low/Medium/High) and confidence scoring.

5. Added strict input and output schema validation
- Implemented Pydantic contracts in app/models/schemas.py.
- Enforced field ranges, categorical constraints, and department-job role compatibility validation.
- Defined structured response schemas for:
  - Single prediction
  - Batch prediction
  - Feature contributions
  - Recommendation items
  - Employee notes

6. Introduced explainability for predictions
- Built the explainer service in app/services/explainer.py.
- Combined scaled feature values, directional correlation, and feature importance to estimate contribution impact.
- Returned top drivers with labels, values, and direction (toward attrition vs retention).

7. Implemented recommendation logic for HR actions
- Added rule-based recommendation engine in app/services/recommender.py.
- Included risk-aware recommendations across wellbeing, growth, compensation, environment, and engagement categories.
- Prioritized recommendations with urgency ordering.

8. Implemented persistent storage for runtime data
- Added app/services/storage.py for:
  - Append-only JSONL prediction logging
  - Employee notes persistence in JSON
  - Batch CSV result storage in app/data/batches
- Added thread-safe writes using a lock.

9. Built analytics aggregation service
- Implemented app/services/analytics.py to aggregate:
  - Baseline predictions on dataset bootstrap
  - Logged prediction history
  - Dashboard summary metrics
  - Department distribution, trends, age-group comparison, income-risk scatter, and heatmap payloads
- Added employee profile assembly with contributions, radar chart data, and notes.

10. Created backend app composition and lifecycle wiring
- Built app/main.py with FastAPI lifespan setup.
- Initialized and attached predictor, explainer, recommender, storage, and analytics services to app state.
- Registered page routes and API routes.
- Added health endpoint and static app.js endpoint.

11. Delivered page routes for core user journeys
- Implemented app/routes/pages.py routes for:
  - Dashboard
  - Single prediction
  - Batch prediction
  - Employee profile
  - Analytics
  - Model info
  - Quick prediction modal

12. Delivered API routes for operational workflows
- Implemented app/routes/api.py routes for:
  - Single employee prediction
  - Batch preview and batch scoring
  - Batch results CSV download
  - Employee profile API
  - Employee note submission
  - Job role dynamic option endpoint
  - Analytics endpoints (summary, department, trends, top features, age groups, income scatter)
- Added HTMX-aware response handling for partial rendering.

13. Built the front-end template system
- Created shared layout and navigation in app/templates/base.html.
- Implemented dedicated templates for dashboard, prediction pages, analytics, model info, employee profile, and batch flows.
- Added partial templates for HTMX lazy-loading and modular rendering.

14. Added front-end interaction layer
- Implemented public/app.js for:
  - Chart lifecycle management
  - Modal open/close behavior
  - Mobile sidebar toggle
  - Sort/filter enhancements for result tables
  - HTMX response error rendering in target containers

15. Added smoke test coverage for core behavior
- Implemented scripts/smoke_test.py with TestClient checks for:
  - Main pages
  - Prediction and analytics APIs
  - HTMX partial endpoints
  - Batch preview and scoring flow
  - Notes and job-role option endpoints
- Added run_test.py as an app entry wrapper.

16. Completed containerization and deployment setup
- Added Dockerfile with slim Python base image and production uvicorn command.
- Added docker-compose.yml with runtime env vars and persistent data volume mapping.
- Added render.yaml for Render deployment with health checks and environment variable mapping.

17. Established dependency and environment configuration
- Pinned runtime dependencies in requirements.txt.
- Added .env.example for risk-threshold configuration.
- Included thresholds as environment-overridable settings in runtime logic.

18. Project documentation and operational notes
- Added README.md with setup, run, testing, and deployment usage notes.
- Kept notebook artifact (ml-flow-of-ibm.ipynb) as training reference while using script-based artifact generation for deployment.

## Current Functional Capabilities

- Predict attrition risk for a single employee (form + API).
- Score CSV batches with preview, validation, and downloadable results.
- View employee profile with key risk drivers, recommendations, radar comparison, and notes.
- Monitor aggregate risk and trends through dashboard and analytics views.
- Inspect model metrics and top features through model info pages.
- Persist prediction history for audit and analytics enrichment.

## Deployment and Runtime Readiness

- Health endpoint available for platform probes.
- Runtime data directory can be configured via APP_RUNTIME_DATA_DIR.
- Risk band thresholds are configurable via HIGH_RISK_THRESHOLD and MEDIUM_RISK_THRESHOLD.
- Docker and Render configs are already present.

## Current Status

Phase status: Completed for MVP + production-style packaging.

The application has end-to-end functionality implemented across model inference, backend APIs, UI workflows, analytics, persistence, and deployment scaffolding. It is ready for internal review, demo usage, and iterative hardening.

## Suggested Next Milestones (Professional Backlog)

1. Add automated unit/integration tests beyond smoke tests (predictor, explainer, APIs, storage).
2. Introduce model versioning and artifact registry practices.
3. Add authentication/authorization for HR-only access.
4. Implement structured logging and observability dashboards.
5. Add CI pipeline for lint, tests, and container build validation.
6. Add data drift and model performance monitoring on new prediction logs.
