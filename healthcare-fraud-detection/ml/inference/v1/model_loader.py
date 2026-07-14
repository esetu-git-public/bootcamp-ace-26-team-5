import os
import joblib

# Enforce PyTorch backend for Keras 3 prior to imports
os.environ["KERAS_BACKEND"] = "torch"
import keras

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_PATH = os.path.join(BASE_DIR, "models", "best_model.keras")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "models", "preprocessor_keras.pkl")

_model = None
_preprocessor = None

def load_artifacts():
    """
    Load Keras Deep Learning model and preprocessor pkl as singletons.
    """
    global _model, _preprocessor

    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Keras model not found at: {MODEL_PATH}")
        print("Loading Keras 3 Deep Learning Model (PyTorch Backend)...")
        _model = keras.models.load_model(MODEL_PATH)
        print("Keras 3 Model Loaded successfully")

    if _preprocessor is None:
        if not os.path.exists(PREPROCESSOR_PATH):
            raise FileNotFoundError(f"Preprocessor pkl not found at: {PREPROCESSOR_PATH}")
        print("Loading Preprocessor...")
        _preprocessor = joblib.load(PREPROCESSOR_PATH)
        print("Preprocessor Loaded successfully")

    return _model, _preprocessor
