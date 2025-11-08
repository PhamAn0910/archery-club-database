import streamlit as st
import pandas as pd
from streamlit.components.v1 import html

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(page_title="Archery Club Dashboard App", layout="wide")

# ---------------------------
# Sidebar Navigation (role-based)
# ---------------------------
st.sidebar.title("🏹 Archery Club")

# User chooses current role
role = st.sidebar.radio("Current Role", ["Archer", "Recorder"], key="role_selector")

# Role-specific navigation
if role == "Archer":
    page = st.sidebar.radio(
        "Navigation",
        [
            "🎯 Live Score Entry",
            "⏱️ Score History",
            "🏆 Personal Bests",
            "🥇 Competitions",      
            "📈 Championship",
            "📖 Round Definitions"
        ],
        key="archer_pages"
    )

elif role == "Recorder":
    page = st.sidebar.radio(
        "Navigation",
        [
            "✅ Score Approval",
            "⚙️ Admin Management"
        ],
        key="recorder_pages"
    )
# Divider for neat grouping
st.sidebar.markdown("---")
st.sidebar.caption("Use this menu to navigate through the app.")
# ---------------------------
# Initialize Session Variables
# ---------------------------
if "current_end" not in st.session_state:
    st.session_state.current_end = 1
if "running_total" not in st.session_state:
    st.session_state.running_total = 0
if "scores" not in st.session_state:
    st.session_state.scores = []  # stores list of end totals

# ==========================================================
#  PAGE 1: LIVE SCORE ENTRY
# ==========================================================
if page == "🎯 Live Score Entry":
    st.title("Archery Club Dashboard App")
    st.subheader("Sarah Johnson")
    st.caption("Live Score Entry")

    # Round Selection
    st.markdown("### Select Round")
    selected_round = st.selectbox(
        "Choose a round...",
        ["", "WA 900", "Melbourne", "Brisbane", "Canberra", "Short Metric"]
    )

    if selected_round:
        st.info("Now Shooting: 6 ends at 90m, 122cm face")
        st.markdown(f"### End {st.session_state.current_end} of 6")

        # Dropdowns for arrow scores
        arrow_labels = [f"Arrow {i}" for i in range(1, 7)]
        score_options = ["M", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "X"]

        arrow_values = []
        cols = st.columns(3)
        for i, label in enumerate(arrow_labels[:3]):
            arrow_values.append(
                cols[i].selectbox(
                    label,
                    score_options,
                    index=score_options.index("M"),
                    key=f"arrow_{st.session_state.current_end}_{i+1}"
                )
            )

        cols2 = st.columns(3)
        for i, label in enumerate(arrow_labels[3:]):
            arrow_values.append(
                cols2[i].selectbox(
                    label,
                    score_options,
                    index=score_options.index("M"),
                    key=f"arrow_{st.session_state.current_end}_{i+4}"
                )
            )

        # Convert scores
        def convert(score):
            if score == "X":
                return 10
            if score == "M":
                return 0
            return int(score)

        numeric_scores = [convert(a) for a in arrow_values]
        end_total = sum(numeric_scores)

        # Display Totals
        st.markdown("---")
        col1, col2 = st.columns(2)
        col1.metric("End Total", end_total)
        col2.metric("Running Total", st.session_state.running_total)

        # Buttons
        col_next, col_reset = st.columns([1, 1])
        with col_next:
            if st.button("Next End ➡️"):
                st.session_state.scores.append(end_total)
                st.session_state.running_total += end_total
                st.session_state.current_end += 1
                if st.session_state.current_end > 6:
                    st.session_state.current_end = 6
                    st.success("🎯 Round Completed! All 6 ends recorded.")
        with col_reset:
            if st.button("🔁 Reset Round"):
                st.session_state.current_end = 1
                st.session_state.running_total = 0
                st.session_state.scores = []
                st.experimental_rerun()

        # Display previous end totals
        if st.session_state.scores:
            st.markdown("### 🧾 Summary of Ends")
            for i, score in enumerate(st.session_state.scores, start=1):
                st.write(f"End {i}: {score} points")

# ==========================================================
#  PAGE 2: SCORE HISTORY
# ==========================================================
elif page == "⏱️ Score History":
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



# ==========================================================
#  PAGE 3: PERSONAL BESTS & CLUB RECORDS (with Division filter)
# ==========================================================
elif page == "🏆 Personal Bests":
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

# ==========================================================
#  PAGE 4: COMPETITIONS (with "Choose a competition..." placeholder)
# ==========================================================
elif page == "🥇 Competitions":
    import pandas as pd
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

# ==========================================================
#  PAGE 5: CHAMPIONSHIP
# ==========================================================
elif page == "📈 Championship":
    import pandas as pd
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

# ==========================================================
#  PAGE 6: ROUND DEFINITIONS (dropdown version – fully native)
# ==========================================================
elif page == "📖 Round Definitions":
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


# ==========================================================
#  RECORDER PAGE 1: SCORE APPROVAL (Interactive Mock Version)
# ==========================================================
elif page == "✅ Score Approval":
    import pandas as pd

    st.title("Score Approval")
    st.caption("Review and approve preliminary scores")

    # --- Initialize mock data once ---
    if "pending_scores" not in st.session_state:
        st.session_state.pending_scores = [
            {
                "Date": "22 Sept 2025",
                "Archer": "Sarah Johnson",
                "Round": "WA 900",
                "Division": "Recurve",
                "Total Score": 802,
                "X Count": 11,
            },
            {
                "Date": "1 Oct 2025",
                "Archer": "Michael Chen",
                "Round": "Melbourne",
                "Division": "Compound",
                "Total Score": 896,
                "X Count": 45,
            },
        ]

    # --- Display data if available ---
    if len(st.session_state.pending_scores) == 0:
        st.info("✅ All scores have been reviewed. No pending approvals.")
    else:
        df = pd.DataFrame(st.session_state.pending_scores)
        st.dataframe(df, use_container_width=True)
        st.markdown("---")

        # --- Actions section ---
        st.markdown("### Actions")

        for i, record in enumerate(st.session_state.pending_scores):
            with st.expander(f"📋 {record['Archer']} — {record['Round']} ({record['Date']})"):
                st.write(f"**Division:** {record['Division']}")
                st.write(f"**Total Score:** {record['Total Score']}")
                st.write(f"**X Count:** {record['X Count']}")

                col1, col2, col3 = st.columns([1, 1, 5])
                with col1:
                    if st.button("✏️ Edit", key=f"edit_{i}"):
                        st.warning("Editing feature coming soon!")
                with col2:
                    if st.button("✅ Confirm", key=f"confirm_{i}"):
                        st.session_state.pending_scores.pop(i)
                        st.success(f"Confirmed score for {record['Archer']} ({record['Round']}).")
                        st.rerun()
                with col3:
                    if st.button("❌ Reject", key=f"reject_{i}"):
                        st.session_state.pending_scores.pop(i)
                        st.error(f"Rejected score for {record['Archer']} ({record['Round']}).")
                        st.rerun()

# ==========================================================
#  RECORDER PAGE 2: ADMIN MANAGEMENT
# ==========================================================
elif page == "⚙️ Admin Management":
    st.title("Admin Management")
    st.caption("Manage club data and system configuration")

    st.markdown("### 👥 User Management")
    st.info("Add, edit, or deactivate club users.")
    st.write("🧑‍💻 Coming soon: Create or edit user accounts")

    st.markdown("### 🎯 Round Management")
    st.info("Add or update official round definitions.")
    st.write("⚙️ Coming soon: Import or modify round data")

    st.markdown("### 🏆 Competition Setup")
    st.info("Define club competitions and link them to rounds.")
    st.write("📅 Coming soon: Schedule competitions for the season")

