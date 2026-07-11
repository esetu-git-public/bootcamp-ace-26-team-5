import joblib
import os

PREPROCESSOR_PATH = r"dl\model\preprocessor.pkl"

print("Checking preprocessor path...")
print("Exists:", os.path.exists(PREPROCESSOR_PATH))
print("Loading preprocessor...")

preprocessor = joblib.load(PREPROCESSOR_PATH)

print("✅ Preprocessor loaded successfully!")
print(type(preprocessor))