import streamlit as st
import pandas as pd
from datetime import date
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

    # --------------------------------------------------
    # DATE RANGE FILTER
    # --------------------------------------------------
    min_start = min(c["start_date"] for c in comps)
    max_end = max(c["end_date"] for c in comps)

    default_range = (min_start, max_end)
    date_range = st.date_input(
        "Filter by Date Range",
        value=default_range,
        min_value=min_start,
        max_value=max_end,
    )

    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_filter, end_filter = date_range
    else:
        start_filter = end_filter = date_range

    if start_filter > end_filter:
        st.error("Start date must be on or before the end date.")
        st.stop()

    comps_in_range = [
        c for c in comps if start_filter <= c["start_date"] <= end_filter
    ]

    if not comps_in_range:
        st.warning("No competitions fall within the selected date range.")
        st.stop()

    comp_names = ["Choose a competition..."] + [
        f"{c['name']} ({c['start_date']})" for c in comps_in_range
    ]
    selected_comp = st.selectbox("Select Competition", comp_names)

    if selected_comp == "Choose a competition...":
        st.stop()

    comp_index = comp_names.index(selected_comp) - 1
    comp_id = comps_in_range[comp_index]["id"]

    # ==========================================================
    # FETCH COMPETITION RESULTS (DB)
    # ==========================================================
    results = fetch_all(
        """
        SELECT 
            ce.rank_in_category AS placement,
            m.full_name AS archer,
            CONCAT(ac.age_class_code, ' ', g.gender_code, ' ', d.bow_type_code) AS category_label,
            r.round_name AS round_name,
            ce.final_total AS total_score,
            s.shoot_date AS shoot_date
        FROM competition_entry ce
        JOIN session s ON s.id = ce.session_id
        JOIN club_member m ON m.id = s.member_id
        JOIN category cat ON cat.id = ce.category_id
        JOIN age_class ac ON ac.id = cat.age_class_id
        JOIN gender g ON g.id = cat.gender_id
        JOIN division d ON d.id = cat.division_id
        JOIN round r ON r.id = s.round_id
        WHERE ce.competition_id = :cid
          AND s.status = 'Confirmed'
          AND s.shoot_date BETWEEN :start_date AND :end_date
          AND ce.final_total IS NOT NULL
        ORDER BY category_label, placement, total_score DESC;
        """,
        {"cid": comp_id, "start_date": start_filter, "end_date": end_filter},
    )

    if not results:
        st.warning("No confirmed entries found for this competition in the chosen range.")
        return

    # ==========================================================
    # DISPLAY RESULTS BY DIVISION
    # ==========================================================
    df = pd.DataFrame(results)
    df["Date"] = pd.to_datetime(df["shoot_date"]).dt.date
    display_df = df.rename(
        columns={
            "placement": "Rank",
            "archer": "Archer",
            "category_label": "Category",
            "round_name": "Round",
            "total_score": "Score",
        }
    )[["Rank", "Archer", "Category", "Round", "Score", "Date"]]

    display_df = display_df.sort_values(["Score", "Rank"], ascending=[False, True])

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