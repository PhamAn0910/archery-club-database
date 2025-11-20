from __future__ import annotations

import datetime
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from db_core import exec_sql, fetch_all, fetch_one
from guards import require_archer

try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

    HAS_AGGRID = True
except Exception:  # pragma: no cover - optional dependency
    HAS_AGGRID = False
    GridOptionsBuilder = GridUpdateMode = AgGrid = None

DATE_FORMAT_UI = "%d-%m-%Y"
ARROW_CHOICES = ["X", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "M"]

DIVISION_NAME_MAP = {
    "R": "Recurve",
    "C": "Compound",
    "RB": "Recurve Barebow",
    "CB": "Compound Barebow",
    "L": "Longbow",
    "": "No Division",
}


def _division_label(code: str | None) -> str:
    token = (code or "").strip().upper()
    friendly = DIVISION_NAME_MAP.get(token, token or "Unknown")
    suffix = token or "—"
    return f"{friendly} ({suffix})"


# ============================================================================
# DATA HELPERS
# ============================================================================

def _arrow_index(value: str | None) -> int:
    token = (value or "M").strip().upper()
    try:
        return ARROW_CHOICES.index(token)
    except ValueError:
        return len(ARROW_CHOICES) - 1


def _fetch_member_context(member_id: int) -> Dict[str, Any] | None:
    return fetch_one(
        """
        SELECT cm.id,
               cm.full_name,
               cm.birth_year,
               cm.gender_id,
               cm.division_id,
               g.gender_code,
               d.bow_type_code,
               (
                   SELECT ac.age_class_code
                   FROM age_class ac
                   WHERE cm.birth_year BETWEEN ac.min_birth_year AND ac.max_birth_year
                   ORDER BY ac.policy_year DESC
                   LIMIT 1
               ) AS age_class_code
        FROM club_member cm
        JOIN gender g ON g.id = cm.gender_id
        JOIN division d ON d.id = cm.division_id
        WHERE cm.id = :mid
        """,
        {"mid": member_id},
    )


def _score_sum_case() -> str:
    return (
        "CASE "
        "WHEN UPPER(TRIM(a.arrow_value)) = 'X' THEN 10 "
        "WHEN UPPER(TRIM(a.arrow_value)) = 'M' THEN 0 "
        "ELSE CAST(a.arrow_value AS UNSIGNED) END"
    )


def _fetch_sessions(member_id: int) -> List[Dict[str, Any]]:
    return fetch_all(
        f"""
        SELECT 
            s.id AS session_id,
            s.shoot_date,
            r.round_name,
            s.status,
            d.bow_type_code AS division_code,
            COALESCE(comp.name, 'Practice (No Competition)') AS competition_name,
            COALESCE(SUM({_score_sum_case()}), 0) AS total_score
        FROM session s
        JOIN round r ON r.id = s.round_id
        JOIN division d ON d.id = s.division_id
        LEFT JOIN competition_entry ce ON ce.session_id = s.id
        LEFT JOIN competition comp ON comp.id = ce.competition_id
        LEFT JOIN `end` e ON e.session_id = s.id
        LEFT JOIN arrow a ON a.end_id = e.id
        WHERE s.member_id = :mid
        GROUP BY s.id, s.shoot_date, r.round_name, s.status, division_code, competition_name
        ORDER BY s.shoot_date DESC, s.id DESC;
        """,
        {"mid": member_id},
    )


def _delete_draft_session(session_id: int, member_id: int) -> None:
    exec_sql(
        "DELETE FROM session WHERE id = :sid AND member_id = :mid AND status = 'Preliminary'",
        {"sid": session_id, "mid": member_id},
    )


# ---------------------------------------------------------------------------
# Session detail helpers for the read-only score view
# ---------------------------------------------------------------------------

def _fetch_session_metadata(session_id: int, member_id: int) -> Dict[str, Any] | None:
    return fetch_one(
        """
        SELECT s.id,
               s.round_id,
               s.shoot_date,
               s.status,
               r.round_name
        FROM session s
        JOIN round r ON r.id = s.round_id
        WHERE s.id = :sid AND s.member_id = :mid
        """,
        {"sid": session_id, "mid": member_id},
    )


def _fetch_round_ranges(round_id: int) -> List[Dict[str, Any]]:
    return fetch_all(
        """
        SELECT id, distance_m, face_size, ends_per_range
        FROM round_range
        WHERE round_id = :rid
        ORDER BY distance_m DESC
        """,
        {"rid": round_id},
    )


def _fetch_arrow_payload(session_id: int) -> Dict[tuple[int, int], Dict[str, Any]]:
    arrow_rows = fetch_all(
        """
        SELECT e.id AS end_id,
               e.round_range_id,
               e.end_no,
               a.arrow_no,
               a.arrow_value
        FROM `end` e
        LEFT JOIN arrow a ON a.end_id = e.id
        WHERE e.session_id = :sid
        ORDER BY e.round_range_id, e.end_no, a.arrow_no
        """,
        {"sid": session_id},
    )
    payload: Dict[tuple[int, int], Dict[str, Any]] = {}
    for row in arrow_rows:
        key = (row["round_range_id"], row["end_no"])
        entry = payload.setdefault(
            key, {"end_id": row["end_id"], "values": ["M"] * 6}
        )
        if row["arrow_no"]:
            entry["values"][row["arrow_no"] - 1] = row["arrow_value"] or "M"
    return payload


def _render_read_only_editor(session_id: int, member_id: int) -> None:
    session = _fetch_session_metadata(session_id, member_id)
    if not session:
        st.warning("Session not found or you do not have access to it.")
        return

    ranges = _fetch_round_ranges(session["round_id"])
    if not ranges:
        st.info("Round definition missing; cannot display arrows.")
        return

    payload = _fetch_arrow_payload(session_id)
    st.markdown(
        f"#### {session['round_name']} — {session['shoot_date'].strftime(DATE_FORMAT_UI)}"
    )
    st.caption("Read-only view. Contact a Recorder for changes.")

    range_labels = [
        f"{idx+1}. {rng['distance_m']} m • {rng['face_size']} cm (×{rng['ends_per_range']} ends)"
        for idx, rng in enumerate(ranges)
    ]
    selected_idx = st.selectbox(
        "Select Distance",
        options=list(range(len(ranges))),
        format_func=lambda i: range_labels[i],
        key=f"history_range_select_{session_id}",
    )
    selected_range = ranges[selected_idx]

    end_numbers = list(range(1, selected_range["ends_per_range"] + 1))
    end_idx = st.selectbox(
        "Select End",
        options=end_numbers,
        key=f"history_end_select_{session_id}_{selected_range['id']}",
    )

    values = payload.get((selected_range["id"], end_idx), {}).get("values", ["M"] * 6)
    cols = st.columns(6)
    for arrow_idx, col in enumerate(cols):
        col.selectbox(
            f"Arrow {arrow_idx + 1}",
            options=ARROW_CHOICES,
            index=_arrow_index(values[arrow_idx]),
            disabled=True,
            key=f"history_arrow_{session_id}_{selected_range['id']}_{end_idx}_{arrow_idx}",
        )

    st.markdown("---")


@require_archer
def show_score_history():
    st.title("🏹 My Score Sessions")
    st.caption("Review drafts, submissions, and confirmed scores in one place")

    auth = st.session_state.get("auth")
    if not auth or not auth.get("logged_in"):
        st.error("⚠️ You must be logged in to view your scores.")
        st.stop()

    member_id = auth["id"]
    member_ctx = _fetch_member_context(member_id)
    if member_ctx:
        st.caption(
            f"Signed in as {member_ctx['full_name']} • {member_ctx['bow_type_code']} {member_ctx['gender_code']} {member_ctx.get('age_class_code', '')}"
        )

    sessions = _fetch_sessions(member_id)

    if not sessions:
        st.info("No sessions recorded yet. Use the Score Entry page to create one.")
        return

    df = pd.DataFrame(sessions)
    df["shoot_date"] = pd.to_datetime(df["shoot_date"]).dt.date
    df["shoot_date_fmt"] = df["shoot_date"].apply(lambda d: d.strftime(DATE_FORMAT_UI))
    df["division_label"] = df["division_code"].apply(_division_label)
    df["status_label"] = df["status"].map(
        {
            "Preliminary": "🟡 Preliminary",
            "Final": "🟦 Final",
            "Confirmed": "🟩 Confirmed",
        }
    )
    df["can_edit"] = df["status"].eq("Preliminary")
    df["can_delete"] = df["status"].eq("Preliminary")

    # ------------------------------------------------------------------
    # Filters (status, competition/practice, date range)
    # ------------------------------------------------------------------
    with st.container():
        col_status, col_comp, col_date = st.columns([1.5, 1.5, 2])

        status_options = sorted(df["status_label"].dropna().unique().tolist())
        selected_statuses = col_status.multiselect(
            "Status",
            options=status_options,
            default=status_options,
        )

        competition_options = [
            "Practice (No Competition)",
            *sorted(
                {
                    name
                    for name in df["competition_name"].dropna()
                    if name != "Practice (No Competition)"
                }
            ),
        ]
        selected_competitions = col_comp.multiselect(
            "Competition",
            options=competition_options,
            default=competition_options,
        )

        min_date, max_date = df["shoot_date"].min(), df["shoot_date"].max()
        date_range = col_date.date_input(
            "Shoot date range",
            value=(min_date, max_date),
        )
        if isinstance(date_range, datetime.date):
            date_range = (date_range, date_range)

    filtered = df[
        df["status_label"].isin(selected_statuses)
        & df["competition_name"].isin(selected_competitions)
        & df["shoot_date"].between(date_range[0], date_range[1])
    ].copy()

    if filtered.empty:
        st.warning("No sessions match your filters.")
        return

    with st.container():
        cards = st.columns(3)
        cards[0].metric("Visible Sessions", len(filtered))
        cards[1].metric("Total Score", int(filtered["total_score"].sum()))
        cards[2].metric("Drafts", int(filtered["can_edit"].sum()))

    display_cols = [
        "session_id",
        "shoot_date_fmt",
        "round_name",
        "division_label",
        "status_label",
        "total_score",
        "competition_name",
    ]
    display_df = filtered[display_cols].rename(
        columns={
            "session_id": "Session ID",
            "shoot_date_fmt": "Shoot Date",
            "round_name": "Round",
            "division_label": "Equipment",
            "status_label": "Status",
            "total_score": "Score",
            "competition_name": "Competition",
        }
    )

    selected_session_id: int | None = None
    selected_row: Dict[str, Any] | None = None

    if HAS_AGGRID:
        builder = GridOptionsBuilder.from_dataframe(display_df)
        builder.configure_selection("single", use_checkbox=True)
        builder.configure_pagination(enabled=True, paginationAutoPageSize=True)
        grid = AgGrid(
            display_df,
            gridOptions=builder.build(),
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            height=420,
            theme="streamlit",
        )
        selected_rows = grid.get("selected_rows", [])
        if isinstance(selected_rows, list) and selected_rows:
            selected_session_id = int(selected_rows[0]["Session ID"])
        elif hasattr(selected_rows, '__len__') and len(selected_rows) > 0:
            # Handle pandas DataFrame case
            selected_session_id = int(selected_rows.iloc[0]["Session ID"])
        else:
            selected_session_id = None
    else:
        st.dataframe(display_df, use_container_width=True, height=420)
        selected_session_id = st.selectbox(
            "Select a session for actions",
            options=[None, *display_df["Session ID"].tolist()],
            format_func=lambda val: "-- Select --" if val is None else str(val),
        )

    if selected_session_id:
        selected_row = filtered.loc[
            filtered["session_id"] == selected_session_id
        ].iloc[0]

    st.markdown("---")

    if selected_session_id is None:
        st.info("Select a session in the table to take actions or view details.")
        return

    st.subheader(
        f"Session #{selected_row['session_id']} — {selected_row['round_name']} ({selected_row['status_label']})"
    )
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.write(f"**Shoot date:** {selected_row['shoot_date_fmt']}")
    col_b.write(f"**Score:** {int(selected_row['total_score'])}")
    col_c.write(f"**Competition:** {selected_row['competition_name']}")
    col_d.write(f"**Equipment:** {selected_row['division_label']}")

    action_col1, action_col2, action_col3 = st.columns(3)
    resume_disabled = not bool(selected_row["can_edit"])
    delete_disabled = not bool(selected_row["can_delete"])

    if action_col1.button(
        "▶ Resume Editing",
        use_container_width=True,
        disabled=resume_disabled,
        key=f"resume_{selected_session_id}",
    ):
        st.session_state.score_entry_session_id = selected_session_id
        st.session_state.score_entry_mode = "resume"
        st.session_state.current_page = "score_entry"
        st.success("Loading session in Score Entry …")
        st.rerun()

    if action_col2.button(
        "🗑️ Delete Draft",
        use_container_width=True,
        disabled=delete_disabled,
        key=f"delete_{selected_session_id}",
    ):
        _delete_draft_session(selected_session_id, member_id)
        st.success("Draft deleted.")
        st.rerun()

    if action_col3.button(
        "👁️ View Arrows",
        use_container_width=True,
        key=f"view_{selected_session_id}",
    ):
        st.session_state.setdefault("score_history_viewing", {})[
            "session_id"
        ] = selected_session_id

    viewing_id = st.session_state.get("score_history_viewing", {}).get("session_id")
    if viewing_id == selected_session_id:
        _render_read_only_editor(selected_session_id, member_id)
    else:
        st.caption("Use “View Arrows” to inspect per-end detail.")