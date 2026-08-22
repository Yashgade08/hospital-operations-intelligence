"""Train and evaluate no-show candidates without using post-appointment data."""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).parents[2]
FEATURES = ["age", "gender", "previous_appointments", "previous_no_shows", "previous_cancellations", "days_between_booking_and_appointment", "appointment_hour", "appointment_day", "distance_km"]

def train() -> dict[str, float]:
    data = pd.read_csv(ROOT / "data" / "appointments.csv")
    x_train, x_test, y_train, y_test = train_test_split(data[FEATURES], data.no_show, test_size=.2, random_state=42, stratify=data.no_show)
    categorical = ["gender"]
    numeric = [column for column in FEATURES if column not in categorical]
    preprocess = ColumnTransformer([("numeric", StandardScaler(), numeric), ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical)])
    candidates = {"logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"), "random_forest": RandomForestClassifier(n_estimators=250, random_state=42, class_weight="balanced")}
    scores = {}
    best = None
    best_model = None
    for name, estimator in candidates.items():
        model = Pipeline([("preprocess", preprocess), ("model", estimator)])
        model.fit(x_train, y_train)
        probabilities = model.predict_proba(x_test)[:, 1]
        predictions = (probabilities >= .5).astype(int)
        scores[name] = {"precision": precision_score(y_test, predictions, zero_division=0), "recall": recall_score(y_test, predictions, zero_division=0), "f1": f1_score(y_test, predictions, zero_division=0), "roc_auc": roc_auc_score(y_test, probabilities)}
        if best is None or scores[name]["f1"] > scores[best]["f1"]:
            best = name
            best_model = model
    models = ROOT / "ml" / "models"; models.mkdir(exist_ok=True)
    joblib.dump(best_model, models / "no_show_model.joblib")
    (models / "no_show_metrics.json").write_text(__import__("json").dumps({"best_model": best, "scores": scores}, indent=2))
    return scores[best]

if __name__ == "__main__":
    print(train())
