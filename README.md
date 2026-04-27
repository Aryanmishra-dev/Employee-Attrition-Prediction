# Employee Attrition Prediction

FastAPI and HTMX application for exploring employee attrition risk, scoring employee CSV batches, and reviewing model explanations for HR analytics workflows.

This repository is now structured as a hardened MVP. It is suitable for demos, experimentation, and internal technical review. Before using real employee data, enable authentication, configure persistent storage outside the container, and complete the governance checklist below.

## Features

- Single employee attrition prediction through a web form and JSON API.
- Batch CSV preview, validation, scoring, and downloadable CSV exports.
- Employee profile pages with risk drivers, recommendations, satisfaction radar, and notes.
- Dashboard and analytics views for aggregate risk trends.
- Model-info page with metrics, confusion matrix, feature importances, and training notes.
- Lightweight NumPy inference artifact for smaller runtime containers.
- Security headers, optional auth gate, upload and row limits, Docker, Render config, and smoke tests.

## Project Layout

```text
app/
  core/          Settings and security middleware
  models/        Pydantic request/response schemas
  routes/        Page and API routes
  services/      Prediction, analytics, storage, recommendations, explanations
  templates/     Jinja2 pages and HTMX partials
  ml_model/      Packaged model artifact
public/          Browser JavaScript
scripts/         Training and smoke-test scripts
docs/            Review and README drafts
tests/           Focused unit tests
```

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

## Configuration

Copy `.env.example` and adjust values for your environment:

```bash
cp .env.example .env
```

Supported environment variables:

```text
APP_RUNTIME_DATA_DIR=app/data
APP_MAX_UPLOAD_BYTES=2000000
APP_MAX_BATCH_ROWS=5000
APP_MAX_NOTE_CHARS=2000
APP_STORE_RAW_PREDICTION_INPUTS=true
APP_ALLOWED_HOSTS=*
APP_ALLOWED_ORIGINS=
APP_AUTH_TOKEN=
APP_AUTH_USERNAME=
APP_AUTH_PASSWORD=
APP_ENABLE_DOCS=true
MEDIUM_RISK_THRESHOLD=0.35
HIGH_RISK_THRESHOLD=0.65
PORT=8000
```

Risk thresholds must satisfy:

```text
0 <= MEDIUM_RISK_THRESHOLD <= HIGH_RISK_THRESHOLD <= 1
```

Authentication is optional for local demos. For any shared deployment, set either `APP_AUTH_TOKEN` for API clients or `APP_AUTH_USERNAME` and `APP_AUTH_PASSWORD` for browser basic auth.

## Testing

Smoke test:

```bash
python3 scripts/smoke_test.py
```

Unit tests:

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest
```

Without installing dev tools, the current focused tests also run with:

```bash
python3 -m unittest discover -s tests
```

Syntax check:

```bash
python3 -m compileall app scripts api tests
```

## Training

The packaged model artifact is:

```text
app/ml_model/model.pkl
```

Rebuild it with training dependencies:

```bash
python3 -m pip install -r requirements-train.txt
python3 scripts/train_model.py
```

The current served artifact is a balanced Logistic Regression model with stored coefficients, scaler statistics, feature metadata, thresholds, and metrics. The runtime predictor computes probabilities with NumPy instead of loading scikit-learn at serving time.

## Docker

```bash
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000
```

## Production Checklist

- Enable authentication and role-based access control.
- Configure `APP_ALLOWED_HOSTS` and `APP_ALLOWED_ORIGINS`.
- Move prediction logs, notes, and batch exports to managed persistent storage.
- Add encryption at rest, retention policies, and audit logging.
- Replace CDN frontend assets with self-hosted assets or add SRI.
- Add CI for linting, tests, dependency scanning, and image scanning.
- Add model card, fairness checks, calibration, subgroup metrics, and drift monitoring.
- Treat predictions as decision support for human review, not automated employment decisions.

## Limitations

- The IBM HR dataset is a sample dataset and may not represent a real workforce.
- Current local file storage is appropriate for demos, not multi-worker production.
- The `confidence` value is a score-certainty indicator, not a calibrated guarantee of correctness.
