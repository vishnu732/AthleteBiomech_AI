import streamlit as st


def apply_global_styles():
    st.markdown(
        """
        <style>
        /* Main app background */
        .stApp {
            background: radial-gradient(circle at top left, #10213f 0%, #0B1120 35%, #050816 100%);
            color: #F9FAFB;
        }

        /* Hide default Streamlit menu/footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Main container */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }

        /* Page title text */
        h1, h2, h3 {
            color: #F9FAFB !important;
            letter-spacing: -0.03em;
        }

        p, li, span, div {
            color: #E5E7EB;
        }

        /* Metric cards */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #111827 0%, #1F2937 100%);
            border: 1px solid rgba(0, 229, 255, 0.18);
            padding: 1.1rem;
            border-radius: 18px;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.28);
        }

        [data-testid="stMetricLabel"] {
            color: #9CA3AF !important;
        }

        [data-testid="stMetricValue"] {
            color: #00E5FF !important;
            font-weight: 800;
        }

        /* Input widgets */
        .stSelectbox, .stNumberInput, .stSlider, .stTextInput, .stFileUploader {
            background: rgba(17, 24, 39, 0.4);
            border-radius: 16px;
        }

        /* Buttons */
        .stButton > button,
        .stDownloadButton > button {
            background: linear-gradient(90deg, #00E5FF 0%, #22C55E 100%);
            color: #020617;
            border: none;
            border-radius: 14px;
            font-weight: 800;
            padding: 0.7rem 1.2rem;
            box-shadow: 0 10px 24px rgba(0, 229, 255, 0.18);
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 28px rgba(34, 197, 94, 0.25);
        }

        /* Tables and dataframes */
        [data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        /* Cards */
        .hero-card {
            background: linear-gradient(135deg, rgba(17, 24, 39, 0.96), rgba(30, 41, 59, 0.92));
            border: 1px solid rgba(0, 229, 255, 0.22);
            border-radius: 26px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.32);
        }

        .hero-title {
            font-size: 2.5rem;
            font-weight: 900;
            color: #F9FAFB;
            margin-bottom: 0.3rem;
            letter-spacing: -0.06em;
        }

        .hero-subtitle {
            font-size: 1.05rem;
            color: #9CA3AF;
            margin-bottom: 1.2rem;
        }

        .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin-top: 1rem;
        }

        .pill {
            background: rgba(0, 229, 255, 0.10);
            border: 1px solid rgba(0, 229, 255, 0.26);
            color: #A5F3FC;
            padding: 0.4rem 0.75rem;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 700;
        }

        .section-card {
            background: rgba(17, 24, 39, 0.78);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 22px;
            padding: 1.4rem;
            margin: 1rem 0;
            box-shadow: 0 18px 36px rgba(0, 0, 0, 0.22);
        }

        .risk-low {
            background: rgba(34, 197, 94, 0.14);
            color: #86EFAC;
            border: 1px solid rgba(34, 197, 94, 0.35);
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            font-weight: 900;
            display: inline-block;
        }

        .risk-medium {
            background: rgba(245, 158, 11, 0.14);
            color: #FCD34D;
            border: 1px solid rgba(245, 158, 11, 0.35);
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            font-weight: 900;
            display: inline-block;
        }

        .risk-high {
            background: rgba(239, 68, 68, 0.14);
            color: #FCA5A5;
            border: 1px solid rgba(239, 68, 68, 0.35);
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            font-weight: 900;
            display: inline-block;
        }

        .muted-text {
            color: #9CA3AF;
            font-size: 0.95rem;
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(0, 229, 255, 0.4), transparent);
            margin: 1.4rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_hero(title, subtitle, pills=None):
    if pills is None:
        pills = []

    pill_html = "".join([f"<span class='pill'>{pill}</span>" for pill in pills])

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
            <div class="pill-row">
                {pill_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_section_card(title, body):
    st.markdown(
        f"""
        <div class="section-card">
            <h3>{title}</h3>
            <p class="muted-text">{body}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_risk_badge(risk_level):
    level = str(risk_level).upper()

    if level == "LOW":
        css_class = "risk-low"
    elif level == "MEDIUM":
        css_class = "risk-medium"
    else:
        css_class = "risk-high"

    st.markdown(
        f"<span class='{css_class}'>{level} RISK</span>",
        unsafe_allow_html=True
    )