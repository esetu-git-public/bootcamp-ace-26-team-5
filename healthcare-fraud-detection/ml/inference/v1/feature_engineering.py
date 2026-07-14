import os
import joblib
from pathlib import Path
import pandas as pd

# Resolve paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_CLAIM_LIMIT_PATH = BASE_DIR / "models" / "claim_threshold.pkl"
DEFAULT_PROVIDER_LIMIT_PATH = BASE_DIR / "models" / "provider_threshold.pkl"

def run_feature_engineering(df: pd.DataFrame, claim_limit_path=None, provider_limit_path=None) -> pd.DataFrame:
    """
    Applies feature engineering transformation to raw claims DataFrame to align
    with the preprocessor training feature schema.
    """
    c_path = Path(claim_limit_path) if claim_limit_path else DEFAULT_CLAIM_LIMIT_PATH
    p_path = Path(provider_limit_path) if provider_limit_path else DEFAULT_PROVIDER_LIMIT_PATH

    # 1. Load percentile thresholds (derived during model training)
    if c_path.exists():
        claim_limit = float(joblib.load(c_path))
    else:
        claim_limit = 711.365  # Training set 95th percentile fallback

    if p_path.exists():
        provider_limit = float(joblib.load(p_path))
    else:
        provider_limit = 72.0  # Training set 95th percentile fallback

    df_out = df.copy()

    # Ensure numerical casts
    df_out["Claim_Amount"] = pd.to_numeric(df_out["Claim_Amount"], errors="coerce").fillna(150.0)
    df_out["Approved_Amount"] = pd.to_numeric(df_out["Approved_Amount"], errors="coerce").fillna(120.0)
    df_out["Length_of_Stay"] = pd.to_numeric(df_out["Length_of_Stay"], errors="coerce").fillna(2.0)
    df_out["Number_of_Claims_Per_Provider_Monthly"] = pd.to_numeric(df_out["Number_of_Claims_Per_Provider_Monthly"], errors="coerce").fillna(30.0)
    df_out["Prior_Visits_12m"] = pd.to_numeric(df_out["Prior_Visits_12m"], errors="coerce").fillna(1.0)
    df_out["Chronic_Condition_Flag"] = pd.to_numeric(df_out["Chronic_Condition_Flag"], errors="coerce").fillna(0.0)
    df_out["Days_Between_Service_and_Claim"] = pd.to_numeric(df_out["Days_Between_Service_and_Claim"], errors="coerce").fillna(10.0)
    df_out["Procedure_Code"] = pd.to_numeric(df_out["Procedure_Code"], errors="coerce").fillna(99213)

    # 2. Derive engineering baseline features
    df_out["Approval_Ratio"] = df_out["Approved_Amount"] / (df_out["Claim_Amount"] + 1)
    df_out["High_Claim"] = (df_out["Claim_Amount"] > claim_limit).astype(int)
    df_out["Long_Stay"] = (df_out["Length_of_Stay"] >= 7).astype(int)
    df_out["Frequent_Visitor"] = (df_out["Prior_Visits_12m"] >= 5).astype(int)
    df_out["High_Provider_Load"] = (df_out["Number_of_Claims_Per_Provider_Monthly"] > provider_limit).astype(int)
    
    # Composite risk score
    df_out["Risk_Score"] = (
        df_out["High_Claim"] +
        df_out["Long_Stay"] +
        df_out["Frequent_Visitor"] +
        df_out["High_Provider_Load"]
    )

    return df_out
