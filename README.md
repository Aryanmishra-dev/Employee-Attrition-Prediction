# Employee Attrition Prediction

FastAPI and HTMX application for exploring employee attrition risk, scoring employee CSV batches, and reviewing model explanations for HR analytics workflows.

This repository is structured as a hardened MVP. It is suitable for demos, experimentation, and internal technical review. Before using real employee data, it is crucial to enable authentication, configure persistent storage outside the container, and complete the governance and security checklists below.

## Features

- **Single and Batch Predictions**: Predict attrition risk for a single employee via a web form or API, and score entire employee batches from CSV files.
- **Employee Profiles**: View detailed profiles for each employee, including risk drivers, actionable recommendations, and a satisfaction radar chart.
- **Analytics Dashboard**: Explore aggregate risk trends with interactive charts for departments, age groups, and income levels.
- **Model Insights**: Understand the model's behavior with a dedicated page for metrics, confusion matrix, feature importances, and training details.
- **Lightweight & Secure**: Uses a lightweight NumPy inference artifact, includes security headers, optional authentication, upload/row limits, and is containerized with Docker.

## Project Layout

```text
app/
  core/          # Settings and security middleware
  models/        # Pydantic request/response schemas
  routes/        # Page and API routes
  services/      # Prediction, analytics, storage, recommendations, explanations
  templates/     # Jinja2 pages and HTMX partials
  ml_model/      # Packaged model artifact
public/          # Browser JavaScript
scripts/         # Training and smoke-test scripts
docs/            # Review and README drafts
tests/           # Unit tests
```

## Quick Start

1.  **Set up the environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    ```

2.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```

3.  **Access the application:**
    Open your browser to `http://127.0.0.1:8000`.

## Configuration

Configuration is managed via environment variables. Copy the example file and customize it for your environment:

```bash
cp .env.example .env
```

Key environment variables:

- `APP_RUNTIME_DATA_DIR`: Directory for storing runtime data.
- `APP_MAX_UPLOAD_BYTES`: Maximum file upload size in bytes.
- `APP_MAX_BATCH_ROWS`: Maximum number of rows in a batch CSV.
- `APP_AUTH_TOKEN`: API token for bearer authentication.
- `APP_AUTH_USERNAME` / `APP_AUTH_PASSWORD`: Credentials for basic web authentication.
- `MEDIUM_RISK_THRESHOLD` / `HIGH_RISK_THRESHOLD`: Thresholds for risk categorization.

## API Endpoints

The API provides programmatic access to the application's features.

- `GET /health`: Health check endpoint.
- `POST /api/predict`: Predict attrition for a single employee.
- `POST /api/batch-predict`: Score a batch of employees from a CSV file.
- `GET /api/employee/{employee_id}`: Retrieve an employee's profile and risk analysis.

For detailed API documentation, start the application and visit `http://127.0.0.1:8000/docs`.

## Testing

- **Smoke Test**:
  ```bash
  python3 scripts/smoke_test.py
  ```
- **Unit Tests**:
  ```bash
  python3 -m pip install -r requirements-dev.txt
  python3 -m pytest
  ```

## Training

The model artifact (`app/ml_model/model.pkl`) can be rebuilt using the training script.

```bash
python3 -m pip install -r requirements-train.txt
python3 scripts/train_model.py
```

The current model is a Logistic Regression classifier. The training script saves the model's coefficients and scaler statistics for lightweight, NumPy-based inference at runtime.

## Docker

Build and run the application using Docker Compose:

```bash
docker compose up --build
```

The application will be available at `http://127.0.0.1:8000`.

## Security and Production Readiness

This application has been hardened but requires further steps for production use with sensitive data.

### Critical Production Steps:

- **Authentication & Authorization**: Integrate with a production-grade authentication system (e.g., SSO/OIDC) and implement Role-Based Access Control (RBAC).
- **Secure Data Storage**: Replace local file storage with a managed, encrypted database (e.g., Postgres) and object storage for sensitive data like prediction logs and employee notes.
- **Asynchronous Task Handling**: Move large batch processing to a background job queue to prevent blocking server resources.
- **Model Governance**: Implement a full model governance workflow, including versioning, fairness and bias audits, calibration, and drift monitoring.
- **Web Security**: Enforce HTTPS, add CSRF protection, implement rate limiting, and use a strict Content Security Policy (CSP).

### Limitations:

- The included IBM HR dataset is for demonstration purposes and may not reflect a real-world workforce.
- The current file-based storage is not suitable for multi-worker or distributed deployments.
- Predictions should be used for decision support and reviewed by a human, not for automated employment decisions.

