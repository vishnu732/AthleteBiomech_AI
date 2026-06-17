import pandas as pd
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT_DIR / "data" / "synthetic_athlete_workload.csv"
MODEL_PATH = ROOT_DIR / "models" / "injury_risk_model.pkl"

df = pd.read_csv(DATA_PATH)

features = [
    "age",
    "sport",
    "training_days",
    "matches_30_days",
    "rest_days",
    "previous_injury",
    "training_intensity"
]

target = "injury_risk_score"

X = df[features]
y = df[target]

numeric_features = [
    "age",
    "training_days",
    "matches_30_days",
    "rest_days"
]

categorical_features = [
    "sport",
    "previous_injury",
    "training_intensity"
]

preprocessor = ColumnTransformer(
    transformers=[
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("numeric", "passthrough", numeric_features)
    ]
)

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    random_state=42
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

pipeline.fit(X_train, y_train)

predictions = pipeline.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("Model training completed.")
print(f"Mean Absolute Error: {mae:.2f}")
print(f"R2 Score: {r2:.2f}")

# Train final model on full dataset before saving
pipeline.fit(X, y)

joblib.dump(pipeline, MODEL_PATH)

print(f"Model saved successfully: {MODEL_PATH}")