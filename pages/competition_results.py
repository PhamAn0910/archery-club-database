"""Competition Results Page"""
import streamlit as st
import pandas as pd

def show_competition_results():
# ==========================================================
#  PAGE 4: COMPETITIONS (with "Choose a competition..." placeholder)
# ==========================================================
    st.title("Competition Results")
    st.caption("View official competition results")

    # --- Competition data ---
    competition_results = {
        "Spring Championship 2025": {
            "Recurve Open Female": [
                {"Rank": "🥇 1st", "Archer": "Sarah Johnson", "Round": "Brisbane", "Score": 1072, "X Count": 12},
            ],
        },
        "Summer Open 2025": {
            "Recurve Open Female": [
                {"Rank": "🥇 1st", "Archer": "Sarah Johnson", "Round": "WA 900", "Score": 814, "X Count": 12},
            ],
            "Compound Open Male": [
                {"Rank": "🥇 1st", "Archer": "Michael Chen", "Round": "WA 900", "Score": 896, "X Count": 45},
            ],
        },
    }

    # --- Dropdown with placeholder ---
    competitions = ["Choose a competition..."] + list(competition_results.keys())
    selected_comp = st.selectbox("Select Competition", competitions, index=0)

    # --- Only show results after user selection ---
    if selected_comp != "Choose a competition...":
        st.markdown("---")
        selected_data = competition_results[selected_comp]

        for division, results in selected_data.items():
            st.markdown(f"### {division}")
            df = pd.DataFrame(results)
            st.dataframe(
                df.style.set_table_styles([
                    {"selector": "thead th", "props": [("background-color", "#f5f5f5"), ("font-weight", "bold")]},
                    {"selector": "tbody td", "props": [("padding", "8px")]},
                ]),
                use_container_width=True
            )