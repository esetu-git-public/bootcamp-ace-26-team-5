import joblib
import pandas as pd
from pathlib import Path

# Resolve threshold paths
BASE_DIR = Path(__file__).resolve().parent.parent
CLAIM_LIMIT_PATH = BASE_DIR / "models" / "claim_threshold.pkl"
PROVIDER_LIMIT_PATH = BASE_DIR / "models" / "provider_threshold.pkl"

# Default fallback thresholds
_claim_threshold = 711.365
_provider_threshold = 72.0

def load_thresholds():
    """
    Loads quantile thresholds from pickled files if they exist.
    """
    global _claim_threshold, _provider_threshold
    
    if CLAIM_LIMIT_PATH.exists():
        try:
            _claim_threshold = float(joblib.load(CLAIM_LIMIT_PATH))
        except Exception:
            pass
            
    if PROVIDER_LIMIT_PATH.exists():
        try:
            _provider_threshold = float(joblib.load(PROVIDER_LIMIT_PATH))
        except Exception:
            pass

# Load at module initialization
load_thresholds()

def run_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs baseline numerical expansions on raw input features for the Keras preprocessor.
    Excludes unused age grouping or claim delay categoricals.
    """
    df = df.copy()
    
    # 1. Numerical derivations
    df["Approval_Ratio"] = df["Approved_Amount"] / (df["Claim_Amount"] + 1)
    df["High_Claim"] = (df["Claim_Amount"] > _claim_threshold).astype(int)
    df["Long_Stay"] = (df["Length_of_Stay"] >= 7).astype(int)
    df["Frequent_Visitor"] = (df["Prior_Visits_12m"] >= 5).astype(int)
    df["High_Provider_Load"] = (df["Number_of_Claims_Per_Provider_Monthly"] > _provider_threshold).astype(int)
    
    # 2. Composite additive score
    df["Risk_Score"] = (
        df["High_Claim"] + 
        df["Long_Stay"] + 
        df["Frequent_Visitor"] + 
        df["High_Provider_Load"]
    )
    
    return df
