import tensorflow as tf
import os

MODEL_PATH = r"dl\model\best_model.keras"

print("Checking model path...")
print("Exists:", os.path.exists(MODEL_PATH))
print("Loading model...")

model = tf.keras.models.load_model(MODEL_PATH)

print("✅ Model loaded successfully!")
print(model.summary())