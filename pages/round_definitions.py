"""Round Definitions Page"""
import streamlit as st
from data_rounds import list_rounds, list_ranges

def show_round_definitions():
    st.title("📖 Round Definitions")
    st.write("Reference guide for all archery rounds")
    st.markdown("---")

    # Session state for selection is page-local
    if "ui.selected_round_id" not in st.session_state:
        st.session_state["ui.selected_round_id"] = None

    selected_id = st.session_state["ui.selected_round_id"]

    try:
        if selected_id is None:
            rounds = list_rounds()
            if not rounds:
                st.info("No rounds defined yet. Contact the recorder to add rounds.")
            else:
                cols = st.columns(3)
                for idx, r in enumerate(rounds):
                    with cols[idx % 3]:
                        st.container(border=True)
                        st.subheader(f"🎯 {r['round_name']}")
                        count = r["range_count"]
                        st.caption(f"{count} {'range' if count == 1 else 'ranges'}")
                        if st.button("View Details", key=f"view_round_{r['id']}", use_container_width=True):
                            st.session_state["ui.selected_round_id"] = r["id"]
                            st.rerun()
        else:
            # Selected round details
            ranges = list_ranges(selected_id)
            if not ranges:
                st.error("Round not found or has no ranges.")
                st.session_state["ui.selected_round_id"] = None
            else:
                col1, col2 = st.columns([3, 1])
                with col1:
                    name = next((r["round_name"] for r in list_rounds() if r["id"] == selected_id), "Selected Round")
                    st.subheader(name)
                with col2:
                    if st.button("← Back to List", use_container_width=True):
                        st.session_state["ui.selected_round_id"] = None
                        st.rerun()

                total_ends = sum(r["ends_per_range"] for r in ranges)
                total_arrows = total_ends * 6
                st.info(f"📊 Total of {total_ends} ends ({total_arrows} arrows)")
                st.markdown("---")

                for idx, row in enumerate(ranges, 1):
                    st.container(border=True)
                    st.markdown(f"#### 📍 Range {idx}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Distance", f"{row['distance_m']} m")
                    c2.metric("Face Size", f"{row['face_size']} cm")
                    arrows = row["ends_per_range"] * 6
                    c3.metric("Arrows", f"{arrows} ({row['ends_per_range']} ends)")

                st.markdown("---")
                st.success(f"📖 **Total:** {total_arrows} arrows across {len(ranges)} {'range' if len(ranges) == 1 else 'ranges'}")

    except Exception as e:
        st.error(f"Something went wrong while loading round definitions: {e}")