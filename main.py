import time

import pandas as pd
import streamlit as st

from chatbot import (
    get_history_response,
    get_recommendation_response,
    get_wishlist_response,
    respond_to_message,
)
from log_parser import get_user_ids, load_logs, process_user_data
from recommender import analytics_summary


st.set_page_config(
    page_title="Log Analyzer Chatbot",
    page_icon=">",
    layout="wide",
)


@st.cache_data
def load_project_data():
    """Load and process data once for better Streamlit performance."""
    logs_df = load_logs("sample_data.json")
    user_data = process_user_data(logs_df)
    analytics = analytics_summary(logs_df)
    return logs_df, user_data, analytics


def apply_professional_theme():
    """Add custom CSS for a polished professional dashboard."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', Segoe UI, sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(34, 211, 238, 0.12), transparent 32%),
                radial-gradient(circle at top right, rgba(245, 158, 11, 0.09), transparent 28%),
                linear-gradient(135deg, #0F172A 0%, #111827 48%, #020617 100%);
            color: #E5E7EB;
        }

        h1, h2, h3, p, label, span, div {
            color: #E5E7EB;
        }

        h1 {
            color: #F8FAFC;
            font-weight: 800;
            letter-spacing: 0;
        }

        [data-testid="stSidebar"] {
            background: #0B1220;
            border-right: 1px solid rgba(148, 163, 184, 0.18);
            box-shadow: 12px 0 34px rgba(2, 6, 23, 0.38);
        }

        .terminal-panel {
            border: 1px solid rgba(148, 163, 184, 0.18);
            background: rgba(15, 23, 42, 0.84);
            box-shadow: 0 20px 48px rgba(2, 6, 23, 0.36);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 18px;
        }

        .metric-card {
            border: 1px solid rgba(34, 211, 238, 0.20);
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.92));
            box-shadow: 0 14px 28px rgba(2, 6, 23, 0.28);
            border-radius: 12px;
            padding: 16px;
            min-height: 92px;
        }

        .metric-value {
            color: #67E8F9;
            font-size: 26px;
            font-weight: 800;
            line-height: 1.2;
        }

        .metric-label {
            color: #94A3B8;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .stButton > button {
            background: linear-gradient(135deg, #0891B2, #2563EB);
            color: #FFFFFF;
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 8px;
            box-shadow: 0 12px 22px rgba(37, 99, 235, 0.24);
            transition: 0.2s ease;
            width: 100%;
            font-weight: 700;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #06B6D4, #3B82F6);
            color: #FFFFFF;
            border: 1px solid rgba(255, 255, 255, 0.24);
            box-shadow: 0 16px 30px rgba(37, 99, 235, 0.36);
            transform: translateY(-1px);
        }

        [data-testid="stChatMessage"] {
            background: rgba(30, 41, 59, 0.78);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 12px;
            box-shadow: 0 10px 24px rgba(2, 6, 23, 0.20);
        }

        .stTextInput input, textarea {
            background: #0F172A;
            color: #E5E7EB;
            border: 1px solid rgba(34, 211, 238, 0.35);
            border-radius: 8px;
        }

        [data-testid="stMetricValue"] {
            color: #67E8F9;
        }

        div[data-baseweb="select"] > div {
            background: #111827;
            border-color: rgba(34, 211, 238, 0.28);
            color: #E5E7EB;
        }

        [data-testid="stExpander"] {
            background: rgba(15, 23, 42, 0.74);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def add_bot_message(text, typing=True):
    """Add bot response to session state and optionally animate it."""
    if typing:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            typed = ""
            for character in text:
                typed += character
                placeholder.markdown(typed + "▌")
                time.sleep(0.006)
            placeholder.markdown(text)

    st.session_state.messages.append({"role": "assistant", "content": text})


def add_user_message(text):
    """Add user message to session state."""
    st.session_state.messages.append({"role": "user", "content": text})


def render_metric(label, value):
    """Render a small dashboard metric card."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_series_chart(title, series):
    """Display a compact bar chart from a pandas Series."""
    st.subheader(title)

    if series.empty:
        st.info("No data available.")
        return

    chart_df = pd.DataFrame(
        {
            "name": series.index.astype(str),
            "count": series.values,
        }
    ).set_index("name")
    st.bar_chart(chart_df, color="#22D3EE")


def main():
    apply_professional_theme()
    logs_df, user_data, analytics = load_project_data()
    user_ids = get_user_ids(user_data)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "System online. Ask for recommendations, history, or wishlist data."
                ),
            }
        ]

    st.sidebar.title("User Analytics")
    selected_user = st.sidebar.selectbox("Select user", user_ids)
    current_user = user_data[selected_user]

    st.sidebar.markdown("---")
    st.sidebar.write(f"Active user: `{selected_user}`")
    st.sidebar.write(f"Searches: `{len(current_user['search_history'])}`")
    st.sidebar.write(f"Views: `{len(current_user['view_history'])}`")
    st.sidebar.write(f"Watched items: `{len(current_user['watch_history'])}`")
    st.sidebar.write(f"Wishlist items: `{len(current_user['wishlist'])}`")
    st.sidebar.write(f"Total time: `{current_user['total_time_seconds']} sec`")

    st.title("Log Analyzer for Web Servers")
    st.caption("Product Recommendation Chatbot")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        render_metric("Total Log Events", len(logs_df))
    with metric_col2:
        render_metric("Users Detected", len(user_ids))
    with metric_col3:
        render_metric("Top Category", analytics["searched_categories"].index[0])
    with metric_col4:
        render_metric("Top Product", analytics["viewed_products"].index[0])

    left_col, right_col = st.columns([1.15, 0.85], gap="large")

    with left_col:
        st.markdown('<div class="terminal-panel">', unsafe_allow_html=True)
        st.subheader("Chat Console")

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        button_col1, button_col2, button_col3 = st.columns(3)

        with button_col1:
            if st.button("Show History"):
                add_user_message("Show my history")
                response = get_history_response(selected_user, user_data)
                add_bot_message(response)
                st.rerun()

        with button_col2:
            if st.button("Show Wishlist"):
                add_user_message("Show my wishlist")
                response = get_wishlist_response(selected_user, user_data)
                add_bot_message(response)
                st.rerun()

        with button_col3:
            if st.button("Get Recommendations"):
                add_user_message("Recommend me something")
                response = get_recommendation_response(selected_user, user_data, logs_df)
                add_bot_message(response)
                st.rerun()

        prompt = st.chat_input("Type a message...")
        if prompt:
            add_user_message(prompt)
            with st.chat_message("user"):
                st.markdown(prompt)

            response = respond_to_message(prompt, selected_user, user_data, logs_df)
            add_bot_message(response)
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="terminal-panel">', unsafe_allow_html=True)
        st.subheader("Live Log Intelligence")
        render_series_chart("Most Searched Categories", analytics["searched_categories"])
        render_series_chart("Most Viewed Products", analytics["viewed_products"])
        render_series_chart("Frequently Watched Items", analytics["watched_items"])
        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Processed Data Preview"):
        st.dataframe(logs_df, use_container_width=True)


if __name__ == "__main__":
    main()
