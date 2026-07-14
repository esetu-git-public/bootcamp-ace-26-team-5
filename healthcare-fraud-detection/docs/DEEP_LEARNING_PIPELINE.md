# Deep Learning Prediction Pipeline: Keras 3 (PyTorch Backend)

This document details the configuration, preprocessor columns, and execution design of the primary Deep Learning inference pipeline.

## 1. Deep Learning Pipeline Architecture
The primary inference engine is a Deep Learning Neural Network saved as a Keras module (`best_model.keras`).

```text
  [ Raw JSON Payload ]
           │
           ▼
  [ Feature Engineering ] ──► (Computes ratios, stay indicators, composite score)
           │
           ▼
  [ Keras Preprocessor ] ──► (Scales numericals, transforms categoricals)
           │
           ▼
  [ Keras NN Model ] ──► (Runs dense layers with PyTorch backend tensors)
           │
           ▼
  [ Fraud Probability ] ──► (Enters Explainability Engine)
```

---

## 2. Python 3.14 Compatibility & PyTorch Backend
Due to Python 3.14 environment limits, pre-built binary wheels for `tensorflow` are not available. To run the deep learning pipeline, we deploy **Keras 3** configured to run with the **PyTorch backend** (`torch` is fully compiled and available in the site packages).

```python
import os
os.environ["KERAS_BACKEND"] = "torch"
import keras

model = keras.models.load_model("best_model.keras")
```

---

## 3. Preprocessor Feature Space
The preprocessor `preprocessor_keras.pkl` transforms raw data into dense matrices using 22 engineered and categorical columns.

### Numerical Inputs (15 Columns):
* `Patient_Age`
* `Procedure_Code`
* `Claim_Amount`
* `Approved_Amount`
* `Days_Between_Service_and_Claim`
* `Number_of_Claims_Per_Provider_Monthly`
* `Length_of_Stay`
* `Chronic_Condition_Flag`
* `Prior_Visits_12m`
* `Approval_Ratio` (Engineered)
* `High_Claim` (Engineered)
* `Long_Stay` (Engineered)
* `Frequent_Visitor` (Engineered)
* `High_Provider_Load` (Engineered)
* `Risk_Score` (Engineered)

### Categorical Inputs (7 Columns):
* `Patient_Gender` (Male, Female)
* `Diagnosis_Code` (I10, E11.9, etc.)
* `Insurance_Type` (Medicaid, Medicare, Private, Self-Pay)
* `Provider_Specialty` (Cardiology, General Practice, Internal Medicine, Neurology, Orthopedics, Pulmonology)
* `Patient_State` (CA, FL, GA, IL, NY, OH, PA, TX)
* `Claim_Status` (Approved, Pending, Rejected)
* `Visit_Type` (Emergency, Inpatient, Outpatient)
