# Healthcare Insurance Fraud Detection (TensorFlow + Keras)

## Overview

This module predicts whether an insurance claim is fraudulent using a TensorFlow + Keras Multi-Layer Perceptron (MLP) model.

---

## Folder Structure

```
dl/
├── model/
├── prediction/
├── schema/
├── reports/
├── samples/
├── requirements.txt
└── README.md
```

---

## Model Files

- best_model.keras
- model_weights.weights.h5
- preprocessor.pkl

---

## Prediction

Use:

```python
from prediction.predict import predict_claim

result = predict_claim(claim_data)
```

---

## Sample Output

```json
{
  "prediction": "Fraud",
  "fraud_probability": 92.5,
  "risk_level": "High",
  "confidence": 92.5,
  "reasons": [
    "High Claim Amount",
    "Frequent Previous Visits"
  ]
}
```

---

## Explainability

The project provides:

- Rule-based explanations through `explainability.py`
- SHAP analysis for model interpretation during development

---

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Model

- TensorFlow
- Keras Sequential MLP
- Binary Classification
- SHAP Explainability