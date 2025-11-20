import streamlit as st
from db_core import fetch_all


def _score_sum_case() -> str:
    return (
        "CASE "
        "WHEN UPPER(TRIM(a.arrow_value)) = 'X' THEN 10 "
        "WHEN UPPER(TRIM(a.arrow_value)) = 'M' THEN 0 "
        "ELSE CAST(a.arrow_value AS UNSIGNED) END"
    )


def _chunked(iterable, n):
    for i in range(0, len(iterable), n):
        yield iterable[i : i + n]


def show_club_records():
    st.title("🏛️ Club Records")
    st.caption("Highest confirmed scores per division and gender for a selected round.")

    rounds = fetch_all("SELECT id, round_name FROM round ORDER BY round_name;")
    if not rounds:
        st.info("No rounds are defined yet. Record board cannot be generated.")
        return

    round_lookup = {r["round_name"]: r["id"] for r in rounds}
    round_name = st.selectbox("Select Round", list(round_lookup.keys()))
    selected_round_id = round_lookup.get(round_name)

    records = fetch_all(
        f"""
        WITH session_totals AS (
            SELECT 
                s.id AS session_id,
                s.member_id,
                s.round_id,
                s.shoot_date,
                SUM({_score_sum_case()}) AS total_score
            FROM session s
            JOIN `end` e ON e.session_id = s.id
            JOIN arrow a ON a.end_id = e.id
            WHERE s.status = 'Confirmed'
              AND s.round_id = :round_id
            GROUP BY s.id, s.member_id, s.round_id, s.shoot_date
        ),
        ranked AS (
            SELECT 
                st.session_id,
                st.member_id,
                st.round_id,
                st.shoot_date,
                st.total_score,
                m.full_name,
                ac.age_class_code,
                g.gender_code,
                d.bow_type_code,
                ROW_NUMBER() OVER (
                    PARTITION BY ac.age_class_code, d.bow_type_code, g.gender_code
                    ORDER BY st.total_score DESC, st.shoot_date ASC, st.session_id ASC
                ) AS rn
            FROM session_totals st
            JOIN club_member m ON m.id = st.member_id
            JOIN gender g ON g.id = m.gender_id
            JOIN division d ON d.id = m.division_id
            JOIN age_class ac ON m.birth_year BETWEEN ac.min_birth_year AND ac.max_birth_year
        )
        SELECT 
            full_name,
            age_class_code,
            bow_type_code,
            gender_code,
            total_score,
            shoot_date
        FROM ranked
        WHERE rn = 1
        ORDER BY bow_type_code, gender_code, age_class_code;
        """,
        {"round_id": selected_round_id},
    )

    if not records:
        st.info("No confirmed sessions recorded for this round yet.")
        return

    st.subheader(f"Record Holders for {round_name}")

    cols_per_row = 2
    row_gap = "24px"
    for row in _chunked(records, cols_per_row):
        columns = st.columns(cols_per_row, gap="medium")
        for col, record in zip(columns, row):
            title = f"{record['age_class_code']} {record['gender_code']} {record['bow_type_code']}"
            score = int(record["total_score"]) if record["total_score"] is not None else 0
            date_str = record["shoot_date"].strftime("%Y-%m-%d") if record["shoot_date"] else "Unknown date"
            with col:
                st.markdown(
                    f"""
                    <div style='border:1px solid #e0e0e0;border-radius:12px;padding:20px;background:#fafafa;margin-bottom:{row_gap};height:100%;display:flex;flex-direction:column;justify-content:space-between;'>
                        <div>
                            <div style='font-size:0.9rem;color:#666;'>Category</div>
                            <div style='font-size:1.2rem;font-weight:600;margin-bottom:8px;'>{title}</div>
                        </div>
                        <div>
                            <div style='font-size:2rem;font-weight:700;color:#1c7ed6;'>{score}</div>
                            <div style='font-size:0.95rem;margin-top:4px;'>Shot by <strong>{record['full_name']}</strong></div>
                            <div style='font-size:0.85rem;color:#666;'>on {date_str}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )