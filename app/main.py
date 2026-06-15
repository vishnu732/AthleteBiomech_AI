import streamlit as st

st.set_page_config(
    page_title="AthleteBiomech AI",
    page_icon="🏃",
    layout="wide"
)

st.title("🏃 AthleteBiomech AI")
st.subheader("Multi-Sport Injury Risk + Video-Based Body Load Analysis")

st.write(
    """
    AthleteBiomech AI is an AI-powered sports injury risk analysis platform.
    It combines athlete workload data with video-based biomechanical movement analysis
    to detect risky posture, estimate body-load stress, and generate injury-prevention recommendations.
    """
)

st.markdown("### What this app will analyze")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Workload Risk", "Coming Soon")
    st.write("Training frequency, match load, rest days, age, and previous injury.")

with col2:
    st.metric("Video Biomechanics", "Coming Soon")
    st.write("Pose tracking, joint angles, landing impact, posture risk.")

with col3:
    st.metric("Coach Report", "Coming Soon")
    st.write("Risk score, risky body areas, movement issues, and recommendations.")

st.markdown("### Supported Sports")

sports = [
    "Cricket",
    "Soccer",
    "Basketball",
    "Tennis",
    "Running",
    "Weightlifting"
]

selected_sport = st.selectbox("Choose a sport to analyze:", sports)

st.success(f"Selected Sport: {selected_sport}")

st.info("Next step: We will build the Workload Injury Risk Predictor.")