import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.ui_styles import apply_global_styles, render_hero, render_section_card


st.set_page_config(
    page_title="AthleteBiomech AI",
    page_icon="🏃",
    layout="wide"
)

apply_global_styles()


render_hero(
    title="AthleteBiomech AI",
    subtitle="AI-powered sports injury risk, workload monitoring, and video biomechanics analysis platform.",
    pills=[
        "Workload Risk",
        "Video Biomechanics",
        "Target Player Analysis",
        "Coach PDF Report",
        "Multi-Sport"
    ]
)


st.markdown(
    """
    AthleteBiomech AI is a sports analytics prototype that combines **athlete workload data**
    and **video-based movement analysis** to estimate injury risk, highlight risky body areas,
    and generate coach-style prevention recommendations.
    """
)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


st.markdown("## Platform Modules")

col1, col2, col3 = st.columns(3)

with col1:
    render_section_card(
        "Workload Intelligence",
        "Predict injury risk using sport, age, training days, match load, rest days, training intensity, and previous injury history."
    )

with col2:
    render_section_card(
        "Video Biomechanics",
        "Upload sports videos and analyze target-player posture, joint angles, movement risk, and sport-specific mechanics."
    )

with col3:
    render_section_card(
        "Coach Report",
        "Combine workload and movement analysis into a professional downloadable coach-style PDF injury risk report."
    )


st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


st.markdown("## Quick Dashboard")

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric("Sports Supported", "6+")

with metric_col2:
    st.metric("Risk Engines", "2")

with metric_col3:
    st.metric("Report Export", "PDF")

with metric_col4:
    st.metric("Analysis Type", "AI + Rules")


st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


st.markdown("## Supported Sports")

sports = [
    "Cricket",
    "Soccer",
    "Basketball",
    "Tennis",
    "Running",
    "Weightlifting"
]

selected_sport = st.selectbox("Choose a sport to explore:", sports)

st.success(f"Selected Sport: {selected_sport}")


st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


st.markdown("## Start Analysis")

nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    st.markdown("### 1. Workload Risk")
    st.write("Enter athlete workload details and predict injury risk.")
    st.page_link("pages/1_Workload_Risk.py", label="Open Workload Predictor", icon="📊")

with nav_col2:
    st.markdown("### 2. Video Analyzer")
    st.write("Upload a sports video and analyze movement mechanics.")
    st.page_link("pages/2_Video_Analyzer.py", label="Open Video Analyzer", icon="🎥")

with nav_col3:
    st.markdown("### 3. Coach Report")
    st.write("Generate a combined injury risk report with PDF export.")
    st.page_link("pages/3_Report.py", label="Open Coach Report", icon="📄")


st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


st.info(
    "Recommended flow: First run Workload Risk, then Video Analyzer, then generate the Coach Report."
)