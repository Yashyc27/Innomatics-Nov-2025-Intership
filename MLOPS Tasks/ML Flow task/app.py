from flask import Flask, render_template, request
import mlflow.pyfunc
import pandas as pd
from src.preprocess import TextCleaner

app = Flask(__name__)

# Fetching the model via Tagging management
model_uri = "models:/YonexSentimentModel@production"

try:
    model = mlflow.pyfunc.load_model(model_uri)
    status = "Model Loaded Successfully"
except:
    model = None
    status = "Model Not Found - Check MLflow Registry"

@app.route('/')
def home():
    return render_template('index.html', status=status)

@app.route('/predict', methods=['POST'])
def predict():
    if model and request.method == 'POST':
        review = request.form.get('review')
        prediction = model.predict(pd.Series([review]))[0]
        result = "Positive" if prediction == 1 else "Negative"
        return render_template('index.html', prediction_text=f"Sentiment: {result}")
    return "Model Error"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)