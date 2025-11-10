"""Championship Ladder Page – Database-Driven (Fixed)"""
import streamlit as st
import pandas as pd
from db_core import fetch_all


def show_championship_ladder():
    # ==========================================================
    # PAGE HEADER
    # ==========================================================
    st.title("🏅 Club Championship Standings")
    st.caption("Automatically calculated from championship competitions")
    st.info("Top 3 highest competition totals per archer contribute to their Championship Score.")

    # ==========================================================
    # FETCH CHAMPIONSHIP ENTRIES (Confirmed only)
    # ==========================================================
    data = fetch_all(
        """
        SELECT 
            m.id AS member_id,
            m.full_name AS archer,
            d.bow_type_code AS division,
            ce.final_total AS score,
            c.name AS competition_name,
            c.start_date
        FROM competition_entry ce
        JOIN competition c ON c.id = ce.competition_id
        JOIN session s ON s.id = ce.session_id
        JOIN club_member m ON m.id = s.member_id
        JOIN division d ON d.id = m.division_id
        WHERE LOWER(c.name) LIKE '%championship%'
          AND ce.final_total IS NOT NULL
          AND s.status = 'Confirmed'
        ORDER BY d.bow_type_code, m.id, ce.final_total DESC;
        """
    )

    if not data:
        st.info("No championship results found in the database.")
        return

    df = pd.DataFrame(data)

    # ==========================================================
    # CALCULATE TOP 3 TOTALS PER ARCHER
    # ==========================================================
    ladder = []
    for (division, archer), group in df.groupby(["division", "archer"]):
        top3 = group.nlargest(3, "score")
        total = top3["score"].sum()
        scores_list = ", ".join(str(x) for x in top3["score"].tolist())
        ladder.append(
            {
                "division": division,
                "archer": archer,
                "championship_score": total,
                "counted_scores": scores_list,
            }
        )

    ladder_df = pd.DataFrame(ladder)
    ladder_df = ladder_df.sort_values(
        ["division", "championship_score"], ascending=[True, False]
    )

    # ==========================================================
    # DISPLAY LADDER
    # ==========================================================
    for div, group in ladder_df.groupby("division"):
        st.markdown(f"### {div} Division")
        group = group.reset_index(drop=True)

        # Dynamically match rank length
        ranks = ["🥇 1st", "🥈 2nd", "🥉 3rd"]
        if len(group) > 3:
            ranks += [f"{i+4}th" for i in range(len(group) - 3)]
        group["Rank"] = ranks[:len(group)]

        display_df = group[
            ["Rank", "archer", "championship_score", "counted_scores"]
        ].rename(
            columns={
                "archer": "Archer",
                "championship_score": "Championship Score",
                "counted_scores": "Counted Scores",
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
