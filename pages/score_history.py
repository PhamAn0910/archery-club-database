"""Score History Page"""
import streamlit as st
from guards import require_archer
from db_core import fetch_all


@require_archer
def show_score_history():
    # ==========================================================
    # PAGE HEADER
    # ==========================================================
    st.title("📈 My Scores")
    st.caption("View all your recorded sessions and totals")

    # ==========================================================
    # LINK WITH LOGIN CONTEXT
    # ==========================================================
    auth = st.session_state.get("auth")
    if not auth or not auth.get("logged_in"):
        st.error("⚠️ You must be logged in to view your scores.")
        st.stop()

    member_id = auth["id"]

    # ==========================================================
    # FETCH SESSION LIST
    # ==========================================================
    sessions = fetch_all(
        """
        SELECT s.id AS session_id,
               DATE(s.shoot_date) AS shoot_date,
               r.round_name,
               s.status,
               COUNT(e.id) AS ends_recorded
        FROM session s
        JOIN round r ON r.id = s.round_id
        LEFT JOIN `end` e ON e.session_id = s.id
        WHERE s.member_id = :mid
        GROUP BY s.id, s.shoot_date, r.round_name, s.status
        ORDER BY s.id DESC
        """,
        {"mid": member_id},
    )

    if not sessions:
        st.info("No sessions recorded yet.")
        return

    # ==========================================================
    # ROUND FILTER
    # ==========================================================
    round_options = ["All Rounds"] + sorted({s["round_name"] for s in sessions})
    selected_round = st.selectbox("Filter by Round", round_options)
    if selected_round != "All Rounds":
        sessions = [s for s in sessions if s["round_name"] == selected_round]

    # ==========================================================
    # DISPLAY EACH SESSION
    # ==========================================================
    for session in sessions:
        st.markdown("---")
        st.subheader(f"🏹 {session['round_name']} — {session['shoot_date']}")
        st.caption(
            f"Session ID: {session['session_id']} | "
            f"Status: {session['status']} | Ends recorded: {session['ends_recorded']}"
        )

        # Fetch end-by-end details
        ends = fetch_all(
            """
            SELECT e.id AS end_id,
                   e.end_no,
                   SUM(
                       CASE 
                           WHEN a.arrow_value = 'M' THEN 0
                           WHEN a.arrow_value = 'X' THEN 10
                           ELSE CAST(a.arrow_value AS UNSIGNED)
                       END
                   ) AS end_total
            FROM `end` e
            LEFT JOIN arrow a ON a.end_id = e.id
            WHERE e.session_id = :sid
            GROUP BY e.id, e.end_no
            ORDER BY e.end_no
            """,
            {"sid": session["session_id"]},
        )

        if not ends:
            st.write("_No ends recorded yet for this session._")
            continue

        # Compute overall total
        total_score = sum(e["end_total"] or 0 for e in ends)

        # Display results
        col1, col2 = st.columns([1, 3])
        col1.metric("Total Score", total_score)
        col2.metric("Ends Recorded", len(ends))

        st.table(ends)


# For standalone testing
if __name__ == "__main__":
    show_score_history()
