# Model README Draft

## Purpose

The model estimates attrition risk from structured HR attributes such as role, tenure, compensation, overtime, satisfaction scores, and career history.

This model should be used as decision support for HR review, not as an automated employment decisioning system.

## Data

Training data:

```text
IBM-HR-Analytics-Employee-Attrition-and-Performance.csv
```

The dataset is a public sample dataset. It may not match the distribution, policies, compensation bands, job taxonomy, or attrition patterns of a real organization.

## Features

Preprocessing currently includes:

- Binary mapping for `Gender` and `OverTime`.
- One-hot encoding for business travel, department, education field, job role, and marital status.
- Dropping constant or identifier-like columns for modeling.
- Engineered features:
  - `IncomePerYear`
  - `PromotionLag`
  - `TenureRatio`
  - `SatisfactionScore`
  - `IsOverworked`
  - `ExperienceLevel`
- Standard scaling using stored mean and scale values.

## Current Artifact

Artifact path:

```text
app/ml_model/model.pkl
```

Current artifact metadata reports:

```text
Accuracy: 0.7823
Precision: 0.3867
Recall: 0.6170
F1 score: 0.4754
AUC-ROC: 0.8108
Classification threshold: 0.53
Confusion matrix: [[201, 46], [18, 29]]
```

The current training script stores Logistic Regression coefficients and scaler statistics for lightweight runtime inference. Keep future model summaries aligned with the artifact that is actually served.

## Reproducible Training

Recommended command after adding training dependencies:

```bash
python3 -m pip install -r requirements-train.txt
python3 scripts/train_model.py
```

Recommended `requirements-train.txt` entries:

```text
-r requirements.txt
scikit-learn==1.8.0
```

## Validation Recommendations

Add:

- Stratified cross-validation.
- Calibration curve and Brier score.
- Precision-recall curve and PR-AUC.
- Subgroup metrics by department, gender, age band, role, and income band.
- Threshold analysis based on false-positive and false-negative business cost.
- Stability testing across random seeds.
- Training/inference parity tests.
- Drift monitoring for incoming prediction requests.

## Governance Recommendations

Create a model card with:

- Intended use and non-use cases.
- Training dataset description.
- Feature list and transformations.
- Evaluation metrics and limitations.
- Fairness and subgroup analysis.
- Human review policy.
- Retraining cadence.
- Owner and approver.
- Artifact checksum and version.

## Artifact Safety

The application loads the model with `joblib.load()`. Only load artifacts produced by the trusted training pipeline. Do not accept user-uploaded pickle/joblib files, and verify artifact checksums before deployment.
