# Technical Review

Review date: 2026-04-27

## Executive Verdict

This is a solid demo/MVP for an employee attrition dashboard: the app has a working FastAPI backend, HTMX/Jinja UI, strict Pydantic input validation, a lightweight NumPy inference path, Docker packaging, and smoke-test coverage for core flows.

After the hardening pass, the largest MVP loopholes have been reduced: configuration is centralized, optional authentication is available, security headers are emitted, upload size/row limits are enforced, dependency groups exist, and the model documentation now matches the training script. The remaining blockers for real HR production use are RBAC/SSO, managed encrypted persistence, audit logging, rate limiting, and deeper MLOps governance.

Overall score: 74 / 100.

## Score Breakdown

| Area | Score | Notes |
| --- | ---: | --- |
| Architecture | 74 | Clear route/service split and centralized settings; app state and analytics remain coupled. |
| Code quality | 74 | Readable Python and schemas; route handlers still carry orchestration logic. |
| Security | 68 | Auth gate, CSP/security headers, origin check, upload limits, and batch ID validation added; RBAC and rate limits remain. |
| Scalability | 55 | Upload limits help, but batch scoring, analytics, logs, and storage are still synchronous and file-backed. |
| Maintainability | 74 | README, env example, dependency groups, tests, and settings layer added; CI still missing. |
| ML/MLOps | 62 | Model documentation now matches the artifact; fairness, calibration, versioning, and drift monitoring remain. |
| Documentation | 76 | Root README and supporting drafts are updated; deeper operational docs can still grow. |
| Deployment readiness | 69 | Docker/Render config improved; managed persistence, observability, and production auth integration remain. |

## Strengths

- FastAPI lifespan cleanly wires predictor, storage, explainer, recommender, and analytics services in `app/main.py`.
- Pydantic schemas enforce numeric ranges, categorical values, and department/job-role compatibility in `app/models/schemas.py`.
- Runtime inference avoids heavy scikit-learn dependencies by storing coefficients and scaler statistics.
- Templates use Jinja escaping and `tojson` for chart payloads, reducing obvious reflected XSS risk.
- Docker runs as a non-root user.
- `scripts/smoke_test.py` covers pages, prediction, analytics, HTMX partials, batch flows, notes, and options.
- `app/core/settings.py` centralizes environment-driven runtime configuration.
- `app/core/security.py` adds auth gating, security headers, origin checks, request size checks, and trusted-host support.

## Critical Findings

1. Authentication is configurable, but production RBAC/SSO is still missing.

   The app now supports token or HTTP Basic authentication through environment variables. This is a useful deployment gate, but it is not yet a full HR access-control system with users, roles, permissions, sessions, and audit trails.

   Recommendation: integrate SSO/OIDC, add role-based access control, and record audit events for profile views, notes, predictions, and exports.

2. Sensitive employee data is logged to local files without protection.

   `build_prediction_entry()` stores raw employee inputs and prediction outputs, and `AppStorage` persists JSONL logs, notes, and batch result CSVs under `app/data`. This can include age, income, overtime, satisfaction, tenure, department, role, and manager-related signals.

   Recommendation: store only necessary fields, encrypt at rest, define retention/deletion rules, move persistence to a managed database/object store, and add data classification notes to the README.

3. Batch processing is bounded but still synchronous.

   Upload byte and row limits are now enforced, but accepted batches still score synchronously in the request path. At larger volumes this can tie up the worker and delay other users.

   Recommendation: add background jobs for large batches, per-user rate limits, progress tracking, and export expiration.

4. File-backed storage is unsafe for multi-worker or distributed deployment.

   `AppStorage` uses an in-process `threading.Lock`, which does not protect multiple Uvicorn workers, multiple containers, or platform restarts. JSON rewrite for notes is also vulnerable to partial writes and lost updates outside one process.

   Recommendation: use Postgres/SQLite with WAL for local installs, object storage for exports, and database transactions for notes/logs.

5. Model governance remains thin.

   The documentation now describes the actual Logistic Regression artifact, but model governance still lacks cross-validation, fairness analysis, calibration, artifact checksums, and retraining policy.

   Recommendation: add a model card, artifact checksums, subgroup metrics, calibration reporting, and drift monitoring.

## High-Priority Findings

6. Dependency separation has improved, but lockfiles are still missing.

   Runtime, training, and development dependency files now exist. The remaining reproducibility gap is that transitive dependencies are not locked.

   Recommendation: generate lockfiles with a tool such as `uv`, `pip-tools`, or Poetry and refresh them through CI.

7. Pickle/joblib artifact loading is trusted without integrity checks.

   `joblib.load()` loads `app/ml_model/model.pkl` at startup. This is acceptable only if the artifact is fully trusted, but dangerous if an attacker can modify the file or artifact supply chain.

   Recommendation: store artifacts in a trusted registry, verify checksums/signatures, and document that arbitrary uploaded/replaced pickle files must never be loaded.

8. Production web security hardening is partially implemented.

   Security headers, CSP, host validation support, origin checks, request size checks, and optional auth are now present. HSTS, rate limiting, request IDs, centralized error handling, and strict self-hosted frontend assets are still missing.

   Recommendation: self-host JS/CSS assets or add SRI, move inline scripts to static files, enforce HTTPS/HSTS at the platform edge, add rate limiting, and add request IDs.

9. Model validation is thin for HR decision support.

   Current metrics come from one stratified train/test split. There is no cross-validation, probability calibration, fairness analysis, subgroup performance, drift monitoring, or human-in-the-loop policy. The model has moderate recall and low precision, so many employees may be flagged incorrectly.

   Recommendation: add cross-validation, calibration curves, PR-AUC, subgroup metrics, threshold rationale, fairness review, model card, data sheet, and explicit "decision support only" language.

10. Analytics recomputes and rereads too much synchronously.

   Analytics combines baseline predictions and file logs on demand. This is fine for demo volume, but it will degrade as logs grow.

   Recommendation: store predictions in queryable tables, pre-aggregate dashboard metrics, paginate recent predictions, and cache immutable baseline analytics.

## Medium-Priority Findings

11. Route handlers are doing too much.

   `app/routes/api.py` handles parsing, validation, prediction orchestration, explanation, recommendation, logging, export assembly, and response rendering. This makes testing and reuse harder.

   Recommendation: move use cases into an application layer such as `PredictEmployee`, `PreviewBatch`, `RunBatchPrediction`, and `SaveEmployeeNote`.

12. Configuration is centralized, but constants are still mixed.

   `app/core/settings.py` now owns runtime configuration and validates risk thresholds. `app/services/constants.py` still mixes UI labels, ML preprocessing, schema constraints, and navigation data.

   Recommendation: split domain constants, UI metadata, and ML preprocessing configuration into separate modules.

13. The test suite is started, but CI is still missing.

   Focused tests now cover settings validation, security middleware, and storage path safety. Broader tests for feature engineering, schema edge cases, explanation math, upload parsing, and model artifact compatibility are still needed.

   Recommendation: add CI for `pytest`, `ruff`, dependency scanning, Docker builds, and coverage reporting.

14. Most README inaccuracies were fixed, but secondary docs can still drift.

   The root README and `.env.example` now match the repository. The narrative `summary.md` should be treated as historical project notes unless it is kept current with future changes.

   Recommendation: keep README, model docs, and deployment docs updated in the same pull requests as code changes.

15. The `confidence` metric can mislead users.

   `confidence_score()` returns `max(probability, 1 - probability)`, which is model certainty around a binary threshold, not calibrated confidence in correctness.

   Recommendation: rename it to "score certainty" or remove it until calibrated probabilities are available.

16. `run_test.py` has been corrected.

   `run_test.py` now delegates to the smoke test instead of creating a virtual environment and installing dependencies.

   Recommendation: prefer `python3 scripts/smoke_test.py` or `python3 -m pytest` in CI.

## Recommended Project Structure

```text
employee-attrition-prediction/
  pyproject.toml
  README.md
  .env.example
  .gitignore
  docker/
    Dockerfile
    docker-compose.yml
  infra/
    render.yaml
  data/
    sample/
      ibm_hr_sample.csv
  models/
    attrition/
      v1/
        model.joblib
        metadata.json
        checksum.txt
  notebooks/
    ml-flow-of-ibm.ipynb
  scripts/
    train_model.py
    smoke_test.py
  src/
    attrition_app/
      main.py
      core/
        settings.py
        security.py
        logging.py
      api/
        routes.py
        dependencies.py
      web/
        routes.py
        templates/
        static/
      schemas/
        prediction.py
        analytics.py
      services/
        prediction_service.py
        analytics_service.py
        recommendation_service.py
      ml/
        features.py
        artifact.py
        predictor.py
        explain.py
      storage/
        repository.py
        file_repository.py
        postgres_repository.py
  tests/
    unit/
    integration/
    fixtures/
  docs/
    API.md
    MODEL_CARD.md
    SECURITY.md
    OPERATIONS.md
```

## Recommended Roadmap

1. Production blockers: add auth/RBAC, CSRF, rate limits, upload limits, secure headers, and persistent database-backed storage.
2. Correctness: fix model documentation mismatch, validate threshold ordering, rename/remove confidence, and add focused tests for prediction parity.
3. MLOps: add model card, artifact checksums, training requirements, repeatable training command, cross-validation, calibration, fairness, and drift monitoring.
4. Maintainability: introduce settings, dependency groups, lint/type/test CI, repository abstractions, and smaller route handlers.
5. UX/operations: add pagination, export expiration, error pages, logging, request IDs, and operational runbooks.

## Verification Performed

- `python3 scripts/smoke_test.py`: passed.
- `python3 -m compileall app scripts api`: passed.
- `python3 -m pip check`: passed, with a local pip cache permission warning.
- `python3 -m pip_audit`: not available in the current Python environment, so dependency vulnerability auditing was not completed.
