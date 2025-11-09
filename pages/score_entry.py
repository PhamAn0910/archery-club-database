"""Live Score Entry Page – Archery Club Dashboard"""
import streamlit as st
from datetime import date
from guards import require_archer
from data_rounds import create_session, save_end, list_rounds
from db_core import fetch_one, fetch_all


@require_archer
def show_score_entry():
    # ==========================================================
    # INITIALIZE STATE
    # ==========================================================
    defaults = {
        "selected_round": None,
        "round_id": None,
        "round_ranges": [],
        "current_range": 1,
        "current_end": 1,
        "session_id": None,
        "scores": [],
        "running_total": 0,
        "range_done": False
    }
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)

    # ==========================================================
    # AUTH / USER CONTEXT
    # ==========================================================
    auth = st.session_state.get("auth")
    if not auth or not auth.get("logged_in"):
        st.error("You must be logged in as an archer to enter scores.")
        st.stop()

    member_id = auth["id"]
    member_name = auth["name"]

    # ==========================================================
    # PAGE HEADER
    # ==========================================================
    st.title("Archery Club Dashboard App")
    st.subheader(member_name)
    st.caption("Live Score Entry")

    # ==========================================================
    # ROUND SELECTION
    # ==========================================================
    rounds = list_rounds()
    round_names = [""] + [r["round_name"] for r in rounds]
    selected_round = st.selectbox("Choose a round...", round_names, key="round_select")

    if not selected_round:
        st.info("Please select a round to begin.")
        st.stop()

    # ----------------------------------------------------------
    # Load selected round’s ranges (only when new round chosen)
    # ----------------------------------------------------------
    if selected_round != st.session_state.selected_round:
        st.session_state.selected_round = selected_round
        st.session_state.scores = []
        st.session_state.running_total = 0
        st.session_state.current_range = 1
        st.session_state.current_end = 1
        st.session_state.session_id = None
        st.session_state.range_done = False

        row = fetch_one(
            "SELECT id FROM round WHERE round_name = :rname", {"rname": selected_round}
        )
        if not row:
            st.error(f"Round '{selected_round}' not found in database.")
            st.stop()
        st.session_state.round_id = row["id"]

        st.session_state.round_ranges = fetch_all(
            """
            SELECT 
                id,
                ROW_NUMBER() OVER (ORDER BY distance_m DESC) AS seq_no,
                distance_m,
                face_size,
                ends_per_range
            FROM round_range
            WHERE round_id = :rid
            ORDER BY distance_m DESC
            """,
            {"rid": st.session_state.round_id},
        )

    # ==========================================================
    # RANGE + END CONTEXT
    # ==========================================================
    ranges = st.session_state.round_ranges
    total_ranges = len(ranges)
    current_range_idx = st.session_state.current_range - 1
    current_range = ranges[current_range_idx]
    distance = current_range["distance_m"]
    face = current_range["face_size"]
    ends_per_range = current_range["ends_per_range"]

    st.markdown(f"### Range {st.session_state.current_range} of {total_ranges}")
    st.info(f"Distance: {distance} m • Face: {face} cm")

    # ==========================================================
    # INPUT ARROWS FOR THIS END
    # ==========================================================
    st.markdown(f"#### End {st.session_state.current_end} of {ends_per_range}")

    score_options = ["M", "1","2","3","4","5","6","7","8","9","10","X"]
    arrow_labels = [f"Arrow {i}" for i in range(1,7)]
    arrow_values = [
        st.selectbox(label, score_options, key=f"{st.session_state.current_range}_{st.session_state.current_end}_{i}")
        for i, label in enumerate(arrow_labels, start=1)
    ]

    def convert(v): return 10 if v == "X" else 0 if v == "M" else int(v)
    end_total = sum(convert(a) for a in arrow_values)

    st.markdown("---")
    st.metric("End Total", end_total)
    st.metric("Running Total", st.session_state.running_total)

    # ==========================================================
    # ACTION BUTTONS
    # ==========================================================
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Next End"):
            # 1. Create session if needed
            if not st.session_state.session_id:
                st.session_state.session_id = create_session(
                    member_id=member_id,
                    round_id=st.session_state.round_id,
                    shoot_date=str(date.today()),
                )

            # 2. Save current end + arrows
            save_end(
                session_id=st.session_state.session_id,
                round_range_id=current_range["id"],
                end_no=st.session_state.current_end,
                arrow_values=arrow_values,
            )

            # 3. Update local totals
            st.session_state.scores.append(end_total)
            st.session_state.running_total += end_total

            # 4. Move to next end or flag range done
            if st.session_state.current_end < ends_per_range:
                st.session_state.current_end += 1
            else:
                st.session_state.range_done = True

            st.rerun()

    with col2:
        if st.button("Reset"):
            for key in ["current_end","current_range","scores","running_total","session_id","range_done"]:
                if key in ["scores"]:
                    st.session_state[key] = []
                elif key in ["current_end","current_range"]:
                    st.session_state[key] = 1
                elif key == "running_total":
                    st.session_state[key] = 0
                else:
                    st.session_state[key] = None
            st.success("Round reset.")
            st.rerun()

    # ==========================================================
    # HANDLE RANGE COMPLETION
    # ==========================================================
    if st.session_state.range_done:
        if total_ranges == 1:
            # Single-distance round – now just save and mark for approval
            st.success("✅ Round complete! Scores saved for approval.")
            st.session_state.session_id = None
            st.stop()
        else:
            # Multi-distance round – manual confirmation for next range
            st.success(f"✅ Range {st.session_state.current_range} ({distance} m) completed.")
            if st.session_state.current_range < total_ranges:
                if st.button("Next Range ➡️"):
                    st.session_state.current_range += 1
                    st.session_state.current_end = 1
                    st.session_state.range_done = False
                    st.rerun()
            else:
                st.success("🎯 All ranges complete! Scores saved for approval.")
                st.session_state.session_id = None
                st.stop()

    # ==========================================================
    # SUMMARY DISPLAY
    # ==========================================================
    if st.session_state.scores:
        st.markdown("### Summary of Ends")
        for i, s in enumerate(st.session_state.scores, start=1):
            st.write(f"End {i}: {s} points")
