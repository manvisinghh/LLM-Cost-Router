import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.router.classifier import route_question

st.set_page_config(page_title="LLM Cost Router", layout="wide")

# --- Custom CSS: cream/charcoal/terracotta theme ---
st.markdown("""
    <style>
    .stApp {
        background-color: #F5F1EA;
    }
    h1, h2, h3 {
        color: #1A1A1A !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    p, .stMarkdown, label {
        color: #1A1A1A;
    }
    .stButton > button {
    background-color: #E8697D;
    color: #FFFFFF;
    border-radius: 4px;
    border: none;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #C4506B;
    color: white;
}
    div[data-testid="stMetric"] {
        background-color: #EDE7DB;
        padding: 1rem;
        border-radius: 8px;
    }
    div[data-testid="stMetricValue"] {
        color: #C4694A;
    }
    .hero-banner {
        background: linear-gradient(135deg, #EDE7DB 0%, #F5F1EA 100%);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 2rem;
    }
    .hero-text h1 {
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    .hero-text p {
        color: #8B8378;
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Hero section with CSS-generated iridescent orb ---
st.markdown("""
    <div class="hero-banner">
        <div class="hero-text">
            <h1>LLM Cost Router</h1>
            <p>Routes queries between a cheap and expensive LLM based on estimated difficulty — cutting inference costs without sacrificing quality where it matters.</p>
        </div>
        <div>
            <svg width="180" height="180" viewBox="0 0 180 180">
                <defs>
                    <radialGradient id="orb1" cx="35%" cy="30%" r="70%">
                        <stop offset="0%" stop-color="#FFD9C7"/>
                        <stop offset="35%" stop-color="#E8896B"/>
                        <stop offset="70%" stop-color="#8B4A6B"/>
                        <stop offset="100%" stop-color="#2D2A4A"/>
                    </radialGradient>
                    <radialGradient id="orb2" cx="40%" cy="35%" r="65%">
                        <stop offset="0%" stop-color="#F5F1EA"/>
                        <stop offset="40%" stop-color="#C4694A"/>
                        <stop offset="80%" stop-color="#6B4A8B"/>
                        <stop offset="100%" stop-color="#1A1A1A"/>
                    </radialGradient>
                </defs>
                <circle cx="115" cy="95" r="60" fill="url(#orb1)" opacity="0.95"/>
                <circle cx="45" cy="55" r="28" fill="url(#orb2)" opacity="0.9"/>
                <circle cx="115" cy="95" r="60" fill="none" stroke="#F5F1EA" stroke-width="1" opacity="0.3"/>
            </svg>
        </div>
    </div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Try it live", "Evaluation results"])

with tab1:
    st.subheader("Ask a question")
    question = st.text_input("Your question:")
    if st.button("Ask") and question.strip():
        with st.spinner("Routing and answering..."):
            result = route_question(question)

        col1, col2, col3 = st.columns(3)
        col1.metric("Routed to", result["routed_to"])
        col2.metric("Difficulty score", result["difficulty_score"])
        col3.metric("Total cost", f"${result.get('total_cost_usd', result.get('cost_usd', 0)):.6f}")

        st.write("**Answer:**")
        st.write(result["answer"])

        if result["fallback_triggered"]:
            st.warning("Fallback triggered — cheap model's answer looked unreliable, escalated to expensive model.")

with tab2:
    st.subheader("Evaluation results (56-question benchmark)")

    try:
        summary = pd.read_csv("evaluation/results/summary.csv")
        st.dataframe(summary, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(summary.set_index("strategy")["total_cost_usd"], color="#C4694A")
            st.caption("Total cost by strategy")
        with col2:
            st.bar_chart(summary.set_index("strategy")["avg_quality_score"], color="#8B4A6B")
            st.caption("Average quality score by strategy")

        st.info(
            "On a balanced 50/50 easy/hard test set, routing overhead offset savings. "
            "Simulating realistic 80/20 easy-weighted traffic showed a 4.1% cost reduction "
            "vs. always using the expensive model, with a modest quality tradeoff."
        )
    except FileNotFoundError:
        st.error("No evaluation results found. Run evaluation/build_report.py first.")