import joblib
import os

# Dynamically get full path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'model.pkl')
vectorizer_path = os.path.join(BASE_DIR, 'vectorizer.pkl')

# Load model and vectorizer
model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

def predict_category(title, description):
    if not title.strip() and not description.strip():
        print("⚠️ Empty input text → Defaulting to 'Uncategorized'")
        return "Uncategorized"

    if model is None or vectorizer is None:
        print("❌ Model or vectorizer not loaded")
        return "Uncategorized"

    try:
        text = f"{title} {description}".strip()
        vectorized = vectorizer.transform([text])
        prediction = model.predict(vectorized)

        predicted = prediction[0] if prediction.size > 0 else None
        if not predicted or not predicted.strip():
            print(f"⚠️ Prediction failed for → {text}")
            return "Uncategorized"

        clean_category = predicted.strip().title()  # Normalize
        print(f"✅ Predicted category: {clean_category}")
        return clean_category

    except Exception as e:
        print("❌ Prediction error:", e)
        return "Uncategorized"
