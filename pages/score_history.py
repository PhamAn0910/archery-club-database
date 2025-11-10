"""Score History Page – Final Version with Correct Classification"""
import streamlit as st
from guards import require_archer
from db_core import fetch_all, exec_sql


@require_archer
def show_score_history():
    st.title("📈 My Score History")
    st.caption("View, resume, or manage your recorded sessions")

    auth = st.session_state.get("auth")
    if not auth or not auth.get("logged_in"):
        st.error("⚠️ You must be logged in to view your scores.")
        st.stop()

    member_id = auth["id"]

    # ==========================================================
    # FETCH ALL SESSIONS + FIXED COMPLETION INFO
    # ==========================================================
    sessions = fetch_all(
        """
        SELECT s.id AS session_id,
               DATE(s.shoot_date) AS shoot_date,
               r.round_name,
               s.status,
               COUNT(DISTINCT e.id) AS ends_recorded,
               (
                   SELECT SUM(rr.ends_per_range)
                   FROM round_range rr
                   WHERE rr.round_id = s.round_id
               ) AS total_ends
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

    # ==========================================================
    # CLASSIFY SESSIONS
    # ==========================================================
    unfinished, preliminary, final, confirmed = [], [], [], []

    for s in sessions:
        ends_done = s["ends_recorded"]
        total_ends = s["total_ends"] or 0
        status = s["status"]

        if status == "Confirmed":
            confirmed.append(s)
        elif status == "Final":
            final.append(s)
        elif status == "Preliminary":
            if ends_done < total_ends:
                unfinished.append(s)
            else:
                preliminary.append(s)

    # ==========================================================
    # UI TABS
    # ==========================================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "🟠 Unfinished",
        "🟡 Submitted (Preliminary)",
        "🟦 Final (Awaiting Confirmation)",
        "🟩 Confirmed (Official)"
    ])

    # ----------------------------------------------------------
    # TAB 1: UNFINISHED
    # ----------------------------------------------------------
    with tab1:
        if not unfinished:
            st.info("No unfinished sessions.")
        for s in unfinished:
            st.markdown("---")
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.subheader(f"{s['round_name']} — {s['shoot_date']}")
            with col2:
                st.markdown("**Status:** 🟠 Unfinished (Private)")
            with col3:
                st.markdown(f"**Progress:** {s['ends_recorded']} / {s['total_ends']}")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("▶ Continue", key=f"resume_{s['session_id']}"):
                    st.session_state.session_id = s["session_id"]
                    st.session_state.selected_round = s["round_name"]
                    st.session_state.current_page = "score_entry"
                    st.rerun()
            with c2:
                if st.button("🗑 Delete", key=f"delete_{s['session_id']}"):
                    exec_sql("DELETE FROM session WHERE id = :sid", {"sid": s["session_id"]})
                    st.success("Unfinished session deleted.")
                    st.rerun()

    # ----------------------------------------------------------
    # TAB 2: PRELIMINARY (Submitted)
    # ----------------------------------------------------------
    with tab2:
        if not preliminary:
            st.info("No submitted (Preliminary) sessions.")
        for s in preliminary:
            st.markdown("---")
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.subheader(f"{s['round_name']} — {s['shoot_date']}")
            with col2:
                st.markdown("**Status:** 🟡 Submitted (Preliminary)")
            with col3:
                st.markdown(f"**Ends:** {s['ends_recorded']} / {s['total_ends']}")

            st.caption("✅ Completed and awaiting recorder review.")
            if st.button("📄 View", key=f"view_{s['session_id']}"):
                st.session_state.session_id = s["session_id"]
                st.session_state.selected_round = s["round_name"]
                st.session_state.current_page = "score_entry"
                st.rerun()

    # ----------------------------------------------------------
    # TAB 3: FINAL (Awaiting Confirmation)
    # ----------------------------------------------------------
    with tab3:
        if not final:
            st.info("No sessions awaiting confirmation.")
        for s in final:
            st.markdown("---")
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.subheader(f"{s['round_name']} — {s['shoot_date']}")
            with col2:
                st.markdown("**Status:** 🟦 Final (Under Review)")
            with col3:
                st.markdown(f"**Ends:** {s['ends_recorded']} / {s['total_ends']}")
            st.caption("🔒 View-only (Recorder reviewing).")

    # ----------------------------------------------------------
    # TAB 4: CONFIRMED (Official)
    # ----------------------------------------------------------
    with tab4:
        if not confirmed:
            st.info("No confirmed (official) sessions.")
        for s in confirmed:
            st.markdown("---")
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.subheader(f"{s['round_name']} — {s['shoot_date']}")
            with col2:
                st.markdown("**Status:** 🟩 Confirmed (Official Record)")
            with col3:
                st.markdown(f"**Ends:** {s['ends_recorded']} / {s['total_ends']}")
            st.caption("✅ Locked – cannot be modified.")
