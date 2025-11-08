"""Recorder Approval Page"""
import streamlit as st
import pandas as pd
from guards import require_recorder

@require_recorder
def show_recorder_approval():
# ==========================================================
#  RECORDER PAGE 1: SCORE APPROVAL (Interactive Mock Version)
# ==========================================================
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