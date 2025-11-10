"""Live Score Entry Page – Final Stable Version"""
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
    }
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)

    # ==========================================================
    # AUTH CONTEXT
    # ==========================================================
    auth = st.session_state.get("auth")
    if not auth or not auth.get("logged_in"):
        st.error("You must be logged in as an archer to enter scores.")
        if st.button("⬅️ Back to My Scores"):
            st.session_state.current_page = "score_history"
            st.rerun()
        st.stop()

    member_id = auth["id"]
    member_name = auth["name"]

    st.title("🏹 Live Score Entry")
    st.subheader(member_name)
    st.caption("Record your scores end by end")

    # ==========================================================
    # HANDLE EXISTING SESSION (RESUME) OR NEW SESSION
    # ==========================================================
    if st.session_state.session_id:
        # Load round info for resumed session
        round_info = fetch_one(
            """
            SELECT r.id AS round_id, r.round_name
            FROM session s
            JOIN round r ON r.id = s.round_id
            WHERE s.id = :sid
            """,
            {"sid": st.session_state.session_id},
        )
        if not round_info:
            st.error("Session not found or invalid.")
            st.stop()

        st.session_state.round_id = round_info["round_id"]
        st.session_state.selected_round = round_info["round_name"]
        selected_round = st.session_state.selected_round
    else:
        # Create new session
        rounds = list_rounds()
        round_names = [""] + [r["round_name"] for r in rounds]
        selected_round = st.selectbox("Choose a round...", round_names, key="round_select")

        if not selected_round:
            st.info("Please select a round to begin.")
            st.stop()

        round_row = fetch_one("SELECT id FROM round WHERE round_name = :rname", {"rname": selected_round})
        if not round_row:
            st.error(f"Round '{selected_round}' not found in database.")
            st.stop()

        st.session_state.round_id = round_row["id"]
        st.session_state.selected_round = selected_round
        st.session_state.session_id = create_session(
            member_id=member_id,
            round_id=st.session_state.round_id,
            shoot_date=str(date.today()),
        )

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

    # ==========================================================
    # RESUME PROGRESS (calculate where to continue)
    # ==========================================================
    resume_rows = fetch_all(
        """
        SELECT rr.id AS range_id, rr.ends_per_range, COUNT(e.id) AS ends_done
        FROM round_range rr
        LEFT JOIN `end` e ON e.round_range_id = rr.id AND e.session_id = :sid
        WHERE rr.round_id = :rid
        GROUP BY rr.id, rr.ends_per_range
        ORDER BY rr.distance_m DESC
        """,
        {"sid": st.session_state.session_id, "rid": st.session_state.round_id},
    )

    for i, r in enumerate(resume_rows, start=1):
        if r["ends_done"] < r["ends_per_range"]:
            st.session_state.current_range = i
            st.session_state.current_end = r["ends_done"] + 1
            break
    else:
        st.session_state.current_range = len(resume_rows)
        st.session_state.current_end = resume_rows[-1]["ends_per_range"]

    total_row = fetch_one(
        """
        SELECT SUM(CASE WHEN a.arrow_value='X' THEN 10
                        WHEN a.arrow_value='M' THEN 0
                        ELSE a.arrow_value END) AS total
        FROM `end` e
        JOIN arrow a ON a.end_id = e.id
        WHERE e.session_id = :sid
        """,
        {"sid": st.session_state.session_id},
    )
    st.session_state.running_total = total_row["total"] or 0

    # ==========================================================
    # RANGE + END INFO
    # ==========================================================
    current_range_idx = st.session_state.current_range - 1
    current_range = ranges[current_range_idx]
    distance = current_range["distance_m"]
    face = current_range["face_size"]
    ends_per_range = current_range["ends_per_range"]

    st.markdown(f"### Range {st.session_state.current_range} of {len(ranges)}")
    st.info(f"Distance: {distance} m • Face: {face} cm")
    st.markdown(f"#### End {st.session_state.current_end} of {ends_per_range}")

    # ==========================================================
    # INPUT SCORES
    # ==========================================================
    score_options = ["M", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "X"]
    arrow_labels = [f"Arrow {i}" for i in range(1, 7)]
    arrow_values = [
        st.selectbox(label, score_options, key=f"{st.session_state.current_range}_{st.session_state.current_end}_{i}")
        for i, label in enumerate(arrow_labels, start=1)
    ]

    def convert(v):
        return 10 if v == "X" else 0 if v == "M" else int(v)

    end_total = sum(convert(a) for a in arrow_values)
    st.metric("End Total", end_total)
    st.metric("Running Total", st.session_state.running_total)

    # ==========================================================
    # ACTIONS
    # ==========================================================
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➡️ Next End"):
            exec_sql(
                """
                INSERT INTO `end` (session_id, round_range_id, end_no)
                SELECT :sid, :rrid, :eno
                WHERE NOT EXISTS (
                    SELECT 1 FROM `end`
                    WHERE session_id = :sid AND round_range_id = :rrid AND end_no = :eno
                );
                """,
                {"sid": st.session_state.session_id, "rrid": current_range["id"], "eno": st.session_state.current_end},
            )
            save_end(
                session_id=st.session_state.session_id,
                round_range_id=current_range["id"],
                end_no=st.session_state.current_end,
                arrow_values=arrow_values,
            )
            st.session_state.running_total += end_total

            # 🔧 Reload progress fresh to ensure correct end numbering
            st.session_state.round_ranges = []
            st.rerun()

    with c2:
        if st.button("⬅️ Back to My Scores"):
            st.session_state.current_page = "score_history"
            st.rerun()

    # ==========================================================
    # SUBMIT (WHEN COMPLETE)
    # ==========================================================
    st.markdown("---")
    st.markdown("### Submit Scores for Approval")

    total_ends = sum(r["ends_per_range"] for r in ranges)
    ends_done_row = fetch_one("SELECT COUNT(*) AS c FROM `end` WHERE session_id = :sid", {"sid": st.session_state.session_id})
    ends_done = ends_done_row["c"]

    if ends_done < total_ends:
        st.warning(f"Session incomplete ({ends_done}/{total_ends} ends). You can resume later.")
    else:
        if st.button("✅ Submit to Recorder"):
            finalize_session(st.session_state.session_id)
            # ✅ Reset to initial mode (Choose Round)
            st.session_state.session_id = None
            st.session_state.round_id = None
            st.session_state.selected_round = None
            st.session_state.round_ranges = []
            st.session_state.current_end = 1
            st.session_state.current_range = 1
            st.session_state.running_total = 0
            st.success("Scores submitted successfully (now Preliminary). Ready for a new session.")
            st.rerun()

    # ==========================================================
    # SUMMARY (Grouped by Range)
    # ==========================================================
    st.markdown("### Summary of Ends")

    summary_rows = fetch_all(
        """
        SELECT rr.distance_m, rr.face_size, e.end_no,
               SUM(CASE WHEN a.arrow_value='X' THEN 10
                        WHEN a.arrow_value='M' THEN 0
                        ELSE a.arrow_value END) AS total
        FROM `end` e
        JOIN round_range rr ON rr.id = e.round_range_id
        LEFT JOIN arrow a ON a.end_id = e.id
        WHERE e.session_id = :sid
        GROUP BY rr.distance_m, rr.face_size, e.end_no
        ORDER BY rr.distance_m DESC, e.end_no ASC
        """,
        {"sid": st.session_state.session_id},
    )

    if not summary_rows:
        st.caption("_No ends recorded yet._")
    else:
        current_distance = None
        for row in summary_rows:
            if row["distance_m"] != current_distance:
                current_distance = row["distance_m"]
                st.markdown(f"#### Range ({current_distance} m, {row['face_size']} cm)")
            st.write(f"End {row['end_no']}: {row['total']} points")


# ==========================================================
# HELPERS
# ==========================================================
def finalize_session(session_id: int):
    # Submitted sessions now marked Preliminary (recorder will confirm later)
    exec_sql("UPDATE session SET status = 'Preliminary' WHERE id = :sid", {"sid": session_id})
    return True
