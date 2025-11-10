import streamlit as st
import pandas as pd
from db_core import fetch_all


def show_competition_results():
    # ==========================================================
    # PAGE HEADER
    # ==========================================================
    st.title("🏁 Competition Results")
    st.caption("View official results from completed competitions")

    # ==========================================================
    # FETCH COMPETITION LIST
    # ==========================================================
    comps = fetch_all(
        "SELECT id, name, start_date, end_date FROM competition ORDER BY start_date DESC"
    )
    if not comps:
        st.info("No competitions found in the database.")
        return

    comp_names = ["Choose a competition..."] + [
        f"{c['name']} ({c['start_date']})" for c in comps
    ]
    selected_comp = st.selectbox("Select Competition", comp_names)

    if selected_comp == "Choose a competition...":
        st.stop()

    comp_index = comp_names.index(selected_comp) - 1
    comp_id = comps[comp_index]["id"]

    # ==========================================================
    # FETCH COMPETITION RESULTS (DB)
    # ==========================================================
    results = fetch_all(
        """
        SELECT 
            d.bow_type_code AS division,
            m.full_name AS archer,
            r.round_name AS round_name,
            ce.final_total AS total_score,
            ce.rank_in_category AS category_rank,
            s.status AS session_status
        FROM competition_entry ce
        JOIN session s ON s.id = ce.session_id
        JOIN club_member m ON m.id = s.member_id
        JOIN division d ON d.id = m.division_id
        JOIN round r ON r.id = s.round_id
        WHERE ce.competition_id = :cid
          AND s.status IN ('Final', 'Confirmed')
        ORDER BY d.bow_type_code, ce.rank_in_category;
        """,
        {"cid": comp_id},
    )

    if not results:
        st.warning("No entries found for this competition.")
        return

    # ==========================================================
    # DISPLAY RESULTS BY DIVISION
    # ==========================================================
    df = pd.DataFrame(results)
    for div, group in df.groupby("division"):
        st.markdown(f"### {div} Division")
        display_df = group[
            ["category_rank", "archer", "round_name", "total_score", "session_status"]
        ].rename(
            columns={
                "category_rank": "Rank",
                "archer": "Archer",
                "round_name": "Round",
                "total_score": "Score",
                "session_status": "Status",
            }
        )
        st.dataframe(
            display_df.style.set_table_styles(
                [
                    {
                        "selector": "thead th",
                        "props": [
                            ("background-color", "#f5f5f5"),
                            ("font-weight", "bold"),
                        ],
                    }
                ]
            ),
            use_container_width=True,
        )