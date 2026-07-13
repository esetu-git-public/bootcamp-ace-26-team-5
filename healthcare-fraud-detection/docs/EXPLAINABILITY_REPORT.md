# Explainability Engine & Audit Markers Report

This document reviews the calculation formulas, audit indicators, and advanced explainability stubs used in the Healthcare Fraud Detection System's explainability engine.

---

## 1. Metric Calculations

The explainability engine maps raw outputs from the prediction models to interpretable categories and scores:

### 1.1 Fraud Probability & Risk Levels
The machine learning model outputs a continuous fraud probability $P \in [0.0, 1.0]$. The risk level is categorized as follows:
* **Low Risk:** $P < 0.30$  
  *(Suggested Action: Auto-Approve Claim)*
* **Medium Risk:** $0.30 \le P < 0.70$  
  *(Suggested Action: Route for Auditing / Under Review)*
* **High Risk:** $P \ge 0.70$  
  *(Suggested Action: Escalate to Claim Inspector Queue)*

### 1.2 Prediction Confidence
The prediction confidence score represents the model's certainty regarding its final binary decision (Fraud vs. Not Fraud, threshold = 0.50):
$$\text{Confidence} = \begin{cases} 
1 - P & \text{if } P < 0.50 \text{ (Not Fraud)} \\
P & \text{if } P \ge 0.50 \text{ (Fraud)}
\end{cases}$$
For example, if $P = 0.02$, the confidence is $98\%$ (high certainty of Not Fraud). If $P = 0.85$, the confidence is $85\%$ (certain of Fraud).

---

## 2. Risk Indicators and Review Factors

The engine compares raw patient and billing metrics against predefined thresholds to compile audit lists:

### 2.1 Top Risk Factors (Outliers)
Generated when input features exceed normal bounds:
* **High Claim Amount:** Triggered if `Claim_Amount` $> \$711.37$.
* **Low Approved Ratio:** Triggered if $\frac{\text{Approved\_Amount}}{\text{Claim\_Amount}} < 0.50$.
* **Unusual Hospital Stay:** Triggered if `Length_of_Stay` $\ge 7$ days.
* **High Provider Claims Volume:** Triggered if `Number_of_Claims_Per_Provider_Monthly` $> 72$.
* **Frequent Patient Claims:** Triggered if `Prior_Visits_12m` $\ge 5$.

### 2.2 Positive Indicators (Risk Mitigators)
* Claim amount is within standard limits ($\le \$711.37$).
* Billing approved ratio is acceptable ($\ge 50\%$).
* Length of stay is standard ($< 7$ days).
* Provider billing volume is stable ($\le 72$ claims/month).
* Supporting evidence exists (witness count $> 0$ or police report available).

### 2.3 Negative Indicators (Risk Promoters)
* Billing discrepancy (deduction discrepancy).
* Long hospital stays.
* Chronic health condition presence.
* Prior high-frequency visit records.

---

## 3. Explainability Engine Evaluation

### 3.1 Simple Explainability
* **Status:** Fully functional in production.
* **Evaluation:** Translating continuous model probabilities into structured lists of Top Factors, Mitigators, and Reviewer Notes provides excellent utility for claim inspectors. It ensures they can quickly scan *why* a claim was flagged.

### 3.2 Advanced Explainability
* **Status:** Placeholders returned when `explain_level="advanced"` is requested.
* **Evaluation:** The advanced block contains mock data for SHAP, LIME, and Integrated Gradients.
  * **SHAP (SHapley Additive exPlanations):** High technical merit. For tree-based models like XGBoost, we can calculate exact local feature contributions in real-time using the `shap.TreeExplainer` library.
  * **LIME (Local Interpretable Model-agnostic Explanations):** Lower utility. LIME is slower than Tree SHAP and relies on random perturbations, which can lead to unstable explanations.
  * **Integrated Gradients:** Not applicable. This method is specifically designed for deep neural networks and cannot run on gradient boosted trees like XGBoost.

---

## 4. Production MVP Recommendation

For a production MVP, we recommend **retaining the Simple Explainability engine** and integrating **SHAP (SHapley Additive exPlanations)** as the sole advanced explainability mechanism:

1. **Adopt SHAP for Tabular Audits:** Tree SHAP is the industry standard for explaining tree-based models like XGBoost. It provides mathematically rigorous local attribution scores.
2. **Deprecate LIME and Integrated Gradients:** Delete LIME and Integrated Gradients placeholders. LIME is redundant, and Integrated Gradients is structurally incompatible with XGBoost.
3. **SHAP Integration Path:** In future updates, we can import the `shap` library, initialize a `shap.TreeExplainer(model)` at startup, and compute local SHAP values for the claim during inference.
