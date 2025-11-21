from __future__ import annotations
from datetime import date as dt_date
import pandas as pd
import streamlit as st

from db_core import fetch_all
from guards import require_archer


def _score_sum_case() -> str:
    return (
        "CASE "
        "WHEN UPPER(TRIM(a.arrow_value)) = 'X' THEN 10 "
        "WHEN UPPER(TRIM(a.arrow_value)) = 'M' THEN 0 "
        "ELSE CAST(a.arrow_value AS UNSIGNED) END"
    )


def _chunked(iterable, n: int):
    for i in range(0, len(iterable), n):
        yield iterable[i : i + n]


@require_archer
def show_my_personal_bests():
    st.title("🥇 My Personal Bests")
    st.caption("Your highest confirmed score for each round.")

    auth = st.session_state.get("auth") or {}
    member_id = auth.get("id")
    member_name = auth.get("name", "you")

    if not member_id:
        st.warning("You need to log in to see this page.")
        return

    personal_bests = fetch_all(
        f"""
        WITH session_totals AS (
            SELECT
                s.id AS session_id,
                s.round_id,
                s.shoot_date,
                SUM({_score_sum_case()}) AS total_score
            FROM session s
            JOIN `end` e ON e.session_id = s.id
            JOIN arrow a ON a.end_id = e.id
            WHERE s.member_id = :member_id
              AND s.status = 'Confirmed'
            GROUP BY s.id, s.round_id, s.shoot_date
        ),
        ranked AS (
            SELECT
                st.session_id,
                st.round_id,
                st.shoot_date,
                st.total_score,
                ROW_NUMBER() OVER (
                    PARTITION BY st.round_id
                    ORDER BY st.total_score DESC, st.shoot_date ASC, st.session_id ASC
                ) AS rn
            FROM session_totals st
        )
        SELECT
            r.round_name,
            ranked.total_score,
            ranked.shoot_date
        FROM ranked
        JOIN round r ON r.id = ranked.round_id
        WHERE ranked.rn = 1
        ORDER BY r.round_name;
        """,
        {"member_id": member_id},
    )

    if not personal_bests:
        st.info("No confirmed sessions found yet. Record a score to unlock your PB board!")
        return

    unique_rounds = sorted({row["round_name"] for row in personal_bests})
    round_filter = st.selectbox(
        "Filter by round",
        ["All rounds"] + unique_rounds,
        index=0,
    )

    filtered = (
        personal_bests
        if round_filter == "All rounds"
        else [row for row in personal_bests if row["round_name"] == round_filter]
    )

    top_score_row = max(filtered, key=lambda r: r["total_score"] or 0)
    latest_row = max(filtered, key=lambda r: r["shoot_date"] or dt_date.min)

    st.markdown("### Highlights")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Rounds with PB", len(filtered))
    with col_b:
        st.metric("Highest Score", int(top_score_row["total_score"]))
    with col_c:
        latest_date = latest_row["shoot_date"]
        date_label = latest_date.strftime("%Y-%m-%d") if latest_date else "N/A"
        st.metric("Most Recent PB", date_label)

    st.markdown("### Personal Best Cards")
    cols_per_row = 2
    for row in _chunked(filtered, cols_per_row):
        col_set = st.columns(cols_per_row)
        for col, record in zip(col_set, row):
            with col:
                score = int(record["total_score"]) if record["total_score"] is not None else 0
                shoot_date = record["shoot_date"]
                date_str = shoot_date.strftime("%Y-%m-%d") if shoot_date else "Unknown"
                st.markdown(
                    f"""
                    <div style='border:1px solid #e0e0e0;border-radius:12px;padding:16px;background:#ffffff;'>
                        <div style='font-size:0.9rem;color:#666;'>Round</div>
                        <div style='font-size:1.2rem;font-weight:600;margin-bottom:8px;'>{record['round_name']}</div>
                        <div style='font-size:2rem;font-weight:700;color:#099268;'>{score}</div>
                        <div style='font-size:0.95rem;margin-top:4px;'>Set by <strong>{member_name}</strong></div>
                        <div style='font-size:0.85rem;color:#666;'>on {date_str}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("### Full Table")
    df = pd.DataFrame(filtered)
    df["shoot_date"] = pd.to_datetime(df["shoot_date"]).dt.date
    df = df.rename(
        columns={
            "round_name": "Round",
            "total_score": "Score",
            "shoot_date": "Date",
        }
    )
    st.dataframe(
        df.sort_values("Round"),
        use_container_width=True,
    )
