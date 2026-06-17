import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "synthetic_athlete_workload.csv"

sports = ["Cricket", "Soccer", "Basketball", "Tennis", "Running", "Weightlifting"]
intensities = ["Low", "Medium", "High"]

rows = []

for _ in range(1500):
    age = np.random.randint(14, 41)
    sport = np.random.choice(sports)
    training_days = np.random.randint(1, 8)
    matches_30_days = np.random.randint(0, 14)
    rest_days = np.random.randint(0, 6)
    previous_injury = np.random.choice(["No", "Yes"], p=[0.72, 0.28])
    training_intensity = np.random.choice(intensities, p=[0.30, 0.45, 0.25])

    risk_score = 0

    if age < 18:
        risk_score += 8
    elif age >= 30:
        risk_score += 12
    else:
        risk_score += 4

    if training_days >= 6:
        risk_score += 25
    elif training_days >= 4:
        risk_score += 15
    else:
        risk_score += 5

    if matches_30_days >= 8:
        risk_score += 20
    elif matches_30_days >= 4:
        risk_score += 12
    else:
        risk_score += 4

    if rest_days <= 1:
        risk_score += 20
    elif rest_days <= 3:
        risk_score += 10
    else:
        risk_score += 2

    if previous_injury == "Yes":
        risk_score += 18

    if training_intensity == "High":
        risk_score += 15
    elif training_intensity == "Medium":
        risk_score += 8
    else:
        risk_score += 3

    sport_modifier = {
        "Cricket": 5,
        "Soccer": 6,
        "Basketball": 7,
        "Tennis": 5,
        "Running": 6,
        "Weightlifting": 7
    }

    risk_score += sport_modifier[sport]
    risk_score += np.random.normal(0, 5)
    risk_score = int(np.clip(risk_score, 5, 100))

    if risk_score <= 30:
        risk_level = "LOW"
    elif risk_score <= 65:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    rows.append({
        "age": age,
        "sport": sport,
        "training_days": training_days,
        "matches_30_days": matches_30_days,
        "rest_days": rest_days,
        "previous_injury": previous_injury,
        "training_intensity": training_intensity,
        "injury_risk_score": risk_score,
        "risk_level": risk_level
    })

df = pd.DataFrame(rows)
df.to_csv(DATA_PATH, index=False)

print(f"Dataset created successfully: {DATA_PATH}")
print(df.head())