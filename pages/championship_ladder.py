import streamlit as st
import pandas as pd
from db_core import fetch_all


def _format_method(method: int) -> str:
    return "Best 1 score" if method == 1 else "Best 2 scores"


def show_championship_ladder():
    # ==========================================================
    # PAGE HEADER
    # ==========================================================
    st.title("🏅 Championship Ladder")
    st.caption("Scores are pulled directly from confirmed sessions that match the ladder rules.")

    # ==========================================================
    # FETCH CHAMPIONSHIPS
    # ==========================================================
    championships = fetch_all(
        """
        SELECT 
            ch.id,
            ch.name,
            ch.start_date,
            ch.end_date,
            ch.category_id,
            CONCAT(ac.age_class_code, ' ', g.gender_code, ' ', d.bow_type_code) AS category_label,
            cat.gender_id,
            cat.division_id,
            ac.min_birth_year,
            ac.max_birth_year
        FROM championship ch
        JOIN category cat ON cat.id = ch.category_id
        JOIN age_class ac ON ac.id = cat.age_class_id
        JOIN gender g ON g.id = cat.gender_id
        JOIN division d ON d.id = cat.division_id
        ORDER BY ch.start_date DESC;
        """
    )

    if not championships:
        st.info("No championships have been configured yet.")
        return

    champ_display = [
        f"{c['name']} ({c['start_date']} → {c['end_date']})" for c in championships
    ]
    selected_label = st.selectbox("Select Championship", champ_display)
    selected_index = champ_display.index(selected_label)
    selected = championships[selected_index]

    st.markdown(
        f"**Category:** {selected['category_label']}  \
        **Window:** {selected['start_date']} to {selected['end_date']}"
    )

    # ==========================================================
    # FETCH RULES FOR THE SELECTED CHAMPIONSHIP
    # ==========================================================
    rules = fetch_all(
        """
        SELECT cr.round_id, r.round_name, cr.score_count_method
        FROM championship_round cr
        JOIN round r ON r.id = cr.round_id
        WHERE cr.championship_id = :cid
        ORDER BY r.round_name;
        """,
        {"cid": selected["id"]},
    )

    if not rules:
        st.warning("This championship has no rounds configured yet.")
        return

    rule_notes = "\n".join(
        f"- **{rule['round_name']}** → {_format_method(rule['score_count_method'])}"
        for rule in rules
    )
    st.markdown("**Scoring Rules**\n" + rule_notes)

    # ==========================================================
    # FETCH ELIGIBLE SESSION SCORES
    # ==========================================================
    round_clause = ", ".join(
        f":round_{idx}" for idx, _ in enumerate(rules)
    )
    params = {
        "start_date": selected["start_date"],
        "end_date": selected["end_date"],
        "gender_id": selected["gender_id"],
        "division_id": selected["division_id"],
        "min_birth_year": selected.get("min_birth_year"),
        "max_birth_year": selected.get("max_birth_year"),
    }
    params.update({f"round_{idx}": rule["round_id"] for idx, rule in enumerate(rules)})

    score_rows = fetch_all(
        f"""
        SELECT 
            s.id AS session_id,
            s.member_id,
            m.full_name,
            s.round_id,
            r.round_name,
            s.shoot_date,
            SUM(
                CASE 
                    WHEN UPPER(TRIM(a.arrow_value)) = 'X' THEN 10
                    WHEN UPPER(TRIM(a.arrow_value)) = 'M' THEN 0
                    ELSE CAST(a.arrow_value AS UNSIGNED)
                END
            ) AS total_score
        FROM session s
        JOIN club_member m ON m.id = s.member_id
        JOIN round r ON r.id = s.round_id
        JOIN `end` e ON e.session_id = s.id
        JOIN arrow a ON a.end_id = e.id
        WHERE s.status = 'Confirmed'
          AND s.shoot_date BETWEEN :start_date AND :end_date
          AND s.round_id IN ({round_clause})
          AND m.gender_id = :gender_id
          AND m.division_id = :division_id
          AND (:min_birth_year IS NULL OR m.birth_year >= :min_birth_year)
          AND (:max_birth_year IS NULL OR m.birth_year <= :max_birth_year)
        GROUP BY s.id, s.member_id, m.full_name, s.round_id, r.round_name, s.shoot_date
        ORDER BY m.full_name, s.round_id, total_score DESC;
        """,
        params,
    )

    if not score_rows:
        st.info("No confirmed sessions match this championship yet.")
        return

    scores_df = pd.DataFrame(score_rows)

    # ==========================================================
    # BUILD LADDER PER ARCHER
    # ==========================================================
    round_order = [rule["round_name"] for rule in rules]

    ladder_rows = []

    grouped = scores_df.groupby(["member_id", "full_name"])
    for (member_id, archer_name), group in grouped:
        row = {"Archer": archer_name, "Total Score": 0, "Complete": True}
        for rule in rules:
            rule_scores = (
                group[group["round_id"] == rule["round_id"]]
                .sort_values("total_score", ascending=False)
            )
            if rule_scores.empty:
                row[rule["round_name"]] = "—"
                row["Complete"] = False
                continue

            take_n = rule["score_count_method"]
            top_scores = [int(score) for score in rule_scores.head(take_n)["total_score"].tolist()]
            round_total = sum(top_scores)
            row[rule["round_name"]] = "+".join(
                str(score) for score in top_scores
            )
            row["Total Score"] += round_total

        ladder_rows.append(row)

    if not ladder_rows:
        st.info("No archers have qualifying scores yet.")
        return

    ladder_df = pd.DataFrame(ladder_rows)
    ladder_df = ladder_df.fillna("—")

    ladder_df = ladder_df.sort_values(
        by=["Complete", "Total Score"], ascending=[False, False]
    ).reset_index(drop=True)

    ranks = []
    complete_rank = 1
    for complete in ladder_df["Complete"]:
        if complete:
            ranks.append(complete_rank)
            complete_rank += 1
        else:
            ranks.append("—")

    ladder_df["Rank"] = ranks

    display_columns = ["Rank", "Archer"] + round_order + ["Total Score"]
    display_df = ladder_df[display_columns]

    incomplete_index = ladder_df.index[~ladder_df["Complete"]].tolist()

    def _row_style(row):
        return ["color: #888888" if row.name in incomplete_index else "" for _ in row]

    st.caption(
        "Archers must have at least one confirmed score per required round to earn a numeric rank."
    )

    st.dataframe(
        display_df.style.apply(_row_style, axis=1).set_table_styles(
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