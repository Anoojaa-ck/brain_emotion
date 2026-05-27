# # ===================== Core Libraries =====================
# import numpy as np
# from tensorflow.keras.models import load_model
#
# # ===================== Paths =====================
# MODEL_PATH = r"C:\Users\anooj\PycharmProjects\brainemotion\myapp\_best_model.h5"
# TXT_INPUT_PATH = r"C:\Users\anooj\OneDrive\Desktop\dataset6.txt"
#
# # ===================== Class Labels (ORDER MATTERS) =====================
# # Replace with the exact order from LabelEncoder.classes_
# CLASS_NAMES = ['angry', 'happy', 'sad']   # <-- example
#
# # ===================== Load Model =====================
# model = load_model(MODEL_PATH)
# print("✅ Model loaded")
#
# # ===================== Prediction Function =====================
# def predict_from_txt(txt_path, model, class_names):
#     # Load comma-separated values (scientific notation supported)
#     features = np.loadtxt(txt_path, delimiter=',')
#
#     # Ensure shape is (1, n_features)
#     if features.ndim == 1:
#         features = features.reshape(1, -1)
#
#     # Validate feature count
#     expected_features = model.input_shape[1]
#     if features.shape[1] != expected_features:
#         raise ValueError(
#             f"Feature mismatch! Expected {expected_features}, got {features.shape[1]}"
#         )
#
#     # Reshape for GRU input: (samples, timesteps, channels)
#     X = features.reshape(features.shape[0], features.shape[1], 1)
#
#     # Predict
#     probabilities = model.predict(X)
#     predicted_indices = np.argmax(probabilities, axis=1)
#     predicted_labels = [class_names[i] for i in predicted_indices]
#
#     return predicted_labels, probabilities
#
# # ===================== Run Prediction =====================
# labels, probs = predict_from_txt(TXT_INPUT_PATH, model, CLASS_NAMES)
#
# # ===================== Output =====================
# for i, label in enumerate(labels):
#     print(f"\n🧠 Sample {i+1}")
#     print("Predicted Emotion:", label)
#     print("Probabilities:")
#     for cls, p in zip(CLASS_NAMES, probs[i]):
#         print(f"  {cls}: {p:.4f}")

import numpy as np
from tensorflow.keras.models import load_model

MODEL_PATH = r"C:\Users\anooj\PycharmProjects\brainemotion\myapp\_best_model.h5"
# MODEL_PATH = r"C:\Users\anooj\PycharmProjects\brainemotion\myapp\_best_model.h5"
CLASS_NAMES = ['angry', 'happy', 'sad']

model = load_model(MODEL_PATH)

def predict_from_txt(txt_path):
    features = np.loadtxt(txt_path, delimiter=',')

    if features.ndim == 1:
        features = features.reshape(1, -1)

    expected_features = model.input_shape[1]
    if features.shape[1] != expected_features:
        raise ValueError(
            f"Feature mismatch! Expected {expected_features}, got {features.shape[1]}"
        )

    X = features.reshape(features.shape[0], features.shape[1], 1)

    probabilities = model.predict(X)
    predicted_index = int(np.argmax(probabilities, axis=1)[0])
    predicted_label = CLASS_NAMES[predicted_index]

    probs_dict = {
        CLASS_NAMES[i]: float(probabilities[0][i])
        for i in range(len(CLASS_NAMES))
    }

    return predicted_label, probs_dict
