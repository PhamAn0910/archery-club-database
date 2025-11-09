"""Personal Bests & Club Records Page"""
import streamlit as st
from guards import require_archer
from db_core import fetch_all


@require_archer
def show_pbs_records():
    # ==========================================================
    # PAGE HEADER
    # ==========================================================
    st.title("🏆 Personal Bests & Club Records")
    st.caption("Track your achievements and compare with club records")

    # ==========================================================
    # AUTH CONTEXT
    # ==========================================================
    auth = st.session_state.get("auth")
    if not auth or not auth.get("logged_in"):
        st.error("Please log in to view your personal bests.")
        st.stop()

    member_id = auth["id"]

    # ==========================================================
    # DIVISION FILTER
    # ==========================================================
    divisions = fetch_all("SELECT bow_type_code FROM division WHERE is_active = 1")
    division_names = ["All Divisions", "Recurve", "Compound", "Longbow", "Recurve Barebow", "Compound Barebow"]
    selected_division = st.selectbox("Filter by Division", division_names)
    st.markdown("---")

    # ==========================================================
    # TABS
    # ==========================================================
    tabs = st.tabs(["My Personal Bests", "Club Records"])

    # ==========================================================
    # TAB 1: PERSONAL BESTS
    # ==========================================================
    with tabs[0]:
        st.subheader("My Personal Bests (Confirmed Sessions Only)")

        pb_query = """
        SELECT 
            r.round_name AS round_name,
            CASE 
                d.bow_type_code 
                WHEN 'R' THEN 'Recurve'
                WHEN 'C' THEN 'Compound'
                WHEN 'L' THEN 'Longbow'
                WHEN 'RB' THEN 'Recurve Barebow'
                WHEN 'CB' THEN 'Compound Barebow'
                ELSE 'Unspecified'
            END AS division,
            s.shoot_date AS date,
            SUM(
                CASE 
                    WHEN a.arrow_value = 'M' THEN 0
                    WHEN a.arrow_value = 'X' THEN 10
                    ELSE CAST(a.arrow_value AS UNSIGNED)
                END
            ) AS total_score
        FROM session s
        JOIN round r ON r.id = s.round_id
        JOIN club_member m ON m.id = s.member_id
        JOIN division d ON d.id = m.division_id
        JOIN `end` e ON e.session_id = s.id
        JOIN arrow a ON a.end_id = e.id
        WHERE s.member_id = :mid
          AND s.status = 'Confirmed'
        GROUP BY s.id, r.round_name, d.bow_type_code, s.shoot_date
        ORDER BY total_score DESC
        """
        pbs = fetch_all(pb_query, {"mid": member_id})

        if not pbs:
            st.info("No confirmed scores yet.")
            st.stop()

        # Keep only the best score per round
        best_by_round = {}
        for row in pbs:
            rn = row["round_name"]
            if rn not in best_by_round or row["total_score"] > best_by_round[rn]["total_score"]:
                best_by_round[rn] = row

        best_list = list(best_by_round.values())
        if selected_division != "All Divisions":
            best_list = [b for b in best_list if b["division"] == selected_division]

        # Display PB cards
        cols = st.columns(min(3, len(best_list)))
        for i, b in enumerate(best_list):
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div style='background-color:white;border:1px solid #eee;
                    border-radius:10px;padding:20px 25px;text-align:center;
                    box-shadow:0 2px 6px rgba(0,0,0,0.05);'>
                        <div style='font-size:28px;'>🎯</div>
                        <h4 style='margin-bottom:2px;'>{b["round_name"]}</h4>
                        <p style='margin-top:0;color:#666;'>{b["division"]}</p>
                        <h2 style='margin:8px 0;color:#222;'>{b["total_score"]}</h2>
                        <p style='color:#999;font-size:14px;'>{b["date"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ==========================================================
    # TAB 2: CLUB RECORDS
    # ==========================================================
    with tabs[1]:
        st.subheader("Club Records (Highest Confirmed Scores)")

        record_query = """
        SELECT 
            r.round_name AS round_name,
            CASE 
                d.bow_type_code 
                WHEN 'R' THEN 'Recurve'
                WHEN 'C' THEN 'Compound'
                WHEN 'L' THEN 'Longbow'
                WHEN 'RB' THEN 'Recurve Barebow'
                WHEN 'CB' THEN 'Compound Barebow'
                ELSE 'Unspecified'
            END AS division,
            m.full_name AS archer,
            s.shoot_date AS date,
            SUM(
                CASE 
                    WHEN a.arrow_value = 'M' THEN 0
                    WHEN a.arrow_value = 'X' THEN 10
                    ELSE CAST(a.arrow_value AS UNSIGNED)
                END
            ) AS total_score
        FROM session s
        JOIN round r ON r.id = s.round_id
        JOIN club_member m ON m.id = s.member_id
        JOIN division d ON d.id = m.division_id
        JOIN `end` e ON e.session_id = s.id
        JOIN arrow a ON a.end_id = e.id
        WHERE s.status = 'Confirmed'
        GROUP BY s.id, r.round_name, d.bow_type_code, m.full_name, s.shoot_date
        ORDER BY total_score DESC
        """
        records = fetch_all(record_query)

        if not records:
            st.info("No confirmed records found.")
            st.stop()

        # Take best record per (round + division)
        record_map = {}
        for row in records:
            key = (row["round_name"], row["division"])
            if key not in record_map or row["total_score"] > record_map[key]["total_score"]:
                record_map[key] = row

        record_list = list(record_map.values())
        if selected_division != "All Divisions":
            record_list = [r for r in record_list if r["division"] == selected_division]

        # Display record cards
        cols = st.columns(min(3, len(record_list)))
        for i, r in enumerate(record_list):
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div style='background-color:white;border:1px solid #eee;
                    border-radius:10px;padding:20px 25px;text-align:center;
                    box-shadow:0 2px 6px rgba(0,0,0,0.05);'>
                        <div style='font-size:30px;color:#d4af37;'>🏆</div>
                        <h4 style='margin-bottom:2px;'>{r["round_name"]}</h4>
                        <p style='margin-top:0;color:#666;'>{r["division"]}</p>
                        <h2 style='margin:8px 0;color:#222;'>{r["total_score"]}</h2>
                        <p style='margin:0;color:#999;font-size:14px;'>{r["archer"]}</p>
                        <p style='margin-top:0;color:#bbb;font-size:13px;'>{r["date"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
