"""Personal Bests & Records Page"""
import streamlit as st
from guards import require_archer

@require_archer
def show_pbs_records():
# ==========================================================
#  PAGE 3: PERSONAL BESTS & CLUB RECORDS (with Division filter)
# ==========================================================
    st.title("Personal Bests & Club Records")
    st.caption("Track your achievements and club records")

    # --- Shared Division Filter ---
    division = st.selectbox("Filter by Division", ["All Divisions", "Recurve", "Compound"])
    st.markdown("---")

    # --- Toggle Tabs ---
    tabs = st.tabs(["My Personal Bests", "Club Records"])

    # ---------------------------
    # Tab 1: My Personal Bests
    # ---------------------------
    with tabs[0]:
        personal_bests = [
            {"Round": "Brisbane", "Division": "Recurve", "Score": 1072, "Date": "15 Oct 2025"},
            {"Round": "WA 900", "Division": "Recurve", "Score": 814, "Date": "1 Nov 2025"},
            {"Round": "Short Metric", "Division": "Compound", "Score": 720, "Date": "10 Sept 2025"},
        ]

        # Filter
        if division != "All Divisions":
            personal_bests = [p for p in personal_bests if p["Division"] == division]

        st.markdown("### My Personal Bests")
        cols = st.columns(len(personal_bests))
        for i, p in enumerate(personal_bests):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style='background-color:white;border:1px solid #eee;
                    border-radius:10px;padding:20px 25px;text-align:center;
                    box-shadow:0 2px 6px rgba(0,0,0,0.05);'>
                        <div style='font-size:30px;'>🏆</div>
                        <h4 style='margin-bottom:2px;'>{p["Round"]}</h4>
                        <p style='margin-top:0;color:#666;'>{p["Division"]}</p>
                        <h2 style='margin:8px 0;color:#222;'>{p["Score"]}</h2>
                        <p style='color:#999;font-size:14px;'>{p["Date"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ---------------------------
    # Tab 2: Club Records
    # ---------------------------
    with tabs[1]:
        club_records = [
            {"Round": "Brisbane", "Division": "Recurve", "Score": 1072, "Archer": "Sarah Johnson", "Date": "15 Oct 2025"},
            {"Round": "Short Metric", "Division": "Recurve", "Score": 666, "Archer": "Emma Wilson", "Date": "28 Oct 2025"},
            {"Round": "WA 900", "Division": "Compound", "Score": 896, "Archer": "Michael Chen", "Date": "1 Nov 2025"},
            {"Round": "WA 900", "Division": "Recurve", "Score": 814, "Archer": "Sarah Johnson", "Date": "1 Nov 2025"},
        ]

        # Filter
        if division != "All Divisions":
            club_records = [r for r in club_records if r["Division"] == division]

        st.markdown("### Club Records")
        cols = st.columns(3)
        for i, r in enumerate(club_records):
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div style='background-color:white;border:1px solid #eee;
                    border-radius:10px;padding:20px 25px;text-align:center;
                    box-shadow:0 2px 6px rgba(0,0,0,0.05);'>
                        <div style='font-size:30px;color:#d4af37;'>🏆</div>
                        <h4 style='margin-bottom:2px;'>{r["Round"]}</h4>
                        <p style='margin-top:0;color:#666;'>{r["Division"]}</p>
                        <h2 style='margin:8px 0;color:#222;'>{r["Score"]}</h2>
                        <p style='margin:0;color:#999;font-size:14px;'>{r["Archer"]}</p>
                        <p style='margin-top:0;color:#bbb;font-size:13px;'>{r["Date"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
