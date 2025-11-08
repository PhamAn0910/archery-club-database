"""Round Definitions Page"""
import streamlit as st
from data_rounds import list_rounds, list_ranges

def show_round_definitions():
# ==========================================================
#  PAGE 6: ROUND DEFINITIONS (dropdown version – fully native)
# ==========================================================
    st.title("Round Definitions")
    st.caption("Reference guide for all archery rounds")

    # --- Data for rounds ---
    rounds_data = {
        "WA 900": [
            {"Range": 1, "Distance": 60, "Face": 122, "Ends": 5},
            {"Range": 2, "Distance": 50, "Face": 122, "Ends": 5},
            {"Range": 3, "Distance": 40, "Face": 80,  "Ends": 5},
        ],
        "Melbourne": [
            {"Range": 1, "Distance": 90, "Face": 122, "Ends": 6},
            {"Range": 2, "Distance": 70, "Face": 122, "Ends": 6},
        ],
        "Brisbane": [
            {"Range": 1, "Distance": 70, "Face": 122, "Ends": 5},
            {"Range": 2, "Distance": 60, "Face": 122, "Ends": 5},
            {"Range": 3, "Distance": 50, "Face": 80,  "Ends": 5},
            {"Range": 4, "Distance": 40, "Face": 80,  "Ends": 5},
        ],
        "Canberra": [
            {"Range": 1, "Distance": 90, "Face": 122, "Ends": 6},
            {"Range": 2, "Distance": 70, "Face": 122, "Ends": 6},
            {"Range": 3, "Distance": 50, "Face": 80,  "Ends": 6},
        ],
        "Short Metric": [
            {"Range": 1, "Distance": 50, "Face": 80, "Ends": 6},
            {"Range": 2, "Distance": 30, "Face": 80, "Ends": 6},
        ],
    }

    # --- Dropdown selection ---
    selected_round = st.selectbox("Select a round", ["Choose a round..."] + list(rounds_data.keys()))

    # --- Display round details if selected ---
    if selected_round != "Choose a round...":
        ranges = rounds_data[selected_round]
        total_ends = sum(r["Ends"] for r in ranges)

        st.markdown(f"### {selected_round}")
        st.caption(f"Total of {total_ends} ends")

        for r in ranges:
            arrows = r["Ends"] * 6
            st.markdown(
                f"""
                <div style='border:1px solid #eee;border-radius:10px;padding:15px 25px;
                margin:10px 0;background-color:white;box-shadow:0 1px 4px rgba(0,0,0,0.04);'>
                    <div style='font-size:18px;font-weight:600;'>Range {r["Range"]}</div>
                    <p style='margin:4px 0;'>Distance: <b>{r["Distance"]}m</b></p>
                    <p style='margin:4px 0;'>Face Size: <b>{r["Face"]}cm</b></p>
                    <p style='margin:4px 0;'>Ends: {r["Ends"]} ends × 6 arrows = {arrows} arrows</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        total_arrows = sum(r["Ends"] * 6 for r in ranges)
        st.markdown(
            f"""
            <div style='border:1px solid #eee;border-radius:10px;padding:15px 20px;
            margin-top:15px;background-color:#f9f9f9;color:#555;'>
                📘 <b>Total Arrows</b><br>
                {total_arrows} arrows across {len(ranges)} ranges
            </div>
            """,
            unsafe_allow_html=True
        )

