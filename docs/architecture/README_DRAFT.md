# Employee Attrition Prediction

FastAPI and HTMX application for exploring employee attrition risk, batch scoring employee records, and reviewing model explanations for HR analytics workflows.

This project is suitable for demos, experimentation, and internal technical review. It includes basic hardening controls, but it should not be used with real employee data until production authentication, authorization, secure persistence, audit logging, rate limiting, and model governance controls are completed.

## Features

- Single employee attrition prediction through a web form and JSON API.
- Batch CSV preview, validation, scoring, and downloadable results.
- Employee profile pages with risk drivers, recommendations, satisfaction radar, and notes.
- Dashboard and analytics views for aggregate risk trends.
- Model-info page with metrics, confusion matrix, feature importances, and training notes.
- Lightweight NumPy inference artifact for smaller runtime containers.
- Docker, Docker Compose, Render deployment config, and smoke tests.

## Architecture

```text
Client browser
  -> FastAPI page routes
  -> Jinja2 templates + HTMX partials
  -> API routes
  -> Prediction, explanation, recommendation, analytics, and storage services
  -> Local model artifact and runtime data files
```

Current persistence uses local files under `app/data`. For production, replace this with a transactional database and managed object storage for exports.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Environment Variables

```bash
APP_RUNTIME_DATA_DIR=app/data
MEDIUM_RISK_THRESHOLD=0.35
HIGH_RISK_THRESHOLD=0.65
PORT=8000
```

Recommended validation: `0 <= MEDIUM_RISK_THRESHOLD <= HIGH_RISK_THRESHOLD <= 1`.

## Testing

Run the smoke test:

```bash
python3 scripts/smoke_test.py
```

Run syntax compilation:

```bash
python3 -m compileall app scripts api
```

Recommended additions:

- Unit tests for feature engineering and schema validation.
- Integration tests for API and HTMX responses.
- Storage tests for concurrent notes/log writes.
- Regression tests that compare training-time and runtime inference outputs.
- CI for lint, type checks, tests, and Docker builds.

## Training

The packaged model artifact lives at:

```text
app/ml_model/model.pkl
```

Rebuilding the model requires training dependencies such as `scikit-learn`. Keep training dependencies separate from runtime dependencies, for example:

```bash
python3 -m pip install -r requirements-train.txt
python3 scripts/train_model.py
```

Recommended artifact practices:

- Store model metadata and checksums beside the artifact.
- Version each model artifact.
- Record dataset version, code revision, metrics, thresholds, and feature list.
- Do not load untrusted pickle/joblib artifacts.

## Docker

```bash
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000
```

## Production Readiness Checklist

- Enable authentication and add role-based authorization.
- Add CSRF protection for note and prediction forms.
- Keep upload size and row limits enabled, and add user-level rate limits.
- Move prediction logs, notes, and batch exports out of local app files.
- Add encryption at rest and transport security.
- Add security headers and a Content Security Policy.
- Self-host frontend assets or use Subresource Integrity.
- Add structured logs, request IDs, metrics, and error tracking.
- Add model card, fairness checks, calibration, and drift monitoring.
- Add CI/CD with linting, tests, dependency scanning, and image scanning.

## Important Limitations

- The IBM HR dataset is a sample dataset and may not represent your workforce.
- Predictions should support human review, not automated employment decisions.
- Probability thresholds need validation against business costs and fairness criteria.
- The current local file storage model is not suitable for multi-worker production deployment.
