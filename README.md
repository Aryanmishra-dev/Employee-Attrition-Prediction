# Employee Attrition Prediction

A full-stack web application for predicting employee attrition risk using machine learning. Built with FastAPI (Backend) and React + Vite (Frontend), it provides single-employee scoring, CSV batch processing, model explainability, and an analytics dashboard.

---

## Overview

Employee attrition prediction estimates the likelihood that an employee may leave an organization based on workforce, compensation, engagement, and job-history signals. This application operationalizes that workflow into a deployable web service with a modern, industry-grade UI:

- **Single & Batch Predictions** — Score individuals via a web form or API, or process entire employee rosters from CSV uploads.
- **Employee Profiles** — View per-employee risk drivers, actionable HR recommendations, and satisfaction radar charts.
- **Analytics Dashboard** — Explore aggregate risk trends across departments, age groups, income levels, and feature importance.
- **Model Insights** — Inspect model metrics, confusion matrix, feature importances, and training details.
- **Explainability & Recommendations** — Understand *why* a prediction was made, with rule-based suggestions for at-risk employees.

## Dataset

The model is trained on the [IBM HR Analytics Employee Attrition & Performance](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) dataset from Kaggle. The raw CSV is excluded from version control; download it from Kaggle for local training.

## Architecture

```text
├── frontend/          React SPA built with Vite, TypeScript, and Tailwind CSS
├── backend/           FastAPI application — routes, services, schemas, middleware
├── ml/                Training pipelines, feature engineering, model artifacts
├── shared/            Shared constants, field mappings, form builders
├── config/            Environment variable templates
├── deployment/        Docker, Render config, CI/CD scaffolding, smoke tests
├── tests/             Unit, integration, and end-to-end tests
├── data/              Raw, processed, and external data directories
├── monitoring/        Dashboard, alert, and metrics placeholders
└── docs/              Technical documentation, runbooks, architecture notes
```

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Frontend** | React, Vite, TypeScript, Tailwind CSS, Lucide React, Chart.js |
| **ML Model** | Logistic Regression (scikit-learn), NumPy inference |
| **Storage** | JSONL append-only logs, CSV batch storage |
| **Containerization** | Docker, Docker Compose |
| **Deployment** | Render.com |
| **Testing** | Pytest, Ruff (linting), Vitest (Frontend) |

## Setup

### Local Development

#### 1. Backend Setup

```bash
# Clone the repository
git clone <repo-url>
cd employee-attrition-prediction

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp config/.env.example .env

# Run the backend
uvicorn backend.app.main:app --reload
```

The backend API will be available at **http://127.0.0.1:8000**.

#### 2. Frontend Setup

Open a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will be available at **http://localhost:5173** (or as indicated in the terminal).

### Docker

```bash
docker compose -f deployment/docker/docker-compose.yml up --build
```

## Model Performance

| Metric | Value |
|---|---|
| Accuracy | 0.7823 |
| AUC-ROC | 0.8108 |
| F1 Score | 0.4754 |
| Precision | 0.3867 |
| Recall | 0.6170 |

The model uses class weighting and threshold optimization (tuned for F2 score with a minimum accuracy constraint of 0.78) to favor recall, reducing the likelihood of missing at-risk employees.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/predict` | Predict attrition for a single employee |
| POST | `/api/batch-predict` | Score a batch of employees from CSV |
| GET | `/api/employee/{id}` | Retrieve employee profile and risk analysis |

Full interactive API documentation is available at **http://127.0.0.1:8000/docs** when the backend is running.

## Training

To retrain the model:

```bash
pip install -r ml/requirements-train.txt
python ml/pipelines/training/train_model.py
```

The training script serializes model coefficients, scaler statistics, and metadata into a lightweight artifact used for NumPy-based inference at runtime.

## Deployment

The application includes a Render.com deployment configuration:

```bash
docker compose -f deployment/docker/docker-compose.yml up --build
```

See `deployment/render/render.yaml` for Render service configuration and `deployment/docker/docker-compose.yml` for local containerized development.

## Production Readiness

This application has been hardened for demonstration and internal review but requires additional steps before handling sensitive data:

- **Authentication** — Integrate SSO/OIDC and role-based access control.
- **Data Storage** — Replace local file storage with a managed database and encrypted object storage.
- **Background Processing** — Move large batch jobs to a task queue.
- **Model Governance** — Implement versioning, bias audits, calibration, and drift monitoring.
- **Web Security** — Enforce HTTPS, add CSRF protection, rate limiting, and a strict Content Security Policy.

Predictions are intended for decision support and should be reviewed by a human, not used for automated employment decisions.

---

## License

This project is provided for demonstration and educational purposes.
