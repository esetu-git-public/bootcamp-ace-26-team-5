import os
import joblib
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "best_model.keras")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "..", "model", "preprocessor.pkl")

_model = None
_preprocessor = None


def load_artifacts():

    global _model, _preprocessor

    if _model is None:
        print("Loading TensorFlow Model...")
        _model = tf.keras.models.load_model(MODEL_PATH)
        print("✅ TensorFlow Model Loaded")

    if _preprocessor is None:
        print("Loading Preprocessor...")
        _preprocessor = joblib.load(PREPROCESSOR_PATH)
        print("✅ Preprocessor Loaded")

    return _model, _preprocessor


if __name__ == "__main__":

    model, preprocessor = load_artifacts()

    print("\n===================================")
    print("Everything Loaded Successfully!")
    print("===================================")