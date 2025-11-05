from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib
import os

# 📦 Sample training data
texts = [
    "old jeans and t-shirts",          # Clothes
    "bread and vegetables",            # Food
    "used smartphone with charger",    # Electronics    
    "winter jacket and gloves",        # Clothes
    "canned soup and rice",            # Food
    "broken laptop for recycling",     # Electronics
]

labels = [
    "Clothes",
    "Food",
    "Electronics",
    "Clothes",
    "Food",
    "Electronics"
]

# Text vectorization
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(texts)

#  Train model
model = MultinomialNB()
model.fit(X, labels)

# Save model and vectorizer to ai_model folder
os.makedirs("ai_model", exist_ok=True)
joblib.dump(model, "ai_model/model.pkl")
joblib.dump(vectorizer, "ai_model/vectorizer.pkl")

print("✅ AI model and vectorizer saved to ai_model/")
