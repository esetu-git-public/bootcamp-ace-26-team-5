# Explainability Engine Design: Claim Inspector Metrics

This document explains the algorithms and levels used by the Explainability Engine to map model classifications to natural language audit indicators and advanced mathematical features.

---

## 1. Explainability Levels

The platform supports two levels of explainability to keep the MVP simple while providing clean slots for deep mathematical auditing.

### Simple Explainability (Default)
Exposes human-readable indices directly suited for standard claim inspectors:
* **Risk Level:** Outlines `Low`, `Medium`, or `High` risk routing based on model probability.
* **Top Risk Factors:** Key reasons triggering flags (e.g., unusually large bills or hospital stay duration).
* **Suggested Action:** Recommended workflows (e.g. auto-approve vs immediate inspection).
* **Reviewer Notes:** Summarized findings paragraph.

### Advanced Explainability (Future Placeholders)
Returned when passing `explain_level="advanced"` in prediction requests. Integrates mock structures preparing the frontend for:
* **SHAP Values:** Local feature contribution scores representing the impact of individual features.
* **LIME Weights:** Local interpretable model-agnostic explanation coefficients.
* **Integrated Gradients:** Neural network gradients demonstrating input feature saliency.

---

## 2. Metric Calculations

### Fraud Probability & Risk Levels
The neural network outputs a continuous probability score $P(\text{Fraud}) \in [0.0, 1.0]$. The risk level is routed according to boundaries:
* **Low Risk:** $P(\text{Fraud}) < 30\%$  
  *(Suggested Action: Auto-Approve Claim)*
* **Medium Risk:** $30\% \le P(\text{Fraud}) < 70\%$  
  *(Suggested Action: Route for Auditing / Under Review)*
* **High Risk:** $P(\text{Fraud}) \ge 70\%$  
  *(Suggested Action: Escalate to Claim Inspector Queue)*

### Prediction Confidence
Confidence indicates the model's certainty regarding its final classification:
$$\text{Confidence} = \begin{cases} 
1 - P(\text{Fraud}) & \text{if } P(\text{Fraud}) < 0.50 \text{ (Not Fraud)} \\
P(\text{Fraud}) & \text{if } P(\text{Fraud}) \ge 0.50 \text{ (Fraud)}
\end{cases}$$

---

## 3. Risk Indicators and Review Factors

The Explainability Engine analyzes features against statistical averages to compile positive/negative indicators.

### Top Risk Factors:
Flagged if a feature crosses its specific outlier threshold (e.g. claim size $> \$711.36$, stay duration $\ge 7$ days, or monthly provider claims $> 72$).

### Positive Indicators (Risk Mitigators):
* Claim size within normal boundaries.
* Acceptable approved amount ratio.
* Standard stay duration.
* Stable monthly provider volume.
* Supporting accident evidence available (police reports or witnesses counts).

### Negative Indicators (Risk Promoters):
* Low approval ratio on billing claims.
* High provider density/activity logs.
* Long stay lengths.
* Chronic illness conditions.
