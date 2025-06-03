import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer

# Load the saved model and vectorizer
model = pickle.load(open('models/spam_classifier.pkl', 'rb'))
vectorizer = pickle.load(open('models/vectorizer.pkl', 'rb'))

def preprocess_text(text):
    # Basic cleaning
    text = re.sub(r'\W', ' ', text)
    text = text.lower()
    return text

def predict_spam(email_text):
    processed_text = preprocess_text(email_text)
    vect_text = vectorizer.transform([processed_text])
    prediction = model.predict(vect_text)
    return "Spam" if prediction[0] == 1 else "Not Spam"
