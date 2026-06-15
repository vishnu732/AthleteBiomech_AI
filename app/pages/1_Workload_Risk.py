import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root folder to Python path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from src.risk_engine import calculate_workload_risk

st.set_page_config(
    page_title="Workload Injury Risk",
    page_icon="⚠️",
    layout="wide"
)

st.title("⚠️ Workload Injury Risk Predictor")

st.write(
    """
    This module estimates an athlete's injury risk based on workload, match frequency,
    rest days, age, previous injury history, and training intensity.
    """
)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    athlete_name = st.text_input("Athlete Name", "Sample Athlete")

    sport = st.selectbox(
        "Select Sport",
        ["Cricket", "Soccer", "Basketball", "Tennis", "Running", "Weightlifting"]
    )

    age = st.number_input(
        "Age",
        min_value=10,
        max_value=60,
        value=22
    )

    training_days = st.slider(
        "Training Days Per Week",
        min_value=0,
        max_value=7,
        value=4
    )

with col2:
    matches_30_days = st.slider(
        "Matches / Competitions in Last 30 Days",
        min_value=0,
        max_value=15,
        value=4
    )

    rest_days = st.slider(
        "Rest Days Per Week",
        min_value=0,
        max_value=7,
        value=2
    )

    previous_injury = st.radio(
        "Previous Injury History?",
        ["No", "Yes"],
        horizontal=True
    )

    training_intensity = st.selectbox(
        "Training Intensity",
        ["Low", "Medium", "High"]
    )

st.markdown("---")

if st.button("Predict Injury Risk"):
    result = calculate_workload_risk(
        age=age,
        sport=sport,
        training_days=training_days,
        matches_30_days=matches_30_days,
        rest_days=rest_days,
        previous_injury=previous_injury,
        training_intensity=training_intensity
    )

    risk_score = result["risk_score"]
    risk_level = result["risk_level"]

    st.subheader(f"Risk Report for {athlete_name}")

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.metric("Injury Risk Score", f"{risk_score}%")

    with metric_col2:
        st.metric("Risk Level", risk_level)

    with metric_col3:
        st.metric("Sport", sport)

    st.markdown("### Overall Risk Meter")
    st.progress(risk_score / 100)

    if risk_level == "LOW":
        st.success("LOW Risk: Current workload appears manageable.")
    elif risk_level == "MEDIUM":
        st.warning("MEDIUM Risk: Athlete may need better recovery and workload control.")
    else:
        st.error("HIGH Risk: Athlete has a high injury-risk profile.")

    st.markdown("---")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("### Risk Factor Breakdown")

        factor_df = pd.DataFrame({
            "Risk Factor": list(result["factor_scores"].keys()),
            "Score": list(result["factor_scores"].values())
        })

        st.bar_chart(
            factor_df,
            x="Risk Factor",
            y="Score"
        )

    with chart_col2:
        st.markdown("### Sport-Specific Body Areas")

        body_df = pd.DataFrame(result["body_area_risks"])
        st.dataframe(body_df, use_container_width=True)

    st.markdown("---")

    st.markdown("### Main Risk Reasons")

    if result["reasons"]:
        for reason in result["reasons"]:
            st.write(f"- {reason}")
    else:
        st.write("- No major risk factors detected.")

    st.markdown("### Recommendations")

    if risk_level == "HIGH":
        st.write("- Reduce training load temporarily.")
        st.write("- Increase rest and recovery days.")
        st.write("- Add mobility and strengthening work.")
        st.write("- Monitor pain or discomfort after training.")
        st.write("- Consider coach or physiotherapist review if pain is present.")
    elif risk_level == "MEDIUM":
        st.write("- Maintain balanced training and recovery.")
        st.write("- Avoid sudden workload increases.")
        st.write("- Add warm-up, stretching, and cooldown routines.")
        st.write("- Track weekly workload changes.")
    else:
        st.write("- Continue current routine with proper recovery.")
        st.write("- Keep tracking workload weekly.")
        st.write("- Maintain strength and mobility exercises.")