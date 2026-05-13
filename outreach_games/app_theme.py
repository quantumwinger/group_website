import matplotlib.pyplot as plt
import streamlit as st


HTML_THEME = {
    "bg": "#0f1117",
    "card": "#1a1d2e",
    "card_border": "#2a2d42",
    "plot_bg": "#12141f",
    "primary": "#e2e8f0",
    "muted": "#94a3b8",
    "dim": "#64748b",
    "accent": "#3b82f6",
    "accent_red": "#ef4444",
    "accent_purple": "#8b5cf6",
    "accent_amber": "#f59e0b",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
}


plt.rcParams.update(
    {
        "figure.facecolor": HTML_THEME["bg"],
        "axes.facecolor": HTML_THEME["plot_bg"],
        "axes.edgecolor": HTML_THEME["card_border"],
        "axes.labelcolor": HTML_THEME["primary"],
        "axes.titlecolor": HTML_THEME["primary"],
        "xtick.color": HTML_THEME["muted"],
        "ytick.color": HTML_THEME["muted"],
        "text.color": HTML_THEME["primary"],
        "legend.facecolor": HTML_THEME["card"],
        "legend.edgecolor": HTML_THEME["card_border"],
        "legend.labelcolor": HTML_THEME["primary"],
        "grid.color": HTML_THEME["card_border"],
    }
)


def apply_html_theme():
    st.markdown(
        f"""
        <style>
        html, body, [class*="st-"], [data-testid="stAppViewContainer"] {{
            font-family: Inter, system-ui, sans-serif;
        }}
        .stApp {{
            background: {HTML_THEME["bg"]};
            color: {HTML_THEME["primary"]};
        }}
        [data-testid="stSidebar"], [data-testid="stSidebarContent"] {{
            background: {HTML_THEME["card"]};
            color: {HTML_THEME["primary"]};
        }}
        h1, h2, h3, h4, h5, h6, p, label, span, div {{
            color: inherit;
        }}
        .stMarkdown, .stMarkdown p, .stSlider label, .stMetric label, .stMetric div {{
            color: {HTML_THEME["primary"]};
        }}
        [data-testid="stMetricValue"] {{
            color: {HTML_THEME["primary"]};
        }}
        [data-testid="stMetricLabel"] {{
            color: {HTML_THEME["muted"]};
        }}
        .stButton button {{
            background: {HTML_THEME["card"]};
            border: 1px solid {HTML_THEME["card_border"]};
            color: {HTML_THEME["primary"]};
        }}
        .stButton button:hover {{
            border-color: {HTML_THEME["accent"]};
            color: {HTML_THEME["primary"]};
        }}
        .stAlert {{
            background: {HTML_THEME["card"]};
            color: {HTML_THEME["primary"]};
        }}
        hr {{
            border-color: {HTML_THEME["card_border"]};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
