"""Recorder Management Page"""
import streamlit as st
import pandas as pd
from guards import require_recorder
from db_core import fetch_all, fetch_one, exec_sql


@require_recorder
def show_recorder_management():
    # ==========================================================
    #  RECORDER PAGE 2: ADMIN MANAGEMENT
    # ==========================================================
    st.title("Admin Management")
    st.caption("Manage club data and system configuration")

    tabs = st.tabs(["👥 User Management", "🎯 Round Management", "🏆 Competition Setup"])

    # ==========================================================
    # TAB 1: USER MANAGEMENT
    # ==========================================================
    with tabs[0]:
        st.subheader("👥 User Management")
        st.info("Add, edit, or deactivate club users.")

        # Fetch all current members
        members = fetch_all("""
            SELECT cm.id,
                   cm.av_number AS AV_Number,
                   cm.full_name AS Name,
                   cm.birth_year AS Birth_Year,
                   g.gender_code AS Gender,
                   d.bow_type_code AS Division,
                   CASE WHEN cm.is_recorder THEN 'Recorder' ELSE 'Archer' END AS Role
            FROM club_member cm
            JOIN gender g ON g.id = cm.gender_id
            JOIN division d ON d.id = cm.division_id
            ORDER BY cm.full_name;
        """)

        if members:
            st.dataframe(pd.DataFrame(members), use_container_width=True)
        else:
            st.warning("No members found in the database.")

        st.markdown("#### ➕ Add New Member")
        with st.form("add_member_form"):
            full_name = st.text_input("Full Name")
            birth_year = st.number_input("Birth Year", 1900, 2025)
            gender = st.selectbox("Gender", ["M", "F"])
            division = st.selectbox("Division", ["R", "C", "RB", "CB", "L", ""])
            is_recorder = st.checkbox("Is Recorder?")
            submitted = st.form_submit_button("Add Member")

            if submitted and full_name:
                exec_sql("""
                    INSERT INTO club_member (full_name, birth_year, gender_id, division_id, is_recorder)
                    VALUES (
                        :full_name,
                        :birth_year,
                        (SELECT id FROM gender WHERE gender_code = :gender),
                        (SELECT id FROM division WHERE bow_type_code = :division),
                        :is_recorder
                    );
                """, {
                    "full_name": full_name,
                    "birth_year": birth_year,
                    "gender": gender,
                    "division": division,
                    "is_recorder": is_recorder,
                })
                st.success(f"✅ Added new member: {full_name}")
                st.rerun()

    # ==========================================================
    # TAB 2: ROUND MANAGEMENT
    # ==========================================================
    with tabs[1]:
        st.subheader("🎯 Round Management")
        st.info("Add or update official round definitions.")

        rounds = fetch_all("SELECT id, round_name AS Name FROM round ORDER BY round_name;")
        if rounds:
            st.dataframe(pd.DataFrame(rounds), use_container_width=True)
        else:
            st.warning("No rounds found.")

        st.markdown("#### ➕ Add New Round")
        with st.form("add_round_form"):
            round_name = st.text_input("Round Name")
            submitted = st.form_submit_button("Create Round")
            if submitted and round_name:
                exec_sql("INSERT INTO round (round_name) VALUES (:name);", {"name": round_name})
                st.success(f"✅ Round '{round_name}' added.")
                st.rerun()

        st.markdown("#### ➕ Add Round Range")
        round_names = [r["Name"] for r in rounds] if rounds else []
        with st.form("add_range_form"):
            selected_round = st.selectbox("Select Round", round_names)
            distance_m = st.number_input("Distance (m)", 10, 100)
            face_size = st.selectbox("Face Size (cm)", [80, 122])
            ends_per_range = st.selectbox("Ends per Range", [5, 6])
            submitted = st.form_submit_button("Add Range")
            if submitted and selected_round:
                exec_sql("""
                    INSERT INTO round_range (round_id, distance_m, face_size, ends_per_range)
                    VALUES (
                        (SELECT id FROM round WHERE round_name = :rname),
                        :distance_m, :face_size, :ends_per_range
                    );
                """, {
                    "rname": selected_round,
                    "distance_m": distance_m,
                    "face_size": face_size,
                    "ends_per_range": ends_per_range
                })
                st.success(f"✅ Range added to {selected_round}")
                st.rerun()

    # ==========================================================
    # TAB 3: COMPETITION SETUP
    # ==========================================================
    with tabs[2]:
        st.subheader("🏆 Competition Setup")
        st.info("Define club competitions and link them to rounds.")

        comps = fetch_all("""
            SELECT id, name AS Competition, start_date AS Start, end_date AS End, rules_note AS Notes
            FROM competition
            ORDER BY start_date DESC;
        """)

        if comps:
            st.dataframe(pd.DataFrame(comps), use_container_width=True)
        else:
            st.warning("No competitions found.")

        st.markdown("#### ➕ Add New Competition")
        with st.form("add_comp_form"):
            name = st.text_input("Competition Name")
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            rules_note = st.text_area("Rules / Notes")
            submitted = st.form_submit_button("Create Competition")
            if submitted and name:
                exec_sql("""
                    INSERT INTO competition (name, start_date, end_date, rules_note)
                    VALUES (:name, :start, :end, :rules);
                """, {
                    "name": name,
                    "start": start_date,
                    "end": end_date,
                    "rules": rules_note
                })
                st.success(f"✅ Competition '{name}' created.")
                st.rerun()

