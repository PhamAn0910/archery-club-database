"""Score Entry Page"""
import streamlit as st
from guards import require_archer

@require_archer
def show_score_entry():
# ==========================================================
#  PAGE 1: LIVE SCORE ENTRY
# ==========================================================
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
                st.rerun()

        # Display previous end totals
        if st.session_state.scores:
            st.markdown("### 🧾 Summary of Ends")
            for i, score in enumerate(st.session_state.scores, start=1):
                st.write(f"End {i}: {score} points")