import streamlit as st
from guards import require_archer
from db_core import fetch_all


@require_archer
def show_score_history():
    st.title("📈 My Scores")
    st.caption("View all your recorded sessions and totals")

    auth = st.session_state.get("auth")
    if not auth or not auth.get("logged_in"):
        st.error("⚠️ You must be logged in to view your scores.")
        st.stop()

    member_id = auth["id"]

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
        ORDER BY s.shoot_date DESC;
        """,
        {"mid": member_id},
    )

    if not sessions:
        st.info("No sessions recorded yet.")
        return

    round_options = ["All Rounds"] + sorted({s["round_name"] for s in sessions})
    selected_round = st.selectbox("Filter by Round", round_options)
    if selected_round != "All Rounds":
        sessions = [s for s in sessions if s["round_name"] == selected_round]

    for session in sessions:
        st.markdown("---")
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.subheader(f"{session['round_name']} — {session['shoot_date']}")
        with col2:
            badge = {
                "Preliminary": "🟡 Preliminary",
                "Final": "🟦 Final",
                "Confirmed": "🟢 Confirmed",
            }.get(session["status"], session["status"])
            st.markdown(f"**Status:** {badge}")
        with col3:
            st.markdown(f"**Ends Recorded:** {session['ends_recorded']}")

        # Resume/Edit button for Preliminary only
        if session["status"] == "Preliminary":
            if st.button(f"✏️ Resume / Edit (ID {session['session_id']})", key=f"edit_{session['session_id']}"):
                st.session_state.session_id = session["session_id"]
                st.session_state.selected_round = session["round_name"]
                st.switch_page("score_entry")  # requires multipage setup
        else:
            st.caption("🔒 View-only (already submitted or confirmed)")