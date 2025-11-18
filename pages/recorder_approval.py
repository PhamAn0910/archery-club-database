"""Recorder Approval (DB-backed)

This page lists sessions entered into club competitions and lets recorders 
edit arrow values (6 arrows per end), change status, and confirm sessions. 
All edits persist to the archery_db via db_core.

Features implemented:
- Filter by competition or show unassigned sessions.
- Clickable AgGrid table showing AV number, round, shoot date, status, and total score.
- Click on a row to select it, then use action buttons:
  - Edit Score: opens score editor with range selection, end navigation, and arrow editing
  - Change Status: opens single session status editor
  - Group Approve/Revert: batch status change with filtering and preview
  - Clear Selection: clears current row selection
- Status changes create audit trail.
- Editing protections: Sessions locked after competition end date.
- Shows all available competitions and all club members with their scores.
- Date display format: dd-mm-yyyy (UI), yyyy-mm-dd (database/backend).
"""

# =====================================================
# IMPORTS
# =====================================================
import datetime
from typing import List, Dict, Optional

import streamlit as st
import pandas as pd
from db_core import fetch_all, exec_sql, fetch_one
from sqlalchemy.exc import ProgrammingError
from guards import require_recorder

# =====================================================
# AGGRID INTEGRATION (OPTIONAL)
# =====================================================
# Optional AgGrid integration for clickable tables (nice UX). If st_aggrid is
# not available we'll fall back to a simpler list-based UI.
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
DATE_FORMAT_UI = "%d-%m-%Y"  # dd-mm-yyyy for UI display
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
    """Convert arrow value to numeric score.
    
    X = 10 points (inner ring of 10, used for tie-breaking but scored as 10)
    M = 0 points (miss)
    Numbers 1-10 = face value
    """
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
    """
    Build a mapping from member_id to AV number using the known av_number column.
    Falls back to member ID if data is unavailable.
    """
    member_ids = list({s['member_id'] for s in sessions})
    member_av_map: Dict[int, str] = {}
    
    if not member_ids:
        return member_av_map
    
    try:
        # Use the known av_number column directly from the schema
        rows = fetch_all(
            "SELECT id, av_number FROM club_member WHERE id IN :ids",
            params={'ids': tuple(member_ids)}
        )
        for r in rows:
            member_av_map[r['id']] = str(r['av_number'] or r['id'])
    except Exception:
        # Fallback to member IDs if query fails
        for mid in member_ids:
            member_av_map[mid] = str(mid)
    
    return member_av_map


def _compute_session_total(session_id: int) -> int:
    """Compute the total score for a session by summing all arrow scores.
    
    Uses UPPER() to handle case-insensitive comparison and CAST() for numeric conversion.
    X = 10, M = 0, numbers 1-10 = face value
    """
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
    
    # Ensure length 6
    while len(arrow_vals) < 6:
        arrow_vals.append('M')
    
    st.markdown(f"**End {end_no}**")
    cols = st.columns(6)
    new_vals: List[str] = []
    choices = ['X', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', 'M']
    
    for i in range(6):
        with cols[i]:
            cur = arrow_vals[i]
            idx = choices.index(cur) if cur in choices else len(choices)-1
            new = st.selectbox(
                f"Arrow {i+1}",
                options=choices,
                index=idx,
                key=f"arrow_{session_id}_{end_id}_{i}_{comp_end.strftime(DATE_FORMAT_DB)}",
                disabled=protected  # Disable if protected
            )
            new_vals.append(new)
    
    # Only persist changes if not protected
    if not protected and new_vals != arrow_vals:
        for i, nv in enumerate(new_vals):
            if i < len(arrows):
                exec_sql(
                    "UPDATE arrow SET arrow_value = :value WHERE end_id = :end_id AND arrow_no = :arrow_no",
                    params={'value': nv, 'end_id': end_id, 'arrow_no': i+1}
                )
            else:
                exec_sql(
                    "INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES (:end_id, :arrow_no, :value)",
                    params={'end_id': end_id, 'arrow_no': i+1, 'value': nv}
                )
    
    # Return the NEW values (what the user just selected), not the old values
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
    else:
        new_status = st.selectbox(
            "Select new status",
            options=['Preliminary', 'Final', 'Confirmed'],
            index=['Preliminary', 'Final', 'Confirmed'].index(status),
            key=f"status_edit_{session_id}"
        )
        if st.button("Apply", key=f"apply_status_{session_id}", type="primary", use_container_width=True):
            if new_status != status:
                _update_session_status(session_id, status, new_status)
                # Persist message across rerun and close the status editor UI
                st.session_state[f"status_msg_{session_id}"] = f"Status updated from '{status}' to '{new_status}'"
                comp_id = session.get('competition_id') or 'unassigned'
                st.session_state.pop(f"show_status_{comp_id}", None)
                st.rerun()
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
    
    Args:
        sess_list: List of session dictionaries for the competition
        comp_end: Competition end date for protection logic
        comp_key: Competition key (ID or 'unassigned') for unique keys
    """

    st.markdown("### Group Approve/Revert")
    st.caption("Change status for multiple sessions at once with filtering options")
    
    today = _today_date()
    
    # Filter options
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
    
    # Apply filters
    filtered_sessions = [
        s for s in sess_list
        if (not current_status_filter or s['status'] in current_status_filter)
        and (not round_filter or s['round_name'] in round_filter)
        and (not av_filter or av_filter.lower() in s.get('av_number', '').lower())
    ]
    
    # Check for protected sessions
    if today > comp_end:
        protected_sessions = list(filtered_sessions)
        editable_sessions = []
    else:
        editable_sessions = [s for s in filtered_sessions if s['status'] != ('Final', 'Confirmed')]
        protected_sessions = [s for s in filtered_sessions if s['status'] == ('Final', 'Confirmed')]
    
    # Display summary
    st.markdown("") # Spacing
    col_summary1, col_summary2, col_summary3 = st.columns(3)
    with col_summary1:
        st.metric("Total Filtered", len(filtered_sessions))
    with col_summary2:
        st.metric("Editable", len(editable_sessions), delta=None if not protected_sessions else f"-{len(protected_sessions)} locked")
    with col_summary3:
        st.metric("Protected", len(protected_sessions), help="Sessions locked after competition end date")
    
    if not filtered_sessions:
        st.info("No sessions match the current filters.")
        return
    
    if not editable_sessions:
        st.warning("All filtered sessions are protected (locked after competition end date).")
        return
    
    # Preview table
    st.markdown("") # Spacing
    st.markdown("")
    st.markdown("##### :material/view_list: Preview Affected Sessions")
    preview_data = []
    for s in editable_sessions:
        preview_data.append({
            'AV Number': s.get('av_number', 'N/A'),
            'Round': s['round_name'],
            'Shoot Date': s['shoot_date'],
            'Current Status': s['status']
        })
    
    df_preview = pd.DataFrame(preview_data)
    st.dataframe(df_preview, use_container_width=True, hide_index=True)
    
    # Status change controls
    st.markdown("") # Spacing
    col_action1, col_action2, col_action3 = st.columns([2, 1, 2])
    
    with col_action1:
        new_bulk_status = st.selectbox(
            "Change all filtered sessions to:",
            options=['Preliminary', 'Final', 'Confirmed'],
            key=f"bulk_new_status_{comp_key}"
        )
    
    with col_action2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        confirm_bulk = st.checkbox(
            "I confirm",
            key=f"bulk_confirm_{comp_key}",
            help="Check this box to enable the Apply button"
        )
    
    with col_action3:
        st.write("")  # Spacing
        st.write("")  # Spacing
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
    Execute group approve/revert status change with progress tracking and error handling.
    
    Args:
        sessions: List of session dictionaries to update
        new_status: New status to apply ('Preliminary', 'Final', 'Confirmed')
        comp_key: Competition key for session state management
    """
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, session in enumerate(sessions):
        try:
            old_status = session['status']
            
            # Skip if status is already the target status
            if old_status == new_status:
                skipped_count += 1
                continue
            
            # Update status
            _update_session_status(session['session_id'], old_status, new_status)
            success_count += 1
            
        except Exception as e:
            error_count += 1
            st.error(f"Failed to update session {session.get('av_number', 'N/A')}: {str(e)}")
        
        # Update progress
        progress = (idx + 1) / len(sessions)
        progress_bar.progress(progress)
        status_text.text(f"Processing: {idx + 1}/{len(sessions)}")
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    # Store results in session state to display after rerun (outside column context)
    st.session_state[f'bulk_results_{comp_key}'] = {
        'success_count': success_count,
        'skipped_count': skipped_count,
        'error_count': error_count,
        'new_status': new_status
    }
    
    # Clear group approve editor state and rerun to refresh data
    if success_count > 0 or error_count > 0:
        st.session_state.pop(f"show_bulk_{comp_key}", None)
        st.balloons()
        st.rerun()


# =====================================================
# SCORE EDITOR
# =====================================================


def _render_score_editor(session: Dict, comp_end: datetime.date):
    """
    Render the score editor panel when Total Score cell is clicked. Shows:
    - Range selector dropdown
    - Current end with arrows editor
    - Running total display
    - Prev/Next navigation below the arrows
    """
    session_id = session['session_id']
    status = session['status']
    today = _today_date()
    protected = (today > comp_end)  # Protect if competition has ended
    
    view_mode = " (View Only)" if protected else ""
    st.markdown(f"### Score Editor{view_mode}: {session.get('av_number', 'N/A')} — {session['round_name']} ({_format_date_for_ui(_parse_date(session['shoot_date']))})")
    
    # Fetch ranges for this round
    ranges = fetch_all(
        "SELECT id, distance_m, face_size, ends_per_range FROM round_range "
        "WHERE round_id = :round_id ORDER BY distance_m DESC",
        params={'round_id': session['round_id']}
    )
    
    if not ranges:
        st.info("No ranges defined for this round.")
        return
    
    # Range selector
    range_options = [f"{r['distance_m']}m (face {r['face_size']}) — {r['ends_per_range']} ends" for r in ranges]
    range_key = f"range_selector_{session_id}_{comp_end.strftime(DATE_FORMAT_DB)}"  # Make unique per session and comp
    
    if range_key not in st.session_state:
        st.session_state[range_key] = 0
    
    selected_range_idx = st.selectbox(
        "Select Range",
        options=list(range(len(range_options))),
        format_func=lambda i: range_options[i],
        index=st.session_state[range_key],
        key=f"range_select_{session_id}_{comp_end.strftime(DATE_FORMAT_DB)}",  # Make unique
        # disabled=protected  # Disable if protected
    )
    st.session_state[range_key] = selected_range_idx
    
    selected_range = ranges[selected_range_idx]
    range_id = selected_range['id']
    
    # Fetch all ends for this range
    ends = fetch_all(
        "SELECT id, end_no FROM `end` WHERE session_id = :session_id AND round_range_id = :range_id ORDER BY end_no",
        params={'session_id': session_id, 'range_id': range_id}
    )
    
    if not ends:
        st.info(f"No ends recorded for range {selected_range['distance_m']}m.")
        return
    
    # End navigator
    end_key = f"end_idx_{session_id}_{range_id}_{comp_end.strftime(DATE_FORMAT_DB)}"  # Make unique
    if end_key not in st.session_state:
        st.session_state[end_key] = 0
    
    current_end_idx = st.session_state[end_key]
    total_ends = len(ends)
    
    st.markdown("") # Spacing
    st.markdown(f"#### Editing End {current_end_idx + 1} of {total_ends}")
    
    # Render arrow editor for current end
    current_end = ends[current_end_idx]
    arrow_vals = _render_arrow_editor(session_id, current_end['id'], current_end['end_no'], protected, comp_end)
    
    # Calculate running total for current end
    end_score = sum(_score_from_arrow(a) for a in arrow_vals)
    
    # Calculate session running total
    session_total = _compute_session_total(session_id)
    
    # Display running totals
    col_summary1, col_summary2 = st.columns(2)
    with col_summary1:
        st.metric("End Score", end_score)
    with col_summary2:
        st.metric("Running Total", session_total)
    
    # Navigation buttons below the arrows (tightened spacing)
    st.markdown("")  # Small gap
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("◀ Previous End", key=f"prev_end_{session_id}_{range_id}_{comp_end.strftime(DATE_FORMAT_DB)}", 
                     disabled=current_end_idx == 0,
                     use_container_width=True):
            st.session_state[end_key] = max(0, current_end_idx - 1)
            st.rerun()
    
    with col_next:
        if st.button("Next End ▶", key=f"next_end_{session_id}_{range_id}_{comp_end.strftime(DATE_FORMAT_DB)}", 
                     disabled=current_end_idx >= total_ends - 1,
                     use_container_width=True):
            st.session_state[end_key] = min(total_ends - 1, current_end_idx + 1)
            st.rerun()

# =====================================================
# MAIN PAGE FUNCTION
# =====================================================

@require_recorder
def show_recorder_approval():
    st.title("Score Approval")
    st.caption("Select a competition, click a session row to edit arrows and change status.")
    
    # Note: transient action messages (status/bulk results) are now shown inline
    # next to the editor controls that triggered them so they appear beneath
    # the calling UI rather than at the very top of the page.
    
    # Fetch ALL competitions, sorted by start date (most recent first)
    competitions = fetch_all("""
        SELECT id, name, DATE_FORMAT(start_date, '%Y-%m-%d') AS start_date,
               DATE_FORMAT(end_date, '%Y-%m-%d') AS end_date
        FROM competition
        ORDER BY start_date DESC, name
    """)
    
    if not competitions:
        st.info("No competitions found in the database.")
        return
    
    # Check for upcoming competition deadlines (Preliminary/Final sessions)
    today = _today_date()
    for comp in competitions:
        comp_end = _parse_date(comp['end_date'])
        days_left = (comp_end - today).days
        
        if 0 < days_left <= DAYS_BEFORE_WARNING:
            # Count unconfirmed sessions for this competition
            unconfirmed_count = fetch_one("""
                SELECT COUNT(*) as count
                FROM session s
                JOIN competition_entry ce ON ce.session_id = s.id
                WHERE ce.competition_id = :comp_id AND s.status IN ('Preliminary', 'Final')
            """, params={'comp_id': comp['id']})
            
            if unconfirmed_count and unconfirmed_count['count'] > 0:
                st.warning(
                    f"**{comp['name']}** ends in {days_left} day(s) on {_format_date_for_ui(comp_end)}. "
                    f"There are {unconfirmed_count['count']} unconfirmed session(s) that need review!",
                    icon=":material/warning:"
                )
    
    # Check for upcoming unassigned session deadlines (Preliminary/Final sessions)
    # Excludes sessions ending today (only warns for sessions ending 1-2 days from now)
    unassigned_sessions_ending_soon = fetch_all("""
        SELECT s.id, s.shoot_date, r.round_name
        FROM session s
        JOIN round r ON r.id = s.round_id
        WHERE s.id NOT IN (SELECT session_id FROM competition_entry)
          AND s.status IN ('Preliminary', 'Final')
          AND s.shoot_date > :today
          AND s.shoot_date <= :warning_date
        ORDER BY s.shoot_date ASC
    """, params={
        'today': today.strftime(DATE_FORMAT_DB),
        'warning_date': (today + datetime.timedelta(days=DAYS_BEFORE_WARNING)).strftime(DATE_FORMAT_DB)
    })
    
    if unassigned_sessions_ending_soon:
        session_list = ", ".join([
            f"{s['round_name']} on {_format_date_for_ui(_parse_date(s['shoot_date']))}"
            for s in unassigned_sessions_ending_soon
        ])
        days_until = (min([_parse_date(s['shoot_date']) for s in unassigned_sessions_ending_soon]) - today).days
        st.warning(
            f"⚠ **Unassigned sessions** ending in {days_until}-{DAYS_BEFORE_WARNING} day(s) with status Preliminary/Final: {session_list}"
        )
    
    # Competition filters
    st.markdown("#### Filter Competitions")
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        # Status filter (all/active/ended)
        comp_status_filter = st.selectbox(
            "Competition Status",
            options=['All', 'Active', 'Ended'],
            index=0,
            help="Filter competitions by their current status"
        )
    
    with col_filter2:
        # Date range filter
        default_start = today - datetime.timedelta(days=365)  # 1 year ago
        default_end = today + datetime.timedelta(days=180)    # 6 months ahead
        
        date_range_start = st.date_input(
            "From Date",
            value=default_start,
            help="Show competitions starting from this date"
        )
        
    with col_filter3:
        date_range_end = st.date_input(
            "To Date",
            value=default_end,
            help="Show competitions ending before this date"
        )
    
    # Apply filters to competitions
    filtered_competitions = []
    for c in competitions:
        comp_start = _parse_date(c['start_date'])
        comp_end = _parse_date(c['end_date'])
        
        # Apply status filter
        if comp_status_filter == 'Active' and today > comp_end:
            continue
        if comp_status_filter == 'Ended' and today <= comp_end:
            continue
        
        # Apply date range filter
        if comp_end < date_range_start or comp_start > date_range_end:
            continue
        
        filtered_competitions.append(c)
    
    if not filtered_competitions:
        st.info("No competitions match the selected filters.")
        return
    
    # comp_options = [f"{c['id']}: {c['name']} ({_format_date_for_ui(_parse_date(c['start_date']))} - {_format_date_for_ui(_parse_date(c['end_date']))})" for c in filtered_competitions]
    comp_options = [f"{c['id']}: {c['name']}" for c in filtered_competitions]
    selected = st.multiselect(
        "Select competitions to review",
        options=comp_options,
        default=comp_options
    )
    
    # Round filter
    all_rounds = fetch_all("SELECT DISTINCT round_name FROM round ORDER BY round_name")
    round_names = [r['round_name'] for r in all_rounds]
    
    selected_rounds = st.multiselect(
        "Filter by Round (optional)",
        options=round_names,
        default=[],
        help="Leave empty to show all rounds"
    )
    
    # Option to show sessions not yet entered into competitions
    show_unassigned = st.checkbox(
        "Also show sessions not yet entered into any competition", 
        value=False,
        help="Show all sessions that haven't been linked to any competition yet"
    )
    
    if not selected and not show_unassigned:
        st.info("Select at least one competition or check 'Show unassigned sessions' to proceed.")
        return
    
    # Fetch sessions based on selection
    sessions = []
    
    if selected:
        selected_ids = [int(s.split(":", 1)[0]) for s in selected]
        
        # Build round filter condition
        round_filter_sql = ""
        round_params = {}
        if selected_rounds:
            round_filter_sql = "AND r.round_name IN :round_names"
            round_params = {'round_names': tuple(selected_rounds)}
        
        # Load sessions that are entered into the selected competitions
        comp_sessions = fetch_all(f"""
            SELECT s.id AS session_id, s.member_id, s.round_id,
                   DATE_FORMAT(s.shoot_date, '%Y-%m-%d') AS shoot_date,
                   s.status, ce.competition_id, c.name AS competition_name,
                   DATE_FORMAT(c.end_date, '%Y-%m-%d') AS comp_end_date,
                   r.round_name, cm.full_name AS member_name, cm.av_number
            FROM session s
            JOIN competition_entry ce ON ce.session_id = s.id
            JOIN competition c ON c.id = ce.competition_id
            JOIN round r ON r.id = s.round_id
            JOIN club_member cm ON cm.id = s.member_id
            WHERE ce.competition_id IN :ids {round_filter_sql}
            ORDER BY c.name, s.shoot_date, cm.full_name
        """, params={'ids': tuple(selected_ids), **round_params})
        sessions.extend(comp_sessions)
    
    if show_unassigned:
        # Build round filter condition for unassigned
        round_filter_sql = ""
        round_params = {}
        if selected_rounds:
            round_filter_sql = "AND r.round_name IN :round_names"
            round_params = {'round_names': tuple(selected_rounds)}
        
        # Load sessions that are NOT entered into any competition
        # Sort by shoot_date ASC so sessions that end first come first
        unassigned_sessions = fetch_all(f"""
            SELECT s.id AS session_id, s.member_id, s.round_id,
                   DATE_FORMAT(s.shoot_date, '%Y-%m-%d') AS shoot_date,
                   s.status, NULL AS competition_id, 'Unassigned' AS competition_name,
                   NULL AS comp_end_date,
                   r.round_name, cm.full_name AS member_name, cm.av_number
            FROM session s
            JOIN round r ON r.id = s.round_id
            JOIN club_member cm ON cm.id = s.member_id
            LEFT JOIN competition_entry ce ON ce.session_id = s.id
            WHERE ce.session_id IS NULL {round_filter_sql}
            ORDER BY s.shoot_date ASC, cm.full_name
        """, params=round_params)
        sessions.extend(unassigned_sessions)
    
    if not sessions:
        st.info("No sessions found for the selected competitions.")
        return
    
    # Convert RowMapping objects to dicts and ensure AV numbers are properly set
    sessions = [dict(s) for s in sessions]
    
    # Ensure AV numbers are properly formatted (fallback to member ID if null)
    for s in sessions:
        if not s.get('av_number'):
            s['av_number'] = f"ID{s['member_id']}"
    
    # Group by competition id (unassigned sessions get grouped separately)
    sessions_by_comp: Dict[str, List[Dict]] = {}
    for s in sessions:
        comp_key = s['competition_id'] if s['competition_id'] is not None else 'unassigned'
        sessions_by_comp.setdefault(comp_key, []).append(s)
    
    # Per-competition listing
    for comp_key, sess_list in sessions_by_comp.items():
        if comp_key == 'unassigned':
            comp_name = "⋮≡ Unassigned Sessions"
            comp_end = _today_date()
            comp_id = 'unassigned'
        else:
            comp = next((c for c in filtered_competitions if c['id'] == comp_key), None)
            comp_name = comp['name'] if comp else str(comp_key)
            comp_end = _parse_date(comp['end_date']) if comp else _today_date()
            comp_id = comp_key
        
        st.markdown("---") # Separator between competitions
        st.markdown(f"## {comp_name} — ends {_format_date_for_ui(comp_end)}")
        
        if HAS_AGGRID and sess_list:
            # Build dataframe for the grid with Total Score column
            rows = []
            for s in sess_list:
                total = _compute_session_total(s['session_id'])
                rows.append({
                    'session_id': s['session_id'],
                    'av_number': s['av_number'],
                    'round': s['round_name'],
                    'shoot_date': _format_date_for_ui(_parse_date(s['shoot_date'])),  # Format for UI
                    'status': s['status'],
                    'total': total,
                })
            
            df = pd.DataFrame(rows)
            
            gb = GridOptionsBuilder.from_dataframe(df)  # type: ignore
            # Enable row selection
            gb.configure_selection(selection_mode='single', use_checkbox=False)
            # Suppress cell focus to avoid confusing red border on clicked cells
            gb.configure_grid_options(suppressCellFocus=True)
            gb.configure_column('session_id', hide=True)
            gb.configure_column('av_number', header_name='AV Number', width=100)
            gb.configure_column('round', header_name='Round', width=150)
            gb.configure_column('shoot_date', header_name='Shoot Date', width=120)
            gb.configure_column('status', header_name='Status', width=120)
            gb.configure_column('total', header_name='Total Score', width=120)
            
            grid_options = gb.build()
            
            # Use a dynamic key to force grid refresh when selection is cleared
            grid_key = st.session_state.get(f"grid_reload_{comp_id}", 0)
            
            grid_response = AgGrid(  # type: ignore
                df,
                gridOptions=grid_options,
                update_mode=GridUpdateMode.SELECTION_CHANGED,  # type: ignore
                allow_unsafe_jscode=True,
                enable_enterprise_modules=False,
                fit_columns_on_grid_load=True,
                height=min(200 + len(rows) * 35, 500),
                theme='balham',  # Use balham theme for consistent light appearance
                key=f"aggrid_{comp_id}_{grid_key}"
            )
            
            # Get selected rows
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
            
            # Session state keys for tracking what editor is open
            session_key = f"editor_session_{comp_id}"
            
            # If a row is selected, store the session and show action buttons
            if len(selected) > 0:
                try:
                    sel_id = selected[0].get('session_id')
                    if sel_id is not None:
                        st.session_state[session_key] = int(sel_id)
                except Exception:
                    st.session_state.pop(session_key, None)
            
            # If we have a selected session, show action buttons
            editor_session_id = st.session_state.get(session_key)
            if editor_session_id:
                selected_session = next((s for s in sess_list if s['session_id'] == editor_session_id), None)
                if selected_session:
                    st.markdown("") # small gap
                    st.markdown(f"**Selected:** {selected_session.get('av_number', 'N/A')} — {selected_session['round_name']} ({_format_date_for_ui(_parse_date(selected_session['shoot_date']))})")
                    
                    # Determine competition-level protection once per competition.
                    # If comp_end is in the past, disable editing actions for all sessions in this competition.
                    protected_comp = (_today_date() > comp_end)

                    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
                    with col1:
                        # View/Edit Score button (view-only if protected)
                        button_label = "View Score" if protected_comp else "Edit Score"
                        button_icon = ":material/visibility:" if protected_comp else ":material/edit:"
                        if st.button(button_label, key=f"btn_score_{comp_id}_{editor_session_id}", icon=button_icon, use_container_width=True):
                            st.session_state[f"show_score_{comp_id}"] = True
                            st.session_state.pop(f"show_status_{comp_id}", None)
                            st.session_state.pop(f"show_bulk_{comp_id}", None)
                            st.rerun()
                    with col2:
                        if st.button("Change Status", key=f"btn_status_{comp_id}_{editor_session_id}", icon=":material/swap_horiz:", use_container_width=True, disabled=protected_comp):
                            st.session_state[f"show_status_{comp_id}"] = True
                            st.session_state.pop(f"show_score_{comp_id}", None)
                            st.session_state.pop(f"show_bulk_{comp_id}", None)
                            st.rerun()
                    with col3:
                        if st.button("Group Approve/Revert", key=f"btn_bulk_{comp_id}_{editor_session_id}", icon=":material/list:", use_container_width=True, disabled=protected_comp):
                            st.session_state[f"show_bulk_{comp_id}"] = True
                            st.session_state.pop(f"show_score_{comp_id}", None)
                            st.session_state.pop(f"show_status_{comp_id}", None)
                            st.rerun()
                    with col4:
                        if st.button("Clear Selection", key=f"btn_clear_{comp_id}_{editor_session_id}", icon=":material/clear:"):
                            # Clear all session states related to this competition
                            st.session_state.pop(session_key, None)
                            st.session_state.pop(f"show_score_{comp_id}", None)
                            st.session_state.pop(f"show_status_{comp_id}", None)
                            st.session_state.pop(f"show_bulk_{comp_id}", None)
                            # Increment grid reload counter to force recreation with no selection
                            current_reload = st.session_state.get(f"grid_reload_{comp_id}", 0)
                            st.session_state[f"grid_reload_{comp_id}"] = current_reload + 1
                            st.rerun()
                    
                    if protected_comp:
                        st.info("This competition has ended — scores are view-only, status changes are disabled.", icon=":material/lock:")

                    # Render the appropriate editor based on button clicks
                    if st.session_state.get(f"show_score_{comp_id}"):
                        _render_score_editor(selected_session, comp_end)
                    elif st.session_state.get(f"show_status_{comp_id}"):
                        _render_status_editor(selected_session, comp_end)
                    elif st.session_state.get(f"show_bulk_{comp_id}"):
                        _render_group_approve_editor(sess_list, comp_end, str(comp_id))

                    st.markdown("") #small gap
                    st.markdown("")
                    # --- Inline transient messages (appear under the calling UI) ---
                    # Show any status update message for this particular session
                    try:
                        status_msg_key = f"status_msg_{selected_session['session_id']}"
                        if status_msg_key in st.session_state:
                            st.success(st.session_state.pop(status_msg_key))
                    except Exception:
                        # Defensive: if selected_session missing or key malformed, ignore
                        pass

                    # Show any bulk-results produced for this competition (if present)
                    bulk_key = f"bulk_results_{str(comp_id)}"
                    if bulk_key in st.session_state:
                        results = st.session_state.pop(bulk_key)
                        st.markdown("") # small gap
                        st.markdown("##### Completed Status Updates")
                        col_result1, col_result2, col_result3 = st.columns(3)
                        with col_result1:
                            st.metric(":material/done_all: Updated", results['success_count'],
                                     help=f"Changed to '{results['new_status']}'")
                        with col_result2:
                            st.metric(":material/rule: Skipped", results['skipped_count'],
                                     help="Already at target status")
                        with col_result3:
                            st.metric(":material/report: Errors", results['error_count'],
                                     help="Failed updates")
                        if results['success_count'] > 0:
                            st.success(f"Successfully updated {results['success_count']} session(s) to '{results['new_status']}'")
                        st.markdown("---")  # Separator
        else:
            # Fallback: simple list (no AgGrid)
            st.info("AgGrid not available. Install streamlit-aggrid for enhanced table view.")
            for s in sess_list:
                formatted_date = _format_date_for_ui(_parse_date(s['shoot_date']))
                st.write(f"- {s['av_number']} — {s['round_name']} ({formatted_date}) [Status: {s['status']}]")

