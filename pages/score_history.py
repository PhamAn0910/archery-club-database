"""Score History Page"""
import streamlit as st
import pandas as pd
from guards import require_archer
from streamlit.components.v1 import html

@require_archer
def show_score_history():
# ==========================================================
#  PAGE 2: SCORE HISTORY
# ==========================================================
    st.title("Archery Club Dashboard App")
    st.subheader("My Score History")
    st.caption("View all your recorded scores")

    # ---------------------------
    # Sample Data
    # ---------------------------
    data = [
        {"Date": "1 Nov 2025", "Round Name": "WA 900", "Total Score": 814, "X Count": 12, "Status": "Confirmed"},
        {"Date": "15 Oct 2025", "Round Name": "Brisbane", "Total Score": 1072, "X Count": 12, "Status": "Confirmed"},
        {"Date": "22 Sept 2025", "Round Name": "WA 900", "Total Score": 802, "X Count": 11, "Status": "Preliminary"},
    ]
    df = pd.DataFrame(data)

    # Round Filter
    selected_round = st.selectbox("Filter by Round", ["All Rounds"] + sorted(df["Round Name"].unique().tolist()))
    if selected_round != "All Rounds":
        df = df[df["Round Name"] == selected_round]

    # Display table
    st.markdown("---")
    st.markdown("#### My Recorded Scores")

    for i, row in df.iterrows():
        cols = st.columns([2, 2, 2, 1.5, 1.5, 2])
        cols[0].write(row["Date"])
        cols[1].write(row["Round Name"])
        cols[2].write(row["Total Score"])
        cols[3].write(row["X Count"])
        cols[4].write(row["Status"])
        with cols[5]:
            if st.button("View Details", key=f"view_{i}"):
                st.session_state["popup_data"] = row


    # ---------------------------
    # Popup modal (with working close button)
    # ---------------------------
    if "popup_data" in st.session_state:
        r = st.session_state["popup_data"]

        modal_html = f"""
        <style>
        .modal-bg {{
            position: fixed; top:0; left:0; width:100%; height:100%;
            background-color: rgba(0,0,0,0.6);
            display:flex; justify-content:center; align-items:center;
            z-index: 9999;
        }}
        .modal-box {{
            background-color: white;
            padding: 25px 35px;
            border-radius: 12px;
            max-width: 700px;
            width: 90%;
            box-shadow: 0 0 30px rgba(0,0,0,0.3);
            font-family: sans-serif;
        }}
        .modal-box h3 {{ margin-top:0; }}
        .arrow-grid {{
            display:grid; grid-template-columns: 60px repeat(6, 1fr) 60px;
            gap:6px; align-items:center;
        }}
        .arrow-cell {{
            text-align:center; border:1px solid #ddd; border-radius:6px; padding:4px;
            background-color:#f8f8f8;
        }}
        </style>

        <div class="modal-bg">
          <div class="modal-box">
            <h3>{r["Round Name"]} – {r["Date"]}</h3>
            <p><b>Total Score:</b> {r["Total Score"]}  <b>X Count:</b> {r["X Count"]}  <b>Status:</b> {r["Status"]}</p>
            <hr style="margin:10px 0;">
            <h4>60 m (122 cm face)</h4>
            <p style="margin-top:-8px;">Range Total: 260 X’s: 2</p>
        """

        ends = [
            {"End": 1, "Arrows": ["X","10","9","9","8","7"], "Total": 53},
            {"End": 2, "Arrows": ["10","9","9","8","8","7"], "Total": 51},
            {"End": 3, "Arrows": ["X","10","10","9","8","8"], "Total": 55},
            {"End": 4, "Arrows": ["9","9","9","8","7","7"], "Total": 49},
            {"End": 5, "Arrows": ["10","9","9","8","8","8"], "Total": 52},
        ]

        for e in ends:
            row_html = f"<div class='arrow-grid'><div><b>End {e['End']}</b></div>"
            for a in e["Arrows"]:
                row_html += f"<div class='arrow-cell'>{a}</div>"
            row_html += f"<div><b>{e['Total']}</b></div></div>"
            modal_html += row_html

        modal_html += """
          </div>
        </div>
        """

        html(modal_html, height=800)

        # Add a real Streamlit close button below
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Close", type="primary"):
            del st.session_state["popup_data"]
            st.rerun()

