import optuna
import mlflow
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

def objective(trial, X_train, X_test, y_train, y_test):
    
    c_val = trial.suggest_float("C", 1e-3, 10.0, log=True)
    solver = trial.suggest_categorical("solver", ["liblinear", "lbfgs"])

    with mlflow.start_run(nested=True):
        
        pipeline = Pipeline([
            ('cleaner', TextCleaner()),
            ('tfidf', TfidfVectorizer(max_features=trial.suggest_int("max_features", 1000, 5000))),
            ('clf', LogisticRegression(C=c_val, solver=solver))
        ])

        
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        score = f1_score(y_test, y_pred) 

        
        mlflow.log_params(trial.params)
        mlflow.log_metric("f1_score", score)
         
        return score