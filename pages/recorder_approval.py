"""Recorder Approval (DB-backed)

This page lists sessions entered into club competitions and lets recorders 
edit arrow values (6 arrows per end), change status, and confirm sessions. 
All edits persist to the archery_db via db_core.

Features implemented (per your requirements):
- Remove manual competition selection filter.
- Filter is ONE line with 3 columns:
  (1) current competition status, (2) competition date range, (3) round filter.
- Day-left warnings:
  - Appear at the very top, right under the main title.
  - Include competitions ending today (days_left == 0).
  - All competitions ending today / in 1–2 days appear in ONE paragraph (single warning).
- Group Approve:
  - CAN approve Final -> Confirmed.
  - CANNOT revert Confirmed -> Preliminary (for consistency with Change Status).
  - NO st.metric counters, but KEEP protected warnings.
- Change Status:
  - ALSO cannot revert Confirmed -> Preliminary (consistency).
- Status changes create audit trail.
- Editing protections: Sessions locked after competition end date.
- Date display format: dd-mm-yyyy (UI), yyyy-mm-dd (database/backend).
- Tab header: "{logged-in AV number}: {Competition name} - ends {comp_end}"

Note: Sessions are a database normalization concept. In the UI, they represent 
an archer's score for a round shot on a specific date, linked to competitions via
competition_entry.
"""

# =====================================================
# IMPORTS
# =====================================================
import datetime
from typing import List, Dict, Optional, Set

import streamlit as st
import pandas as pd
from db_core import fetch_all, exec_sql, fetch_one
from sqlalchemy.exc import ProgrammingError
from guards import require_recorder

# =====================================================
# AGGRID INTEGRATION
# =====================================================
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
    HAS_AGGRID = True
except Exception:
    HAS_AGGRID = False
    AgGrid = GridOptionsBuilder = GridUpdateMode = None


# =====================================================
# GLOBAL CONSTANTS
# =====================================================
DAYS_BEFORE_WARNING = 2  # Warn if competition ends within this many days
DATE_FORMAT_UI = "%d/%m/%Y"  # dd-mm-yyyy for UI display
DATE_FORMAT_DB = "%Y-%m-%d"  # yyyy-mm-dd for database/backend


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def _get_recorder_id() -> Optional[int]:
    """Get the current recorder's member ID from session state."""
    auth = st.session_state.get("auth", {})
    return auth.get("id")

def _today_date() -> datetime.date:
    """Return today's date."""
    return datetime.date.today()


def _parse_date(s: str) -> datetime.date:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.datetime.strptime(s, DATE_FORMAT_DB).date()
    except Exception:
        return _today_date()


def _format_date_for_ui(date: datetime.date) -> str:
    """Format a date object for UI display (dd-mm-yyyy)."""
    return date.strftime(DATE_FORMAT_UI)


def _format_date_for_db(date: datetime.date) -> str:
    """Format a date object for database operations (yyyy-mm-dd)."""
    return date.strftime(DATE_FORMAT_DB)


def _score_from_arrow(a: str) -> int:
    """Convert arrow value to numeric score."""
    if not a:
        return 0
    a_upper = str(a).upper().strip()
    if a_upper == 'X':
        return 10
    if a_upper == 'M':
        return 0
    try:
        return int(a_upper)
    except Exception:
        return 0


def _build_av_number_map(sessions: List[Dict]) -> Dict[int, str]:
    """Build mapping from member_id to av_number."""
    member_ids = list({s['member_id'] for s in sessions})
    member_av_map: Dict[int, str] = {}

    if not member_ids:
        return member_av_map

    try:
        rows = fetch_all(
            "SELECT id, av_number FROM club_member WHERE id IN :ids",
            params={'ids': tuple(member_ids)}
        )
        for r in rows:
            member_av_map[r['id']] = str(r['av_number'] or r['id'])
    except Exception:
        for mid in member_ids:
            member_av_map[mid] = str(mid)

    return member_av_map


def _compute_session_total(session_id: int) -> int:
    """Compute total score for a session by summing all arrow scores."""
    try:
        total_row = fetch_one(
            "SELECT SUM(CASE "
            "WHEN UPPER(TRIM(a.arrow_value)) = 'X' THEN 10 "
            "WHEN UPPER(TRIM(a.arrow_value)) = 'M' THEN 0 "
            "ELSE CAST(a.arrow_value AS UNSIGNED) END) AS total "
            "FROM arrow a JOIN `end` e ON a.end_id = e.id WHERE e.session_id = :sid",
            params={'sid': session_id}
        )
        return int(total_row['total']) if total_row and total_row['total'] is not None else 0
    except Exception:
        return 0


# =====================================================
# SESSION STATUS MANAGEMENT
# =====================================================

def _update_session_status(session_id: int, old_status: str, new_status: str):
    """Update session status and write audit trail."""
    exec_sql(
        "UPDATE session SET status = :status WHERE id = :id",
        params={'status': new_status, 'id': session_id}
    )
    recorder_id = _get_recorder_id()
    try:
        exec_sql(
            "INSERT INTO session_audit (session_id, old_status, new_status, changed_by) "
            "VALUES (:session_id, :old, :new, :by)",
            params={'session_id': session_id, 'old': old_status, 'new': new_status, 'by': recorder_id}
        )
    except Exception as ae:
        if isinstance(ae, ProgrammingError) or 'session_audit' in str(ae) or '1146' in str(ae):
            st.warning("Audit table missing; status updated but audit row was not recorded.")
        else:
            st.error(f"Failed to write audit row: {ae}")


# =====================================================
# ARROW EDITOR
# =====================================================

def _render_arrow_editor(session_id: int, end_id: int, end_no: int, protected: bool, comp_end: datetime.date):
    """Render the 6-arrow editor for a single end."""
    arrows = fetch_all(
        "SELECT arrow_no, arrow_value FROM arrow WHERE end_id = :end_id ORDER BY arrow_no",
        params={'end_id': end_id}
    )
    arrow_vals = [a['arrow_value'] for a in arrows]

    while len(arrow_vals) < 6:
        arrow_vals.append('M')

    cols = st.columns(6)
    new_vals: List[str] = []
    choices = ['X', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', 'M']

    for i in range(6):
        with cols[i]:
            cur = arrow_vals[i]
            idx = choices.index(cur) if cur in choices else len(choices) - 1
            new = st.selectbox(
                f"Arrow {i+1}",
                options=choices,
                index=idx,
                key=f"arrow_{session_id}_{end_id}_{i}_{comp_end.strftime(DATE_FORMAT_DB)}",
                disabled=protected
            )
            new_vals.append(new)

    if not protected and new_vals != arrow_vals:
        for i, nv in enumerate(new_vals):
            if i < len(arrows):
                exec_sql(
                    "UPDATE arrow SET arrow_value = :value WHERE end_id = :end_id AND arrow_no = :arrow_no",
                    params={'value': nv, 'end_id': end_id, 'arrow_no': i + 1}
                )
            else:
                exec_sql(
                    "INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES (:end_id, :arrow_no, :value)",
                    params={'end_id': end_id, 'arrow_no': i + 1, 'value': nv}
                )

    return new_vals


# =====================================================
# STATUS EDITOR
# =====================================================

def _render_status_editor(session: Dict, comp_end: datetime.date):
    """Render inline status editor when Status cell is clicked."""
    session_id = session['session_id']
    status = session['status']
    today = _today_date()
    protected = (today > comp_end)

    st.markdown(f"### Change Status: {session.get('av_number', 'N/A')} — {session['round_name']}")

    if protected:
        st.warning(f"Status is locked at '{status}' (competition ended on {_format_date_for_ui(comp_end)})")
        return

    new_status = st.selectbox(
        "Select new status",
        options=['Preliminary', 'Final', 'Confirmed'],
        index=['Preliminary', 'Final', 'Confirmed'].index(status),
        key=f"status_edit_{session_id}"
    )

    if st.button("Apply", key=f"apply_status_{session_id}", type="primary", use_container_width=True):
        # CONSISTENCY RULE:
        # Never allow Confirmed -> Preliminary (single-edit).
        if status in ("Confirmed", "Final") and new_status == "Preliminary":
            st.warning(
                f"Reverting a {status} score back to Preliminary is not allowed.",
                icon=":material/lock:"
            )
            return

        if new_status != status:
            _update_session_status(session_id, status, new_status)
            st.session_state[f"status_msg_{session_id}"] = f"Status updated from '{status}' to '{new_status}'"
        else:
            _update_session_status(session_id, status, new_status)
            st.session_state[f"status_msg_{session_id}"] = f"Status has been updated to {new_status}"

        comp_id = session.get('competition_id') or 'unassigned'
        st.session_state.pop(f"show_status_{comp_id}", None)
        st.rerun()


# =====================================================
# GROUP APPROVE/REVERT EDITOR
# =====================================================

def _render_group_approve_editor(sess_list: List[Dict], comp_end: datetime.date, comp_key: str):
    """
    Render group approve/revert interface with filtering and preview.
    Per requirements:
    - No metrics.
    - Keep protected warnings for competitions that ended.
    - Allow Final -> Confirmed in bulk (approve).
    - Forbid Confirmed -> Preliminary in bulk.
    """
    st.markdown("### Group Approve/Revert")
    st.caption("Change status for multiple sessions at once with filtering options")

    today = _today_date()

    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        current_status_filter = st.multiselect(
            "Filter by Current Status",
            options=['Preliminary', 'Final', 'Confirmed'],
            default=['Preliminary'],
            key=f"bulk_current_status_{comp_key}"
        )

    with col_filter2:
        round_filter = st.multiselect(
            "Filter by Round",
            options=sorted(list(set(s['round_name'] for s in sess_list))),
            key=f"bulk_round_{comp_key}"
        )

    with col_filter3:
        av_filter = st.text_input(
            "Filter by AV Number (partial match)",
            key=f"bulk_av_{comp_key}"
        )

    filtered_sessions = [
        s for s in sess_list
        if (not current_status_filter or s['status'] in current_status_filter)
        and (not round_filter or s['round_name'] in round_filter)
        and (not av_filter or av_filter.lower() in s.get('av_number', '').lower())
    ]

    if not filtered_sessions:
        st.info("No sessions match the current filters.")
        return

    if today > comp_end:
        st.warning(
            "All sessions are protected (competition has ended). Bulk changes are disabled.",
            icon=":material/lock:"
        )
        return

    editable_sessions = filtered_sessions

    st.markdown("##### :material/view_list: Preview Affected Sessions")
    preview_data = [{
        'AV Number': s.get('av_number', 'N/A'),
        'Round': s['round_name'],
        'Shoot Date': s['shoot_date'],
        'Current Status': s['status']
    } for s in editable_sessions]

    df_preview = pd.DataFrame(preview_data)
    st.dataframe(df_preview, use_container_width=True, hide_index=True)

    st.markdown("")
    col_action1, col_action2, col_action3 = st.columns([2, 1, 2])

    with col_action1:
        new_bulk_status = st.selectbox(
            "Change all filtered sessions to:",
            options=['Preliminary', 'Final', 'Confirmed'],
            key=f"bulk_new_status_{comp_key}"
        )

    with col_action2:
        st.write("")
        st.write("")
        confirm_bulk = st.checkbox(
            "I confirm",
            key=f"bulk_confirm_{comp_key}",
            help="Check this box to enable the Apply button"
        )

    with col_action3:
        st.write("")
        st.write("")
        if st.button(
            f"Apply to {len(editable_sessions)} Session(s)",
            key=f"bulk_apply_{comp_key}",
            type="primary",
            icon=":material/list_alt_check:",
            disabled=not confirm_bulk,
            use_container_width=True
        ):
            _execute_group_approve_change(editable_sessions, new_bulk_status, comp_key)


def _execute_group_approve_change(sessions: List[Dict], new_status: str, comp_key: str):
    """
    Execute group approve/revert status change with clearer messages.
    Rules:
      - Final -> Confirmed is allowed.
      - Confirmed -> Preliminary is NOT allowed (only forbidden revert).
    """
    success_count = 0
    skipped_count = 0
    error_count = 0

    blocked_confirmed_to_prelim = 0
    failed_sessions: List[Dict] = []
    already_target_sessions: List[Dict] = []
    updated_from_statuses: Set[str] = set()

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, session in enumerate(sessions):
        old_status = session['status']
        av = session.get('av_number', 'N/A')

        try:
            if old_status == new_status:
                skipped_count += 1
                already_target_sessions.append(session)
                continue

            if old_status in ("Confirmed", "Final") and new_status == "Preliminary":
                skipped_count += 1
                blocked_confirmed_to_prelim += 1
                continue

            _update_session_status(session['session_id'], old_status, new_status)
            success_count += 1
            updated_from_statuses.add(old_status)

        except Exception as e:
            error_count += 1
            failed_sessions.append({
                "av_number": av,
                "round_name": session.get("round_name", "N/A"),
                "shoot_date": session.get("shoot_date", "N/A"),
                "error": str(e)
            })

        progress = (idx + 1) / len(sessions)
        progress_bar.progress(progress)
        status_text.text(f"Processing: {idx + 1}/{len(sessions)}")

    progress_bar.empty()
    status_text.empty()

    st.session_state[f'bulk_results_{comp_key}'] = {
        "success_count": success_count,
        "skipped_count": skipped_count,
        "error_count": error_count,
        "new_status": new_status,
        "blocked_confirmed_to_prelim": blocked_confirmed_to_prelim,
        "already_target_count": len(already_target_sessions),
        "failed_sessions": failed_sessions,
        "updated_from_statuses": sorted(list(updated_from_statuses)),
    }

    if success_count > 0 or error_count > 0 or skipped_count > 0:
        st.session_state.pop(f"show_bulk_{comp_key}", None)
        st.balloons()
        st.rerun()


# =====================================================
# SCORE EDITOR
# =====================================================

def _render_score_editor(session: Dict, comp_end: datetime.date):
    """Render the score editor panel when Total Score cell is clicked."""
    session_id = session['session_id']
    today = _today_date()
    protected = (today > comp_end)

    view_mode = " (View Only)" if protected else ""
    st.markdown(
        f"### Score Editor{view_mode}: "
        f"{session.get('av_number', 'N/A')} — {session['round_name']} "
        f"— {_format_date_for_ui(_parse_date(session['shoot_date']))} – {_format_date_for_ui(comp_end)}"
    )

    ranges = fetch_all(
        "SELECT id, distance_m, face_size, ends_per_range FROM round_range "
        "WHERE round_id = :round_id ORDER BY distance_m DESC",
        params={'round_id': session['round_id']}
    )

    if not ranges:
        st.info("No ranges defined for this round.")
        return

    range_options = [
        f"{r['distance_m']}m (face {r['face_size']}) — {r['ends_per_range']} ends"
        for r in ranges
    ]
    range_key = f"range_selector_{session_id}_{comp_end.strftime(DATE_FORMAT_DB)}"

    if range_key not in st.session_state:
        st.session_state[range_key] = 0

    selected_range_idx = st.selectbox(
        "Select Range",
        options=list(range(len(range_options))),
        format_func=lambda i: range_options[i],
        index=st.session_state[range_key],
        key=f"range_select_{session_id}_{comp_end.strftime(DATE_FORMAT_DB)}",
    )
    st.session_state[range_key] = selected_range_idx

    selected_range = ranges[selected_range_idx]
    range_id = selected_range['id']

    ends = fetch_all(
        "SELECT id, end_no FROM `end` "
        "WHERE session_id = :session_id AND round_range_id = :range_id "
        "ORDER BY end_no",
        params={'session_id': session_id, 'range_id': range_id}
    )

    if not ends:
        st.info(f"No ends recorded for range {selected_range['distance_m']}m.")
        return

    end_key = f"end_idx_{session_id}_{range_id}_{comp_end.strftime(DATE_FORMAT_DB)}"
    if end_key not in st.session_state:
        st.session_state[end_key] = 0

    current_end_idx = st.session_state[end_key]
    total_ends = len(ends)

    st.markdown("")
    st.markdown(f"#### End {current_end_idx + 1} of {total_ends}")

    current_end = ends[current_end_idx]
    arrow_vals = _render_arrow_editor(session_id, current_end['id'], current_end['end_no'], protected, comp_end)

    end_score = sum(_score_from_arrow(a) for a in arrow_vals)
    session_total = _compute_session_total(session_id)

    col_summary1, col_summary2 = st.columns(2)
    with col_summary1:
        st.metric("End Score", end_score)
    with col_summary2:
        st.metric("Running Total", session_total)

    st.markdown("")
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button(
            "◀ Previous End",
            key=f"prev_end_{session_id}_{range_id}_{comp_end.strftime(DATE_FORMAT_DB)}",
            disabled=current_end_idx == 0,
            use_container_width=True
        ):
            st.session_state[end_key] = max(0, current_end_idx - 1)
            st.rerun()

    with col_next:
        if st.button(
            "Next End ▶",
            key=f"next_end_{session_id}_{range_id}_{comp_end.strftime(DATE_FORMAT_DB)}",
            disabled=current_end_idx >= total_ends - 1,
            use_container_width=True
        ):
            st.session_state[end_key] = min(total_ends - 1, current_end_idx + 1)
            st.rerun()


# =====================================================
# MAIN PAGE FUNCTION
# =====================================================

@require_recorder
def show_recorder_approval():
    st.title("Score Approval")
    st.caption("Filter competitions, then click a session row to edit arrows and change status.")

    competitions = fetch_all("""
        SELECT id, name,
               DATE_FORMAT(start_date, '%Y-%m-%d') AS start_date,
               DATE_FORMAT(end_date, '%Y-%m-%d') AS end_date
        FROM competition
        ORDER BY start_date DESC, name
    """)

    if not competitions:
        st.info("No competitions found in the database.")
        return

    today = _today_date()

    # =====================================================
    # DAY-LEFT WARNINGS AT TOP (single paragraph)
    # Includes ending TODAY and within next DAYS_BEFORE_WARNING days.
    # =====================================================
    warning_items: List[str] = []
    for comp in competitions:
        comp_end = _parse_date(comp['end_date'])
        days_left = (comp_end - today).days

        if 0 <= days_left <= DAYS_BEFORE_WARNING:
            unconfirmed_count = fetch_one("""
                SELECT COUNT(*) as count
                FROM session s
                JOIN competition_entry ce ON ce.session_id = s.id
                WHERE ce.competition_id = :comp_id
                  AND s.status IN ('Preliminary', 'Final')
            """, params={'comp_id': comp['id']})

            if unconfirmed_count and unconfirmed_count['count'] > 0:
                when_text = "today" if days_left == 0 else f"in {days_left} day(s)"
                warning_items.append(
                    f"""**{comp['name']}** ends {when_text} on {_format_date_for_ui(comp_end)}.
                    Please approve {unconfirmed_count['count']} unconfirmed session(s) before the shooting event ends.
                    \n"""
                )

    if warning_items:
        st.warning(" ".join(warning_items), icon=":material/warning:")

    # =====================================================
    # FILTERS: ONE LINE, 3 COLUMNS
    # =====================================================
    st.markdown("#### Filters")
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        comp_status_filter = st.selectbox(
            "Competition Status",
            options=['All', 'Active', 'Ended'],
            index=0,
            help="Filter competitions by their current status"
        )

    with col_f2:
        default_start = today - datetime.timedelta(days=365)
        default_end = today + datetime.timedelta(days=180)
        date_range = st.date_input(
            "Competition Date Range",
            value=(default_start, default_end),
            help="Show competitions within this start/end range"
        )
        if isinstance(date_range, tuple) and len(date_range) == 2:
            date_range_start, date_range_end = date_range
        else:
            date_range_start, date_range_end = default_start, default_end

    all_rounds = fetch_all("SELECT DISTINCT round_name FROM round ORDER BY round_name")
    round_names = [r['round_name'] for r in all_rounds]

    with col_f3:
        selected_rounds = st.multiselect(
            "Round Filter",
            options=round_names,
            default=[],
            help="Leave empty to show all rounds"
        )

    # Apply filters to competitions
    filtered_competitions = []
    for c in competitions:
        comp_start = _parse_date(c['start_date'])
        comp_end = _parse_date(c['end_date'])

        if comp_status_filter == 'Active' and today > comp_end:
            continue
        if comp_status_filter == 'Ended' and today <= comp_end:
            continue

        if comp_end < date_range_start or comp_start > date_range_end:
            continue

        filtered_competitions.append(c)

    if not filtered_competitions:
        st.info("No competitions match the selected filters.")
        return

    selected_ids = [int(c['id']) for c in filtered_competitions]

    round_filter_sql = ""
    round_params = {}
    if selected_rounds:
        round_filter_sql = "AND r.round_name IN :round_names"
        round_params = {'round_names': tuple(selected_rounds)}

    sessions = fetch_all(f"""
        SELECT s.id AS session_id, s.member_id, s.round_id,
               DATE_FORMAT(s.shoot_date, '%Y-%m-%d') AS shoot_date,
               s.status,
               ce.competition_id,
               c.name AS competition_name,
               DATE_FORMAT(c.end_date, '%Y-%m-%d') AS comp_end_date,
               r.round_name,
               cm.full_name AS member_name,
               cm.av_number
        FROM session s
        JOIN competition_entry ce ON ce.session_id = s.id
        JOIN competition c ON c.id = ce.competition_id
        JOIN round r ON r.id = s.round_id
        JOIN club_member cm ON cm.id = s.member_id
        WHERE ce.competition_id IN :ids {round_filter_sql}
        ORDER BY c.name, s.shoot_date, cm.full_name
    """, params={'ids': tuple(selected_ids), **round_params})

    if not sessions:
        st.info("No sessions found for the selected filters.")
        return

    sessions = [dict(s) for s in sessions]
    for s in sessions:
        if not s.get('av_number'):
            s['av_number'] = f"ID{s['member_id']}"

    sessions_by_comp: Dict[int, List[Dict]] = {}
    for s in sessions:
        comp_key = int(s['competition_id'])
        sessions_by_comp.setdefault(comp_key, []).append(s)

    active_comp_ids = list(sessions_by_comp.keys())
    active_comp_ids.sort(reverse=True)

    if not active_comp_ids:
        st.info("No sessions found.")
        return

    tab_labels = []
    for cid in active_comp_ids:
        comp = next((c for c in filtered_competitions if int(c['id']) == cid), None)
        tab_labels.append(comp['name'] if comp else f"Comp {cid}")

    tabs = st.tabs(tab_labels)

    for i, comp_key in enumerate(active_comp_ids):
        with tabs[i]:
            sess_list = sessions_by_comp[comp_key]

            comp = next((c for c in filtered_competitions if int(c['id']) == comp_key), None)
            comp_name = comp['name'] if comp else f"Competition {comp_key}"
            comp_end = _parse_date(comp['end_date']) if comp else _today_date()
            comp_id = comp_key

            st.markdown(f"## {comp_name} — ends {_format_date_for_ui(comp_end)}")

            if HAS_AGGRID and sess_list:
                rows = []
                for s in sess_list:
                    total = _compute_session_total(s['session_id'])
                    rows.append({
                        'session_id': s['session_id'],
                        'av_number': s['av_number'],
                        'round': s['round_name'],
                        'shoot_date': _format_date_for_ui(_parse_date(s['shoot_date'])),
                        'status': s['status'],
                        'total': total,
                    })

                df = pd.DataFrame(rows)
                gb = GridOptionsBuilder.from_dataframe(df)  # type: ignore

                gb.configure_default_column(flex=1, min_width=100, resizable=True)
                gb.configure_selection(selection_mode='single', use_checkbox=False)
                gb.configure_grid_options(suppressCellFocus=True)

                gb.configure_column('session_id', hide=True)
                gb.configure_column('av_number', header_name='AV Number')
                gb.configure_column('round', header_name='Round')
                gb.configure_column('shoot_date', header_name='Shoot Date')
                gb.configure_column('status', header_name='Status')
                gb.configure_column('total', header_name='Total Score')

                grid_options = gb.build()
                grid_key = st.session_state.get(f"grid_reload_{comp_id}", 0)

                grid_response = AgGrid(  # type: ignore
                    df,
                    gridOptions=grid_options,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,  # type: ignore
                    allow_unsafe_jscode=True,
                    enable_enterprise_modules=False,
                    fit_columns_on_grid_load=True,
                    height=min(200 + len(rows) * 35, 500),
                    theme='balham',
                    key=f"aggrid_{comp_id}_{grid_key}"
                )

                selected_raw = grid_response.get('selected_rows', [])
                if isinstance(selected_raw, pd.DataFrame):
                    try:
                        selected = selected_raw.to_dict('records')
                    except Exception:
                        selected = []
                elif isinstance(selected_raw, list):
                    selected = selected_raw
                else:
                    try:
                        selected = list(selected_raw) if selected_raw is not None else []
                    except Exception:
                        selected = []

                session_key = f"editor_session_{comp_id}"

                if len(selected) > 0:
                    try:
                        sel_id = selected[0].get('session_id')
                        if sel_id is not None:
                            st.session_state[session_key] = int(sel_id)
                    except Exception:
                        st.session_state.pop(session_key, None)

                editor_session_id = st.session_state.get(session_key)
                if editor_session_id:
                    selected_session = next((s for s in sess_list if s['session_id'] == editor_session_id), None)
                    if selected_session:
                        st.markdown("")
                        st.markdown(
                            f"**Selected:** {selected_session.get('av_number', 'N/A')} — "
                            f"{selected_session['round_name']} "
                            f"— {_format_date_for_ui(_parse_date(selected_session['shoot_date']))} – {_format_date_for_ui(comp_end)}"
                        )

                        protected_comp = (_today_date() > comp_end)

                        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
                        with col1:
                            button_label = "View Score" if protected_comp else "Edit Score"
                            button_icon = ":material/visibility:" if protected_comp else ":material/edit:"
                            is_score_active = st.session_state.get(f"show_score_{comp_id}", False)
                            if st.button(
                                button_label,
                                key=f"btn_score_{comp_id}_{editor_session_id}",
                                icon=button_icon,
                                use_container_width=True,
                                type="primary" if is_score_active else "secondary"
                            ):
                                st.session_state[f"show_score_{comp_id}"] = True
                                st.session_state.pop(f"show_status_{comp_id}", None)
                                st.session_state.pop(f"show_bulk_{comp_id}", None)
                                st.rerun()
                        with col2:
                            is_status_active = st.session_state.get(f"show_status_{comp_id}", False)
                            if st.button(
                                "Change Status",
                                key=f"btn_status_{comp_id}_{editor_session_id}",
                                icon=":material/swap_horiz:",
                                use_container_width=True,
                                type="primary" if is_status_active else "secondary",
                                disabled=protected_comp
                            ):
                                st.session_state[f"show_status_{comp_id}"] = True
                                st.session_state.pop(f"show_score_{comp_id}", None)
                                st.session_state.pop(f"show_bulk_{comp_id}", None)
                                st.rerun()
                        with col3:
                            is_bulk_active = st.session_state.get(f"show_bulk_{comp_id}", False)
                            if st.button(
                                "Group Approve",
                                key=f"btn_bulk_{comp_id}_{editor_session_id}",
                                icon=":material/list:",
                                use_container_width=True,
                                type="primary" if is_bulk_active else "secondary",
                                disabled=protected_comp
                            ):
                                st.session_state[f"show_bulk_{comp_id}"] = True
                                st.session_state.pop(f"show_score_{comp_id}", None)
                                st.session_state.pop(f"show_status_{comp_id}", None)
                                st.rerun()
                        with col4:
                            if st.button(
                                "Clear Selection",
                                key=f"btn_clear_{comp_id}_{editor_session_id}",
                                icon=":material/clear:", 
                                use_container_width=True
                            ):
                                st.session_state.pop(session_key, None)
                                st.session_state.pop(f"show_score_{comp_id}", None)
                                st.session_state.pop(f"show_status_{comp_id}", None)
                                st.session_state.pop(f"show_bulk_{comp_id}", None)
                                current_reload = st.session_state.get(f"grid_reload_{comp_id}", 0)
                                st.session_state[f"grid_reload_{comp_id}"] = current_reload + 1
                                st.rerun()

                        if protected_comp:
                            st.info("This competition has ended — scores are view-only.", icon=":material/lock:")

                        if st.session_state.get(f"show_score_{comp_id}"):
                            _render_score_editor(selected_session, comp_end)
                        elif st.session_state.get(f"show_status_{comp_id}"):
                            _render_status_editor(selected_session, comp_end)
                        elif st.session_state.get(f"show_bulk_{comp_id}"):
                            _render_group_approve_editor(sess_list, comp_end, str(comp_id))

                        try:
                            status_msg_key = f"status_msg_{selected_session['session_id']}"
                            if status_msg_key in st.session_state:
                                st.success(st.session_state.pop(status_msg_key))
                        except Exception:
                            pass

                        bulk_key = f"bulk_results_{str(comp_id)}"
                        if bulk_key in st.session_state:
                            results = st.session_state.pop(bulk_key)
                            new_status = results["new_status"]

                            updated_from_statuses = results.get("updated_from_statuses", [])
                            if results["success_count"] > 0:
                                if len(updated_from_statuses) == 1:
                                    from_status = updated_from_statuses[0]
                                    st.success(
                                        f"Status updated from '{from_status}' to '{new_status}' "
                                        f"for {results['success_count']} session(s)."
                                    )
                                else:
                                    st.success(
                                        f"Status updated to '{new_status}' "
                                        f"for {results['success_count']} session(s)."
                                    )

                            already_target_count = results.get("already_target_count", 0)
                            if already_target_count > 0:
                                st.info(
                                    f"Status has been updated to {new_status} for {already_target_count} session(s) "
                                    f"(already {new_status})."
                                )

                            blocked_count = results.get("blocked_confirmed_to_prelim", 0)
                            if blocked_count > 0:
                                st.warning(
                                    f"Reverting to Preliminary is not allowed. "
                                    f"{blocked_count} Confirmed session(s) were skipped."
                                )

                            failed_sessions = results.get("failed_sessions", [])
                            if failed_sessions:
                                st.error(
                                    f"The following selected session(s) were NOT updated to {new_status}:"
                                )
                                err_df = pd.DataFrame([{
                                    "AV Number": f["av_number"],
                                    "Round": f["round_name"],
                                    "Shoot Date": f["shoot_date"],
                                    "Error": f["error"]
                                } for f in failed_sessions])
                                st.dataframe(err_df, use_container_width=True, hide_index=True)

            else:
                st.info("AgGrid not available or no sessions.")
                for s in sess_list:
                    st.write(f"- {s['av_number']} {s['round_name']}")
