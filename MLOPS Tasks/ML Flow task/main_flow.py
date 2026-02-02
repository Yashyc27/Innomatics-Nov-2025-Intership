import pandas as pd
import optuna
import mlflow
import mlflow.sklearn
from prefect import task, flow
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import f1_score
from src.preprocess import TextCleaner

# --- Task 1: Data Ingestion ---
@task(name="Load_and_Prepare_Data")
def load_data():
    df = pd.read_csv("data/reviews_badminton_data.csv")
    df['sentiment'] = df['Ratings'].apply(lambda x: 1 if x >= 4 else 0)
    return train_test_split(df['Review text'], df['sentiment'], test_size=0.2, random_state=42)

# --- Task 2: Objective Function ---
def objective(trial, X_train, X_test, y_train, y_test):
    classifier_name = trial.suggest_categorical("classifier", ["LogisticRegression", "NaiveBayes"])
    run_name = f"Trial_{trial.number}_{classifier_name}"
    
    with mlflow.start_run(run_name=run_name, nested=True):
        if classifier_name == "LogisticRegression":
            model = LogisticRegression(C=trial.suggest_float("C", 0.1, 10.0, log=True))
        else:
            model = MultinomialNB(alpha=trial.suggest_float("alpha", 0.1, 2.0))

        pipeline = Pipeline([
            ('cleaner', TextCleaner()), 
            ('tfidf', TfidfVectorizer(max_features=2500)), 
            ('clf', model)
        ])
        
        pipeline.fit(X_train, y_train)
        score = f1_score(y_test, pipeline.predict(X_test))

        mlflow.log_params(trial.params)
        mlflow.log_metric("f1_score", score)
        return score

# --- Task 3: Main Workflow ---
@flow(name="Yonex_Sentiment_Analysis_Workflow")
def sentiment_pipeline():
    mlflow.set_experiment("Yonex_Sentiment_Project")
    X_train, X_test, y_train, y_test = load_data()

    study = optuna.create_study(direction="maximize")
    
    with mlflow.start_run(run_name="Optimization_Batch_Parent"):
        study.optimize(lambda t: objective(t, X_train, X_test, y_train, y_test), n_trials=5)

        # Log artifacts
        best_report = f"Best F1 Score: {study.best_value}\nBest Params: {study.best_params}"
        with open("best_run_summary.txt", "w") as f:
            f.write(best_report)
        mlflow.log_artifact("best_run_summary.txt")

        # Re-train and Register the winning model
        best_clf_name = study.best_params['classifier']
        if best_clf_name == "LogisticRegression":
            best_clf = LogisticRegression(C=study.best_params['C'])
        else:
            best_clf = MultinomialNB(alpha=study.best_params['alpha'])

        best_pipeline = Pipeline([
            ('cleaner', TextCleaner()), 
            ('tfidf', TfidfVectorizer(max_features=2500)), 
            ('clf', best_clf)
        ])
        best_pipeline.fit(X_train, y_train)

        # REGISTER MODEL HERE
        mlflow.sklearn.log_model(
            sk_model=best_pipeline,
            name="model",  # Use 'name' instead of 'artifact_path'
            registered_model_name="YonexSentimentModel"
)

if __name__ == "__main__":
    sentiment_pipeline.serve(name="Daily_Yonex_Retraining", cron="0 0 * * *")