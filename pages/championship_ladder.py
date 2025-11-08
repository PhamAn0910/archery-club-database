"""Championship Ladder Page"""
import streamlit as st
import pandas as pd

def show_championship_ladder():
# ==========================================================
#  PAGE 5: CHAMPIONSHIP
# ==========================================================
    st.title("Club Championship 2025")
    st.caption("Ranking based on best 3 scores")

    # --- Info box ---
    st.info("🏅 Championship scoring: Sum of best 3 across eligible rounds")

    # --- Championship data ---
    championship_results = {
        "Recurve Open": [
            {
                "Rank": "🥇 1st",
                "Archer": "Sarah Johnson",
                "Championship Score": 1886,
                "Counted Scores": "1072, 814"
            },
        ],
        "Compound Open": [
            {
                "Rank": "🥇 1st",
                "Archer": "Michael Chen",
                "Championship Score": 896,
                "Counted Scores": "896"
            },
        ],
    }

    # --- Display each division ---
    for division, results in championship_results.items():
        st.markdown(f"### {division}")
        df = pd.DataFrame(results)
        st.dataframe(
            df.style.set_table_styles([
                {"selector": "thead th", "props": [("background-color", "#f5f5f5"), ("font-weight", "bold")]},
                {"selector": "tbody td", "props": [("padding", "8px")]},
            ]),
            use_container_width=True
        )
