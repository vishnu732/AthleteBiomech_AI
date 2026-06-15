def calculate_workload_risk(
    age,
    sport,
    training_days,
    matches_30_days,
    rest_days,
    previous_injury,
    training_intensity
):
    reasons = []

    factor_scores = {
        "Age Risk": 0,
        "Training Load": 0,
        "Match Frequency": 0,
        "Recovery Risk": 0,
        "Previous Injury": 0,
        "Training Intensity": 0
    }

    if age < 18:
        factor_scores["Age Risk"] = 8
        reasons.append("Young athlete: growth-stage athletes may need careful workload control.")
    elif age >= 30:
        factor_scores["Age Risk"] = 12
        reasons.append("Higher age group: recovery time may be slower.")
    else:
        factor_scores["Age Risk"] = 4

    if training_days >= 6:
        factor_scores["Training Load"] = 25
        reasons.append("Very high training frequency.")
    elif training_days >= 4:
        factor_scores["Training Load"] = 15
        reasons.append("Moderate-to-high training frequency.")
    else:
        factor_scores["Training Load"] = 5

    if matches_30_days >= 8:
        factor_scores["Match Frequency"] = 20
        reasons.append("High match frequency in the last 30 days.")
    elif matches_30_days >= 4:
        factor_scores["Match Frequency"] = 12
        reasons.append("Moderate match frequency.")
    else:
        factor_scores["Match Frequency"] = 4

    if rest_days <= 1:
        factor_scores["Recovery Risk"] = 20
        reasons.append("Low recovery time between training/matches.")
    elif rest_days <= 3:
        factor_scores["Recovery Risk"] = 10
        reasons.append("Recovery days are slightly low.")
    else:
        factor_scores["Recovery Risk"] = 2

    if previous_injury == "Yes":
        factor_scores["Previous Injury"] = 18
        reasons.append("Previous injury history increases future injury risk.")
    else:
        factor_scores["Previous Injury"] = 0

    if training_intensity == "High":
        factor_scores["Training Intensity"] = 15
        reasons.append("High training intensity increases body-load stress.")
    elif training_intensity == "Medium":
        factor_scores["Training Intensity"] = 8
        reasons.append("Medium training intensity creates moderate load.")
    else:
        factor_scores["Training Intensity"] = 3

    risk_score = sum(factor_scores.values())
    risk_score = min(risk_score, 100)

    if risk_score <= 30:
        risk_level = "LOW"
    elif risk_score <= 65:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    sport_risk_map = {
        "Cricket": ["Shoulder", "Elbow", "Lower Back", "Knee"],
        "Soccer": ["Knee", "Ankle", "Hamstring", "Hip"],
        "Basketball": ["Knee", "Ankle", "Landing Impact", "Hip"],
        "Tennis": ["Shoulder", "Elbow", "Wrist", "Lower Back"],
        "Running": ["Knee", "Ankle", "Hip", "Shin"],
        "Weightlifting": ["Lower Back", "Knee", "Shoulder", "Hip"]
    }

    risky_areas = sport_risk_map.get(sport, ["General Body Load"])

    body_area_risks = []
    for area in risky_areas:
        body_area_risks.append({
            "Body Area": area,
            "Risk": risk_level
        })

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
        "risky_areas": risky_areas,
        "factor_scores": factor_scores,
        "body_area_risks": body_area_risks
    }