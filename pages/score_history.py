import streamlit as st
from guards import require_archer
from db_core import fetch_all


# ==========================================================
# HELPER FUNCTION – Display a list of sessions
# ==========================================================
def show_sessions(records, label, caption):
    if not records:
        st.info(f"No sessions under {label}.")
        return
    for s in records:
        # light spacing between sessions instead of lines
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.markdown(
                f"<h4 style='font-size:22px; margin-bottom:0'>{s['round_name']} — {s['shoot_date']}</h4>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(f"<b>Status:</b> {label}", unsafe_allow_html=True)
        with col3:
            st.markdown(
                f"<b>Ends:</b> {s['ends_recorded']} / {s['total_ends']}",
                unsafe_allow_html=True,
            )
        st.caption(caption)


# ==========================================================
# MAIN PAGE FUNCTION
# ==========================================================
@require_archer
def show_score_history():
    # ------------------------------------------------------
    # GLOBAL FONT STYLING (applies to entire page)
    # ------------------------------------------------------
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-size: 18px !important;
        }
        h1, h2, h3, h4 {
            font-weight: 700;
        }
        [data-testid="stMarkdownContainer"] label,
        .stRadio label,
        .stTabs [role="tab"] {
            font-size: 17px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("📈 My Score History")
    st.caption("View, resume, or review your recorded sessions")

    auth = st.session_state.get("auth")
    if not auth or not auth.get("logged_in"):
        st.error("⚠️ You must be logged in to view your scores.")
        st.stop()

    member_id = auth["id"]

    # ======================================================
    # FETCH ALL SESSIONS
    # ======================================================
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

    # ======================================================
    # CLASSIFY SESSIONS
    # ======================================================
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

    # ======================================================
    # MAIN LAYOUT – TWO TABS
    # ======================================================
    tab_finished, tab_unfinished = st.tabs(["📋 Finished Sessions", "🕓 Unfinished Sessions"])

    # ------------------------------------------------------
    # TAB 1: FINISHED
    # ------------------------------------------------------
    with tab_finished:
        st.markdown("### Officially Recorded Sessions")
        view_mode = st.radio(
            "Show:",
            ["🟡 Preliminary", "🟦 Final", "🟩 Confirmed"],
            horizontal=True,
            key="finished_filter",
        )

        if view_mode == "🟡 Preliminary":
            show_sessions(
                preliminary,
                "🟡 Submitted (Preliminary)",
                "✅ Completed and awaiting recorder review.",
            )
        elif view_mode == "🟦 Final":
            show_sessions(
                final,
                "🟦 Final (Under Review)",
                "🔒 View-only (Recorder reviewing).",
            )
        elif view_mode == "🟩 Confirmed":
            show_sessions(
                confirmed,
                "🟩 Confirmed (Official Record)",
                "✅ Locked – cannot be modified.",
            )

    # ------------------------------------------------------
    # TAB 2: UNFINISHED
    # ------------------------------------------------------
    with tab_unfinished:
        st.markdown("### 🕓 Unfinished Sessions (Private Drafts)")
        if not unfinished:
            st.info("No unfinished sessions.")
        else:
            for s in unfinished:
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.markdown(
                        f"<h4 style='font-size:22px; margin-bottom:0'>{s['round_name']} — {s['shoot_date']}</h4>",
                        unsafe_allow_html=True,
                    )
                with col2:
                    st.markdown("**Status:** Draft (Not yet submitted)")
                with col3:
                    st.markdown(
                        f"**Progress:** {s['ends_recorded']} / {s['total_ends']}"
                    )

                if st.button("▶ Continue", key=f"resume_{s['session_id']}"):
                    st.session_state.session_id = s["session_id"]
                    st.session_state.selected_round = s["round_name"]
                    st.session_state.current_page = "score_entry"
                    st.rerun()

            st.caption("ℹ️ Only administrators can delete sessions.")