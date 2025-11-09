"""Recorder Approval Page — Full Version (Editable + Auto-Confirm + Safe Insert)"""
import streamlit as st
import pandas as pd
from guards import require_recorder
from db_core import fetch_all, fetch_one, exec_sql


@require_recorder
def show_recorder_approval():
    # ==========================================================
    #  RECORDER PAGE 1: SCORE APPROVAL
    # ==========================================================
    st.title("Score Approval")
    st.caption("Review, edit, and confirm preliminary scores")

    # ----------------------------------------------------------
    # 1. Fetch pending sessions
    # ----------------------------------------------------------
    pending_query = """
        SELECT 
            s.id           AS session_id,
            cm.full_name   AS archer,
            r.round_name   AS round_name,
            s.shoot_date,
            s.status
        FROM session s
        JOIN club_member cm ON s.member_id = cm.id
        JOIN round r        ON s.round_id = r.id
        WHERE s.status = 'Preliminary'
        ORDER BY s.shoot_date DESC;
    """
    sessions = fetch_all(pending_query)

    if not sessions:
        st.info("✅ All scores have been reviewed. No pending approvals.")
        return

    st.dataframe(
        pd.DataFrame(sessions)[["archer", "round_name", "shoot_date", "status"]],
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("---")

    # ----------------------------------------------------------
    # 2. Iterate through each pending session
    # ----------------------------------------------------------
    for row in sessions:
        sid = row["session_id"]
        title = f"📋 {row['archer']} — {row['round_name']} ({row['shoot_date']})"
        with st.expander(title):
            st.subheader("Arrow Details")

            # --------------------------------------------------
            # Fetch arrows for this session
            # --------------------------------------------------
            arrow_query = """
                SELECT 
                    e.id            AS end_id,
                    rr.distance_m   AS distance,
                    e.end_no,
                    a.arrow_no,
                    a.arrow_value
                FROM `end` e
                JOIN round_range rr ON e.round_range_id = rr.id
                JOIN arrow a        ON a.end_id = e.id
                WHERE e.session_id = :sid
                ORDER BY rr.distance_m DESC, e.end_no, a.arrow_no;
            """
            arrows = fetch_all(arrow_query, {"sid": sid})
            arrow_df = pd.DataFrame(arrows)

            if arrow_df.empty:
                st.warning("No arrow data found for this session.")
                continue

            # --------------------------------------------------
            # Editable grid
            # --------------------------------------------------
            editable_df = st.data_editor(
                arrow_df,
                num_rows="fixed",
                key=f"editor_{sid}",
                use_container_width=True,
                hide_index=True,
            )

            # --------------------------------------------------
            # Save edited arrows
            # --------------------------------------------------
            if st.button("💾 Save Changes", key=f"save_{sid}"):
                for _, row2 in editable_df.iterrows():
                    exec_sql(
                        """
                        UPDATE arrow
                        SET arrow_value = :val
                        WHERE end_id = :eid AND arrow_no = :no;
                        """,
                        {"val": row2["arrow_value"], "eid": row2["end_id"], "no": row2["arrow_no"]},
                    )
                st.success("Arrow values updated successfully.")
                st.rerun()

            st.markdown("---")

            # --------------------------------------------------
            # Recalculate totals
            # --------------------------------------------------
            total_query = """
                SELECT 
                    SUM(
                        CASE 
                            WHEN a.arrow_value = 'X' THEN 10
                            WHEN a.arrow_value = 'M' THEN 0
                            ELSE CAST(a.arrow_value AS UNSIGNED)
                        END
                    ) AS total_points,
                    SUM(a.arrow_value = 'X') AS x_count
                FROM arrow a
                JOIN `end` e ON a.end_id = e.id
                WHERE e.session_id = :sid;
            """
            totals = fetch_one(total_query, {"sid": sid})
            total_points = totals["total_points"] or 0
            x_count = totals["x_count"] or 0

            col_a, col_b = st.columns(2)
            col_a.metric("Total Score", total_points)
            col_b.metric("X Count", x_count)
            st.markdown("---")

            # --------------------------------------------------
            # Confirm / Reject buttons
            # --------------------------------------------------
            col1, col2, col3 = st.columns([1, 1, 5])

            with col2:
                if st.button("✅ Confirm", key=f"confirm_{sid}"):
                    # Update session status
                    exec_sql(
                        """
                        UPDATE session
                        SET status = 'Confirmed'
                        WHERE id = :id;
                        """,
                        {"id": sid},
                    )

                    # Safely insert into competition_entry (no duplicates)
                    insert_query = """
                        INSERT IGNORE INTO competition_entry (session_id, competition_id, category_id, final_total)
                        SELECT 
                            s.id,
                            c.id,
                            cat.id,
                            :total
                        FROM session s
                        JOIN club_member m ON s.member_id = m.id
                        JOIN category cat
                        ON cat.gender_id = m.gender_id
                        AND cat.division_id = m.division_id
                        JOIN competition c
                        ON c.name = 'Club Championship 2025'
                        WHERE s.id = :sid;
                    """
                    exec_sql(insert_query, {"sid": sid, "total": total_points})


                    st.success(
                        f"✅ Confirmed and linked score for {row['archer']} ({row['round_name']})."
                    )
                    st.rerun()

            with col3:
                if st.button("❌ Reject", key=f"reject_{sid}"):
                    exec_sql("DELETE FROM session WHERE id = :id;", {"id": sid})
                    st.error(f"❌ Rejected score for {row['archer']} ({row['round_name']}).")
                    st.rerun()
