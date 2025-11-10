"""Live Score Entry Page – Archery Club Dashboard"""
import streamlit as st
from datetime import date
from guards import require_archer
from data_rounds import create_session, save_end, list_rounds
from db_core import fetch_one, fetch_all, exec_sql


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
        "range_done": False,
        "editing_end": None,
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
    # Load round ID + check for existing Preliminary sessions
    # ----------------------------------------------------------
    round_row = fetch_one(
        "SELECT id FROM round WHERE round_name = :rname", {"rname": selected_round}
    )
    if not round_row:
        st.error(f"Round '{selected_round}' not found in database.")
        st.stop()

    st.session_state.round_id = round_row["id"]

    prelim_sessions = fetch_all(
        """
        SELECT s.id, s.shoot_date,
               COUNT(e.id) AS ends_recorded,
               COALESCE(rr_total.ends_per_round, 0) AS total_ends
        FROM session s
        LEFT JOIN `end` e ON e.session_id = s.id
        LEFT JOIN (
            SELECT round_id, SUM(ends_per_range) AS ends_per_round
            FROM round_range GROUP BY round_id
        ) rr_total ON rr_total.round_id = s.round_id
        WHERE s.member_id = :mid
          AND s.round_id = :rid
          AND s.status = 'Preliminary'
        GROUP BY s.id
        ORDER BY s.shoot_date DESC;
        """,
        {"mid": member_id, "rid": st.session_state.round_id},
    )

    # ----------------------------------------------------------
    # Ask user if existing session(s) found
    # ----------------------------------------------------------
    if prelim_sessions and not st.session_state.session_id:
        latest = prelim_sessions[0]
        ends_done = latest["ends_recorded"]
        ends_total = latest["total_ends"]

        if ends_done < ends_total:
            st.warning(
                f"You have an unfinished Preliminary session for {selected_round} "
                f"({ends_done}/{ends_total} ends recorded, started {latest['shoot_date']})."
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➡️ Continue Session"):
                    st.session_state.session_id = latest["id"]
                    st.rerun()
            with col2:
                if st.button("🆕 Start New Session"):
                    st.session_state.session_id = None
                    create_new_session(member_id, st.session_state.round_id) 
                    st.rerun()
            st.stop()

        else:
            st.info(
                f"You have a completed Preliminary session for {selected_round} "
                f"(all {ends_total} ends recorded)."
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Edit This Session"):
                    st.session_state.session_id = latest["id"]
                    st.rerun()
            with col2:
                if st.button("🆕 Start New Session"):
                    st.session_state.session_id = None
                    create_new_session(member_id, st.session_state.round_id)
                    st.rerun()
            st.stop()

    # ==========================================================
    # SESSION CREATION (when new)
    # ==========================================================
    if not st.session_state.session_id:
        st.session_state.session_id = create_session(
            member_id=member_id,
            round_id=st.session_state.round_id,
            shoot_date=str(date.today()),
        )

    # ==========================================================
    # FETCH CURRENT SESSION STATUS
    # ==========================================================
    session_info = fetch_one(
        "SELECT status FROM session WHERE id = :sid", {"sid": st.session_state.session_id}
    )
    session_status = session_info["status"]

    if session_status in ["Final", "Confirmed"]:
        st.info(f"This session is **{session_status}** and cannot be edited.")
        st.stop()

    # ==========================================================
    # LOAD ROUND RANGES
    # ==========================================================
    if not st.session_state.round_ranges:
        st.session_state.round_ranges = fetch_all(
            """
            SELECT id, distance_m, face_size, ends_per_range
            FROM round_range
            WHERE round_id = :rid
            ORDER BY distance_m DESC
            """,
            {"rid": st.session_state.round_id},
        )

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

    score_options = ["M", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "X"]
    arrow_labels = [f"Arrow {i}" for i in range(1, 7)]
    arrow_values = [
        st.selectbox(label, score_options, key=f"{st.session_state.current_range}_{st.session_state.current_end}_{i}")
        for i, label in enumerate(arrow_labels, start=1)
    ]

    def convert(v): return 10 if v == "X" else 0 if v == "M" else int(v)
    end_total = sum(convert(a) for a in arrow_values)

    st.metric("End Total", end_total)
    st.metric("Running Total", st.session_state.running_total)

    # ==========================================================
    # ACTION BUTTONS (NEXT END / RESET)
    # ==========================================================
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Next End"):
            save_end(
                session_id=st.session_state.session_id,
                round_range_id=current_range["id"],
                end_no=st.session_state.current_end,
                arrow_values=arrow_values,
            )
            st.session_state.scores.append(end_total)
            st.session_state.running_total += end_total

            if st.session_state.current_end < ends_per_range:
                st.session_state.current_end += 1
            else:
                st.session_state.range_done = True

            st.rerun()

    with col2:
        if st.button("Reset Round"):
            for k in ["current_end", "current_range", "scores", "running_total", "range_done"]:
                if k == "scores":
                    st.session_state[k] = []
                elif k in ["current_end", "current_range"]:
                    st.session_state[k] = 1
                elif k == "running_total":
                    st.session_state[k] = 0
                else:
                    st.session_state[k] = False
            st.success("Round reset.")
            st.rerun()

    # ==========================================================
    # SUBMIT FOR APPROVAL
    # ==========================================================
    st.markdown("---")
    st.markdown("### Submit Scores for Approval")

    # Count ends to check completeness
    total_ends = sum(r["ends_per_range"] for r in ranges)
    ends_done_row = fetch_one("SELECT COUNT(*) AS c FROM `end` WHERE session_id = :sid", {"sid": st.session_state.session_id})
    ends_done = ends_done_row["c"]

    if st.button("✅ Submit Scores for Approval"):
        if ends_done < total_ends:
            st.warning(
                f"This session is incomplete ({ends_done}/{total_ends} ends recorded). "
                "Are you sure you want to submit anyway?"
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Yes, Submit Anyway"):
                    finalize_session(st.session_state.session_id)
                    st.success("Scores submitted successfully (now Final).")
                    st.rerun()
            with c2:
                st.button("Cancel")
            st.stop()
        else:
            finalize_session(st.session_state.session_id)
            st.success("Scores submitted successfully (now Final).")
            st.rerun()

    # ==========================================================
    # SUMMARY DISPLAY
    # ==========================================================
    st.markdown("### Summary of Ends")
    ends = fetch_all(
        """
        SELECT e.id, e.end_no,
               SUM(CASE WHEN a.arrow_value='X' THEN 10 WHEN a.arrow_value='M' THEN 0 ELSE a.arrow_value END) AS total
        FROM `end` e
        LEFT JOIN arrow a ON a.end_id = e.id
        WHERE e.session_id = :sid
        GROUP BY e.id, e.end_no
        ORDER BY e.end_no
        """,
        {"sid": st.session_state.session_id},
    )
    for e in ends:
        st.write(f"End {e['end_no']}: {e['total']} points")

    if not ends:
        st.caption("_No ends recorded yet._")


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def finalize_session(session_id: int):
    exec_sql("UPDATE session SET status = 'Final' WHERE id = :sid", {"sid": session_id})
    return True


def create_new_session(member_id: int, round_id: int):
    return create_session(member_id=member_id, round_id=round_id, shoot_date=str(date.today()))
