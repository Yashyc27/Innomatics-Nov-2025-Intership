import re
import nltk
import joblib
from flask import Flask, render_template, request
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

app = Flask(__name__)

nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

model = joblib.load('best_sentiment_model.pkl')
vectorizer = joblib.load('tfidf_ngram_vectorizer.pkl')

def clean_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', str(text).lower())
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return " ".join(words)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        review = request.form['review']
        cleaned_review = clean_text(review)
        vectorized_review = vectorizer.transform([cleaned_review])
        prediction = model.predict(vectorized_review)[0]
        
        sentiment = "Positive" if prediction == 1 else "Negative"
        return render_template('index.html', prediction_text=f'Sentiment: {sentiment}', original_review=review)

if __name__ == "__main__":
    # host='0.0.0.0' tells Flask to listen on all public IPs of the EC2
    # port=5000 is the standard port for Flask
    app.run(host='0.0.0.0', port=5000)