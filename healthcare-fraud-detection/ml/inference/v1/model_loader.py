import os
import joblib
import json
import threading
from pathlib import Path

# Set Keras backend prior to importing Keras
os.environ["KERAS_BACKEND"] = "torch"

# Resolve package-relative paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_MODEL_PATH = BASE_DIR / "models" / "best_model.keras"
DEFAULT_PREPROCESSOR_PATH = BASE_DIR / "models" / "preprocessor_keras.pkl"
DEFAULT_METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"

# Caching variables
_model = None
_preprocessor = None
_metadata = None
_lock = threading.Lock()

def load_artifacts(model_path=None, preprocessor_path=None, metadata_path=None):
    """
    Lazy-loads and caches the Keras model, preprocessor, and training metadata.
    """
    global _model, _preprocessor, _metadata

    with _lock:
        # 1. Resolve paths
        m_path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
        p_path = Path(preprocessor_path) if preprocessor_path else DEFAULT_PREPROCESSOR_PATH
        meta_path = Path(metadata_path) if metadata_path else DEFAULT_METADATA_PATH

        # 2. Load model metadata
        if _metadata is None:
            if meta_path.exists():
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        _metadata = json.load(f)
                except Exception as e:
                    print(f"[ML LOADER v1] Warning: Failed to parse model metadata: {e}")
                    _metadata = {}
            else:
                _metadata = {}

        # 3. Skip loading model and preprocessor if already cached
        if _model is not None and _preprocessor is not None:
            return _model, _preprocessor, _metadata

        # 4. Import Keras and load assets
        import keras
        
        if not m_path.exists():
            raise FileNotFoundError(f"[ML LOADER v1] Keras model file not found at: {m_path}")
        if not p_path.exists():
            raise FileNotFoundError(f"[ML LOADER v1] Keras preprocessor file not found at: {p_path}")

        if _model is None:
            print(f"[ML LOADER v1] Loading Keras Deep Learning Model (PyTorch Backend) from {m_path}...")
            _model = keras.models.load_model(str(m_path))
            print("[ML LOADER v1] Keras model loaded successfully.")

        if _preprocessor is None:
            print(f"[ML LOADER v1] Loading Preprocessor from {p_path}...")
            _preprocessor = joblib.load(p_path)
            print("[ML LOADER v1] Preprocessor loaded successfully.")

        return _model, _preprocessor, _metadata

def get_model():
    global _model
    if _model is None:
        load_artifacts()
    return _model

def get_preprocessor():
    global _preprocessor
    if _preprocessor is None:
        load_artifacts()
    return _preprocessor

def get_metadata():
    global _metadata
    if _metadata is None:
        load_artifacts()
    return _metadata
