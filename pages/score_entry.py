from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from db_core import exec_sql, fetch_all, fetch_one
from guards import require_archer

try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

    HAS_AGGRID = True
except Exception:  # pragma: no cover - optional dependency
    HAS_AGGRID = False
    AgGrid = GridOptionsBuilder = GridUpdateMode = None

DATE_FORMAT_UI = "%d-%m-%Y"
DATE_FORMAT_DB = "%Y-%m-%d"
ARROW_CHOICES = ["X", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "M"]

DIVISION_NAME_MAP = {
    "R": "Recurve",
    "C": "Compound",
    "RB": "Recurve Barebow",
    "CB": "Compound Barebow",
    "L": "Longbow",
    "": "No Division",
}


def _division_label(code: Optional[str]) -> str:
    token = (code or "").strip().upper()
    friendly = DIVISION_NAME_MAP.get(token, token or "Unknown")
    suffix = token or "—"
    return f"{friendly} ({suffix})"

@dataclass
class RoundRange:
    id: int
    distance_m: int
    face_size: int
    ends_per_range: int


def _get_member_context(member_id: int) -> Optional[Dict[str, Any]]:
    return fetch_one(
        """
        SELECT cm.id,
               cm.full_name,
               cm.av_number,
               g.gender_code,
               d.bow_type_code,
               d.id AS division_id
        FROM club_member cm
        JOIN gender g ON g.id = cm.gender_id
        JOIN division d ON d.id = cm.division_id
        WHERE cm.id = :mid
        """,
        {"mid": member_id},
    )


@st.cache_data(ttl=300)
def _list_rounds() -> List[Dict[str, Any]]:
    return fetch_all(
        """
        SELECT r.id,
               r.round_name,
               (SELECT SUM(rr.ends_per_range) FROM round_range rr WHERE rr.round_id = r.id) AS total_ends
        FROM round r
        ORDER BY r.round_name
        """
    )


@st.cache_data(ttl=300)
def _list_active_competitions() -> List[Dict[str, Any]]:
    return fetch_all(
        """
        SELECT id,
               name,
               DATE_FORMAT(start_date, :fmt) AS start_fmt,
               DATE_FORMAT(end_date, :fmt) AS end_fmt
        FROM competition
        WHERE end_date >= CURDATE()
        ORDER BY end_date DESC
        """,
        {"fmt": DATE_FORMAT_DB},
    )


@st.cache_data(ttl=300)
def _list_divisions() -> List[Dict[str, Any]]:
    return fetch_all(
        """
        SELECT id, bow_type_code
        FROM division
        WHERE is_active = TRUE OR bow_type_code = ''
        ORDER BY CASE WHEN bow_type_code = '' THEN 1 ELSE 0 END, bow_type_code
        """
    )


def _create_session(member_id: int, round_id: int, division_id: int, shoot_date: datetime.date) -> int:
    exec_sql(
        """
        INSERT INTO session (member_id, round_id, division_id, shoot_date, status)
        VALUES (:mid, :rid, :div_id, :date, 'Preliminary')
        """,
        {
            "mid": member_id,
            "rid": round_id,
            "div_id": division_id,
            "date": shoot_date.strftime(DATE_FORMAT_DB),
        },
    )
    row = fetch_one(
        "SELECT id FROM session WHERE member_id = :mid ORDER BY id DESC LIMIT 1",
        {"mid": member_id},
    )
    if not row:
        raise RuntimeError("Failed to create session")
    return int(row["id"])


def _find_category_for_session(session_id: int) -> Optional[int]:
    """Find the appropriate category for a session based on member and session characteristics."""
    row = fetch_one(
        """
        SELECT cat.id
        FROM session s
        JOIN club_member cm ON cm.id = s.member_id
        JOIN category cat ON (
            cat.gender_id = cm.gender_id 
            AND cat.division_id = s.division_id
        )
        JOIN age_class ac ON ac.id = cat.age_class_id
        WHERE s.id = :sid
          AND cm.birth_year BETWEEN ac.min_birth_year AND ac.max_birth_year
        ORDER BY ac.policy_year DESC
        LIMIT 1
        """,
        {"sid": session_id},
    )
    return row["id"] if row else None


def _link_session_to_competition(session_id: int, competition_id: Optional[int]) -> None:
    if competition_id:
        category_id = _find_category_for_session(session_id)
        if not category_id:
            raise ValueError(f"Could not determine category for session {session_id}")
        
        exec_sql(
            """
            INSERT INTO competition_entry (session_id, competition_id, category_id)
            VALUES (:sid, :cid, :cat_id)
            ON DUPLICATE KEY UPDATE 
                competition_id = VALUES(competition_id),
                category_id = VALUES(category_id)
            """,
            {"sid": session_id, "cid": competition_id, "cat_id": category_id},
        )
    else:
        exec_sql("DELETE FROM competition_entry WHERE session_id = :sid", {"sid": session_id})


def _update_session_division(session_id: int, division_id: int) -> None:
    exec_sql(
        "UPDATE session SET division_id = :div WHERE id = :sid",
        {"div": division_id, "sid": session_id},
    )


def _fetch_session(session_id: int, member_id: int) -> Optional[Dict[str, Any]]:
    return fetch_one(
        """
        SELECT s.id,
               s.member_id,
               s.round_id,
               s.division_id,
               s.status,
               DATE_FORMAT(s.shoot_date, :fmt) AS shoot_date,
               r.round_name,
               d.bow_type_code AS division_code,
               ce.competition_id,
               c.name AS competition_name
        FROM session s
        JOIN round r ON r.id = s.round_id
        LEFT JOIN division d ON d.id = s.division_id
        LEFT JOIN competition_entry ce ON ce.session_id = s.id
        LEFT JOIN competition c ON c.id = ce.competition_id
        WHERE s.id = :sid AND s.member_id = :mid
        """,
        {"sid": session_id, "mid": member_id, "fmt": DATE_FORMAT_DB},
    )


def _load_round_ranges(round_id: int) -> List[RoundRange]:
    rows = fetch_all(
        """
        SELECT id, distance_m, face_size, ends_per_range
        FROM round_range
        WHERE round_id = :rid
        ORDER BY distance_m DESC
        """,
        {"rid": round_id},
    )
    return [RoundRange(**dict(row)) for row in rows]


def _fetch_end_id(session_id: int, range_id: int, end_no: int) -> Optional[int]:
    row = fetch_one(
        "SELECT id FROM `end` WHERE session_id = :sid AND round_range_id = :rid AND end_no = :eno",
        {"sid": session_id, "rid": range_id, "eno": end_no},
    )
    return int(row["id"]) if row else None


def _fetch_arrow_values(end_id: int) -> List[str]:
    rows = fetch_all(
        "SELECT arrow_no, arrow_value FROM arrow WHERE end_id = :eid ORDER BY arrow_no",
        {"eid": end_id},
    )
    values = ["M"] * 6
    for row in rows:
        idx = int(row["arrow_no"]) - 1
        if 0 <= idx < 6:
            values[idx] = row["arrow_value"] or "M"
    return values


def _upsert_end(session_id: int, range_id: int, end_no: int, arrows: List[str]) -> None:
    end_id = _fetch_end_id(session_id, range_id, end_no)
    if not end_id:
        exec_sql(
            "INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (:sid, :rid, :eno)",
            {"sid": session_id, "rid": range_id, "eno": end_no},
        )
        end_id = _fetch_end_id(session_id, range_id, end_no)
    if not end_id:
        raise RuntimeError("Unable to resolve end id after insert")

    exec_sql("DELETE FROM arrow WHERE end_id = :eid", {"eid": end_id})
    for i, value in enumerate(arrows, start=1):
        exec_sql(
            "INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES (:eid, :ano, :aval)",
            {"eid": end_id, "ano": i, "aval": value},
        )


def _compute_session_total(session_id: int) -> int:
    row = fetch_one(
        """
        SELECT SUM(CASE 
                    WHEN UPPER(TRIM(a.arrow_value)) = 'X' THEN 10
                    WHEN UPPER(TRIM(a.arrow_value)) = 'M' THEN 0
                    ELSE CAST(a.arrow_value AS UNSIGNED)
                 END) AS total
        FROM arrow a
        JOIN `end` e ON e.id = a.end_id
        WHERE e.session_id = :sid
        """,
        {"sid": session_id},
    )
    return int(row["total"]) if row and row["total"] is not None else 0


def _count_recorded_ends(session_id: int) -> int:
    row = fetch_one("SELECT COUNT(*) AS c FROM `end` WHERE session_id = :sid", {"sid": session_id})
    return int(row["c"]) if row and row["c"] is not None else 0


def _total_expected_ends(round_id: int) -> int:
    row = fetch_one(
        "SELECT SUM(ends_per_range) AS total FROM round_range WHERE round_id = :rid",
        {"rid": round_id},
    )
    return int(row["total"]) if row and row["total"] is not None else 0


def _build_summary_rows(session_id: int) -> List[Dict[str, Any]]:
    return fetch_all(
        """
        SELECT rr.distance_m,
               rr.face_size,
               e.end_no,
               SUM(CASE 
                    WHEN UPPER(TRIM(a.arrow_value)) = 'X' THEN 10
                    WHEN UPPER(TRIM(a.arrow_value)) = 'M' THEN 0
                    ELSE CAST(a.arrow_value AS UNSIGNED)
               END) AS end_total
        FROM `end` e
        JOIN round_range rr ON rr.id = e.round_range_id
        LEFT JOIN arrow a ON a.end_id = e.id
        WHERE e.session_id = :sid
        GROUP BY rr.distance_m, rr.face_size, e.end_no
        ORDER BY rr.distance_m DESC, e.end_no
        """,
        {"sid": session_id},
    )


def _list_member_drafts(member_id: int) -> List[Dict[str, Any]]:
    return fetch_all(
        """
        SELECT s.id AS session_id,
               DATE_FORMAT(s.shoot_date, :fmt) AS shoot_date,
               r.round_name,
               c.name AS competition_name,
               d.bow_type_code AS division_code,
               (SELECT COUNT(*) FROM `end` e WHERE e.session_id = s.id) AS ends_done,
               (
                   SELECT SUM(rr.ends_per_range)
                   FROM round_range rr
                   WHERE rr.round_id = s.round_id
               ) AS total_ends
        FROM session s
        JOIN round r ON r.id = s.round_id
        JOIN division d ON d.id = s.division_id
        LEFT JOIN competition_entry ce ON ce.session_id = s.id
        LEFT JOIN competition c ON c.id = ce.competition_id
        WHERE s.member_id = :mid AND s.status = 'Preliminary'
        ORDER BY s.shoot_date DESC
        """,
        {"mid": member_id, "fmt": DATE_FORMAT_DB},
    )


def _delete_session(session_id: int, member_id: int) -> None:
    exec_sql(
        "DELETE FROM arrow WHERE end_id IN (SELECT id FROM `end` WHERE session_id = :sid)",
        {"sid": session_id},
    )
    exec_sql("DELETE FROM `end` WHERE session_id = :sid", {"sid": session_id})
    exec_sql("DELETE FROM competition_entry WHERE session_id = :sid", {"sid": session_id})
    exec_sql("DELETE FROM session WHERE id = :sid AND member_id = :mid", {"sid": session_id, "mid": member_id})


def _reset_score_entry_state() -> None:
    for key in [
        "score_entry_session_id",
        "score_entry_editor",
        "score_entry_resume_notice",
    ]:
        st.session_state.pop(key, None)


def _get_editor_state(session_id: int) -> Dict[str, Any]:
    state = st.session_state.setdefault("score_entry_editor", {})
    if state.get("session_id") != session_id:
        state.clear()
        state["session_id"] = session_id
        state["range_idx"] = 0
        state["end_no"] = 1
    state.setdefault("range_idx", 0)
    state.setdefault("end_no", 1)
    return state


def _arrow_select_key(session_id: int, range_id: int, end_no: int, arrow_idx: int) -> str:
    return f"arrow_{session_id}_{range_id}_{end_no}_{arrow_idx}"


def _status_badge(status: str) -> str:
    mapping = {
        "Preliminary": "🟡 Preliminary",
        "Final": "🟦 Final",
        "Confirmed": "🟩 Confirmed",
    }
    return mapping.get(status, status)


def _arrow_index(value: str | None) -> int:
    token = (value or "M").strip().upper()
    try:
        return ARROW_CHOICES.index(token)
    except ValueError:
        return len(ARROW_CHOICES) - 1


def _score_from_value(value: str | None) -> int:
    token = (value or "M").strip().upper()
    if token == "X":
        return 10
    if token == "M":
        return 0
    try:
        return int(token)
    except ValueError:
        return 0


def _update_competition_final_total(session_id: int) -> None:
    """Calculate and update the final_total in competition_entry for a session."""
    total_score = _compute_session_total(session_id)
    exec_sql(
        "UPDATE competition_entry SET final_total = :total WHERE session_id = :sid",
        {"total": total_score, "sid": session_id}
    )

@require_archer
def show_score_entry():
    st.title("🏹 Archer Score Entry")
    st.caption("Create new sessions, finish drafts, and submit to your recorder")

    auth = st.session_state.get("auth")
    if not auth or not auth.get("logged_in"):
        st.error("You must be logged in as an archer to record scores.")
        if st.button("↩ Back to Score History"):
            st.session_state.current_page = "score_history"
            st.rerun()
        st.stop()

    member_id = auth["id"]
    member_ctx = _get_member_context(member_id)
    if member_ctx:
        st.caption(
            f"Signed in as {member_ctx['full_name']} — {member_ctx['bow_type_code']} {member_ctx['gender_code']}"
        )

    if st.button("↩ Back to Score History", key="nav_history"):
        # Clear any score entry session state when navigating back
        _reset_score_entry_state()
        st.session_state.current_page = "score_history"
        st.rerun()

    notice = st.session_state.pop("score_entry_resume_notice", None)
    if notice:
        st.success(notice)

    session_id = st.session_state.get("score_entry_session_id")
    if not session_id:
        _render_session_launcher(member_id, member_ctx)
        return

    session = _fetch_session(session_id, member_id)
    if not session:
        st.error("Session not found or you no longer have access to it.")
        _reset_score_entry_state()
        return

    ranges = _load_round_ranges(session["round_id"])
    if not ranges:
        st.warning("This round is missing distance definitions. Please contact a recorder.")
        return

    shoot_date_ui = datetime.datetime.strptime(session["shoot_date"], DATE_FORMAT_DB).strftime(
        DATE_FORMAT_UI
    )
    # total_score and recorded_ends are calculated in _render_score_editor
    total_ends = _total_expected_ends(session["round_id"])

    info_col1, info_col2, info_col3 = st.columns(3)
    with info_col1:
        st.markdown("**Shoot Date**")
        st.markdown(f"### {shoot_date_ui}")
    with info_col2:
        st.markdown("**Status**")
        st.markdown(f"### {_status_badge(session['status'])}")
    with info_col3:
        st.markdown("**Competition**")
        st.markdown(f"### {session['competition_name'] or 'Unassigned'}")

    card1, card2, card3 = st.columns(3)
    with card1:
        st.markdown("**Round**")
        st.markdown(f"### {session['round_name']}")
    # Score and Progress metrics are updated in _render_score_editor for better state sync

    if session["status"] != "Preliminary":
        st.info("This session is locked. You can view details but not modify arrows.")
    else:
        if st.button("🗑️ Delete Draft", type="secondary"):
            _delete_session(session_id, member_id)
            _reset_score_entry_state()
            st.success("Draft deleted.")
            st.rerun()

    _render_score_editor(session, ranges, total_ends, card2, card3)
    _render_summary_table(session_id)


def _render_session_launcher(member_id: int, member_ctx: Optional[Dict[str, Any]]) -> None:
    st.subheader("Start or resume a session")
    tab_new, tab_resume = st.tabs(["✨ New Session", "⏳ Drafts"])

    with tab_new:
        rounds = _list_rounds()
        if not rounds:
            st.info("No rounds are configured yet. Please ask an admin to add some.")
            return

        divisions = _list_divisions()
        if not divisions:
            st.info("No equipment divisions are available. Please contact a recorder.")
            return

        round_labels = {
            f"{row['round_name']} ({row['total_ends']} ends)": row["id"] for row in rounds
        }
        competitions = _list_active_competitions()
        
        # Check if competitions are available
        if not competitions:
            st.warning("No active competitions found. Contact a recorder to create one.")
            return

        comp_labels: Dict[str, int] = {}
        for comp in competitions:
            label = f"{comp['name']} (ends {datetime.datetime.strptime(comp['end_fmt'], DATE_FORMAT_DB).strftime(DATE_FORMAT_UI)})"
            comp_labels[label] = comp["id"]

        division_labels: Dict[str, int] = {}
        default_division_id = (member_ctx or {}).get("division_id")
        default_idx = 0
        for idx, div in enumerate(divisions):
            label = _division_label(div["bow_type_code"])
            division_labels[label] = div["id"]
            if div["id"] == default_division_id:
                default_idx = idx

        with st.form("start_session_form"):
            shoot_date = st.date_input("Shoot date", value=datetime.date.today())
            round_choice = st.selectbox("Round", list(round_labels.keys()))
            comp_choice = st.selectbox("Competition", list(comp_labels.keys()))
            equipment_choice = st.selectbox(
                "Equipment for this session",
                list(division_labels.keys()),
                index=min(default_idx, len(division_labels) - 1),
                help="Use this to record the bow/division actually used on the day.",
            )
            submitted = st.form_submit_button("Start Session", width="stretch")

        if submitted:
            new_session_id = _create_session(
                member_id,
                round_labels[round_choice],
                division_labels[equipment_choice],
                shoot_date,
            )
            comp_id = comp_labels[comp_choice]
            _link_session_to_competition(new_session_id, comp_id)
            st.session_state.score_entry_session_id = new_session_id
            st.session_state.score_entry_resume_notice = "New session created. Happy shooting!"
            st.rerun()

    with tab_resume:
        drafts = _list_member_drafts(member_id)
        if not drafts:
            st.info("No drafts available. Start a new session above.")
            return

        df = pd.DataFrame(drafts)
        if not df.empty and "division_code" in df:
            df["Division"] = df["division_code"].apply(_division_label)
        # First rename columns
        df = df.rename(
            columns={
                "session_id": "Session ID",
                "shoot_date": "Shoot Date",
                "round_name": "Round",
                "competition_name": "Competition",
                "ends_done": "Ends Done",
                "total_ends": "Total Ends",
            }
        )
        # Then handle legacy data with null competition names
        if not df.empty and "Competition" in df:
            df["Competition"] = df["Competition"].fillna("Unassigned")
        if "division_code" in df:
            df = df.drop(columns=["division_code"])
        desired_cols = [
            "Session ID",
            "Shoot Date",
            "Round",
            "Division",
            "Competition",
            "Ends Done",
            "Total Ends",
        ]
        df = df[[col for col in desired_cols if col in df.columns]]

        selected_id: Optional[int] = None
        if HAS_AGGRID:
            builder = GridOptionsBuilder.from_dataframe(df)
            builder.configure_selection("single", use_checkbox=False)
            builder.configure_column("Session ID", hide=True)
            grid = AgGrid(
                df,
                gridOptions=builder.build(),
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                height=300,
                allow_unsafe_jscode=True,
                theme="streamlit",
            )
            
            selected_rows = grid.get("selected_rows")
            if selected_rows is not None and len(selected_rows) > 0:
                if isinstance(selected_rows, pd.DataFrame):
                    row = selected_rows.iloc[0]
                else:
                    row = selected_rows[0]
                    
                selected_id = int(row["Session ID"])
                st.session_state.score_entry_session_id = selected_id
                st.session_state.score_entry_resume_notice = "Draft loaded."
                st.rerun()
        else:
            st.dataframe(df, width="stretch")
            selected_id = st.selectbox(
                "Select a draft",
                options=[None, *df["Session ID"].tolist()],
                format_func=lambda v: "--" if v is None else f"Session {v}",
            )

            if selected_id and st.button("Resume draft", width="stretch"):
                st.session_state.score_entry_session_id = selected_id
                st.session_state.score_entry_resume_notice = "Draft loaded."
                st.rerun()


def _render_competition_linker(session: Dict[str, Any]) -> None:
    with st.expander("Competition link", expanded=False):
        competitions = _list_active_competitions()
        if not competitions:
            st.warning("No active competitions available. Contact a recorder.")
            return
            
        options: List[str] = []
        label_to_id: Dict[str, int] = {}
        index = 0
        for idx, comp in enumerate(competitions):
            label = f"{comp['name']} (ends {datetime.datetime.strptime(comp['end_fmt'], DATE_FORMAT_DB).strftime(DATE_FORMAT_UI)})"
            options.append(label)
            label_to_id[label] = comp["id"]
            if comp["id"] == session.get("competition_id"):
                index = idx

        selection = st.selectbox("Linked competition", options=options, index=index)
        chosen_id = label_to_id.get(selection)

        if st.button("Update link", key=f"comp_update_{session['id']}"):
            _link_session_to_competition(session["id"], chosen_id)
            st.session_state.score_entry_resume_notice = "Competition link updated."
            st.rerun()


def _render_equipment_selector(
    session: Dict[str, Any], editable: bool, member_ctx: Optional[Dict[str, Any]]
) -> None:
    with st.expander("Equipment for this session", expanded=False):
        divisions = _list_divisions()
        if not divisions:
            st.info("No equipment divisions configured. Please contact a recorder.")
            return

        label_to_id: Dict[str, int] = {}
        options: List[str] = []
        current_idx = 0
        for idx, div in enumerate(divisions):
            label = _division_label(div["bow_type_code"])
            options.append(label)
            label_to_id[label] = div["id"]
            if div["id"] == session.get("division_id"):
                current_idx = idx

        profile_label = _division_label(member_ctx.get("bow_type_code") if member_ctx else None)
        st.caption(f"Profile default: {profile_label}")

        selection = st.selectbox(
            "Equipment used",
            options=options,
            index=min(current_idx, len(options) - 1),
            disabled=not editable,
        )
        chosen_id = label_to_id.get(selection, session.get("division_id"))
        needs_update = chosen_id != session.get("division_id")
        if not editable:
            st.caption("Session is locked; equipment can't be changed.")
            return

        st.button(
            "Update equipment",
            key=f"equip_{session['id']}",
            type="secondary",
            disabled=not needs_update,
            on_click=lambda: _apply_equipment_update(session["id"], chosen_id),
        )


def _apply_equipment_update(session_id: int, division_id: Optional[int]) -> None:
    if division_id is None:
        return
    _update_session_division(session_id, division_id)
    st.session_state.score_entry_resume_notice = "Equipment updated."
    st.rerun()


def _nav_callback(
    session_id: int,
    range_id: int,
    current_end: int,
    arrow_keys: List[str],
    end_select_key: str,
    range_select_key: str,
    state: Dict[str, Any],
    direction: str,
    max_ends: int,
    editable: bool,
) -> None:
    # 1. Save current arrows if editable
    if editable:
        # We read directly from session_state because the widgets have updated it
        values = [st.session_state.get(k, "M") for k in arrow_keys]
        _upsert_end(session_id, range_id, current_end, values)

    # 2. Update navigation state
    if direction == "prev":
        new_val = max(1, current_end - 1)
        state["end_no"] = new_val
        st.session_state[end_select_key] = new_val

    elif direction == "next":
        new_val = min(max_ends, current_end + 1)
        state["end_no"] = new_val
        st.session_state[end_select_key] = new_val

    elif direction == "next_range":
        # Move to next range, reset end to 1
        new_range_idx = state.get("range_idx", 0) + 1
        state["range_idx"] = new_range_idx
        state["end_no"] = 1
        # Force update the range selectbox
        st.session_state[range_select_key] = new_range_idx

    elif direction == "submit":
        exec_sql("UPDATE session SET status = 'Final' WHERE id = :sid", {"sid": session_id})
        _update_competition_final_total(session_id)
        st.session_state.score_entry_resume_notice = "Session submitted for review!"


def _render_score_editor(
    session: Dict[str, Any],
    ranges: List[RoundRange],
    total_ends: int,
    score_col: Any,
    progress_col: Any,
) -> None:
    session_id = session["id"]
    editable = session["status"] == "Preliminary"
    state = _get_editor_state(session_id)

    previous_range_idx = state.get("range_idx", 0)
    range_select_key = f"range_select_{session_id}"
    range_idx = st.selectbox(
        "Range",
        options=list(range(len(ranges))),
        format_func=lambda i: f"{ranges[i].distance_m} m • {ranges[i].face_size} cm (×{ranges[i].ends_per_range})",
        index=min(previous_range_idx, len(ranges) - 1),
        key=range_select_key,
    )
    
    if range_idx != previous_range_idx:
        state["range_idx"] = range_idx
        state["end_no"] = 1

    current_range = ranges[range_idx]

    end_rows = fetch_all(
        """
        SELECT id, end_no
        FROM `end`
        WHERE session_id = :sid AND round_range_id = :rid
        ORDER BY end_no
        """,
        {"sid": session_id, "rid": current_range.id},
    )
    end_lookup = {int(row["end_no"]): int(row["id"]) for row in end_rows}
    end_options = list(range(1, current_range.ends_per_range + 1))

    end_select_key = f"end_select_{session_id}_{current_range.id}"
    end_idx = min(state.get("end_no", 1) - 1, len(end_options) - 1)
    selected_end = st.selectbox(
        "End",
        options=end_options,
        format_func=lambda n: f"End {n}{'' if n in end_lookup else ' (new)'}",
        index=end_idx,
        key=end_select_key,
    )
    state["end_no"] = selected_end

    if selected_end in end_lookup:
        end_id = end_lookup[selected_end]
        base_values = _fetch_arrow_values(end_id)
    else:
        end_id = None
        base_values = ["M"] * 6

    arrow_cols = st.columns(6)
    arrow_values: List[str] = []
    arrow_keys: List[str] = []
    values_changed = False
    
    for arrow_idx, col in enumerate(arrow_cols, start=1):
        key = _arrow_select_key(session_id, current_range.id, selected_end, arrow_idx)
        arrow_keys.append(key)
        new_value = col.selectbox(
            f"Arrow {arrow_idx}",
            ARROW_CHOICES,
            index=_arrow_index(base_values[arrow_idx - 1]),
            key=key,
            disabled=not editable,
        )
        arrow_values.append(new_value)
        if new_value != base_values[arrow_idx - 1]:
            values_changed = True

    # Auto-save when values change
    if editable and values_changed:
        _upsert_end(session_id, current_range.id, selected_end, arrow_values)

    # Update global metrics
    current_score = _compute_session_total(session_id)
    with score_col:
        st.markdown("**Score**")
        st.markdown(f"### {current_score}")

    with progress_col:
        st.markdown("**Progress**")
        st.markdown(f"### {selected_end}/{current_range.ends_per_range} ends")

    end_total = sum(_score_from_value(val) for val in arrow_values)
    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.markdown("**End Score**")
        st.markdown(f"### {end_total}")
    with summary_col2:
        st.markdown("**Session Total**")
        st.markdown(f"### {current_score}")

    # Navigation buttons
    nav_col1, nav_col2 = st.columns(2)
    
    # Previous button
    nav_col1.button(
        "◀ Previous",
        disabled=selected_end == 1,
        width="stretch",
        key=f"prev_{session_id}_{current_range.id}_{selected_end}",
        on_click=_nav_callback,
        args=(
            session_id,
            current_range.id,
            selected_end,
            arrow_keys,
            end_select_key,
            range_select_key,
            state,
            "prev",
            current_range.ends_per_range,
            editable,
        ),
    )
    
    # Next button or Submit button
    is_last_end = selected_end >= current_range.ends_per_range
    is_last_range = range_idx >= len(ranges) - 1
    
    if is_last_end and is_last_range:
        # This is the last end of the last range - show submit button
        nav_col2.button(
            "✅ Submit for Review",
            width="stretch",
            type="primary",
            key=f"submit_{session_id}_{current_range.id}_{selected_end}",
            on_click=_nav_callback,
            args=(
                session_id,
                current_range.id,
                selected_end,
                arrow_keys,
                end_select_key,
                range_select_key,
                state,
                "submit",
                current_range.ends_per_range,
                editable,
            ),
        )
    elif is_last_end and not is_last_range:
        # Last end of current range - move to next range
        nav_col2.button(
            "Next Range ▶",
            width="stretch",
            key=f"next_range_{session_id}_{current_range.id}_{selected_end}",
            on_click=_nav_callback,
            args=(
                session_id,
                current_range.id,
                selected_end,
                arrow_keys,
                end_select_key,
                range_select_key,
                state,
                "next_range",
                current_range.ends_per_range,
                editable,
            ),
        )
    else:
        # Regular next end button
        nav_col2.button(
            "Next ▶",
            width="stretch",
            key=f"next_{session_id}_{current_range.id}_{selected_end}",
            on_click=_nav_callback,
            args=(
                session_id,
                current_range.id,
                selected_end,
                arrow_keys,
                end_select_key,
                range_select_key,
                state,
                "next",
                current_range.ends_per_range,
                editable,
            ),
        )


def _render_summary_table(session_id: int) -> None:
    st.markdown("---")
    st.subheader("Range summary")
    rows = _build_summary_rows(session_id)
    if not rows:
        st.caption("No ends recorded yet.")
        return
    df = pd.DataFrame(rows)
    df["distance"] = df["distance_m"].astype(int).astype(str) + " m"
    # Ensure end_total is properly converted to integer
    df["end_total"] = pd.to_numeric(df["end_total"], errors="coerce").fillna(0).astype(int)
    df = df.rename(columns={"face_size": "Face", "end_no": "End", "end_total": "Score"})
    st.dataframe(df[["distance", "Face", "End", "Score"]], width="stretch", hide_index=True)