"""Recorder Approval (DB-backed)

This page lists sessions entered into club competitions / championships and
lets recorders edit arrow values (6 arrows per end), change status, and
confirm sessions. All edits persist to the archery_db via db_core.

Features implemented:
- Filter by competition (club competitions and championships) by name.
- Clickable AgGrid table showing AV number, round, shoot date, status, and total score.
- Click on a row to select it, then use action buttons:
  - "📊 Edit Score" button opens score editor with:
    - Range selection dropdown
    - End-by-end navigation (Prev/Next buttons below arrows)
    - 6-arrow editor per end
    - Running total display (end score + session total)
  - "🔄 Change Status" button opens single session status editor
  - "📋 Bulk Change" button opens bulk status change interface with:
    - Multi-filter options (status, round, AV number)
    - Preview table of affected sessions
    - Protection for locked sessions (Final/Confirmed after comp end)
    - Progress tracking and error handling
    - Confirmation checkbox for safety
  - "✖ Clear Selection" button clears the selection
- Status changes create audit trail.
- Editing protections: Final/Confirmed scores locked after competition end date.
"""

import datetime
from typing import List, Dict, Optional

import streamlit as st
import pandas as pd
from db_core import fetch_all, exec_sql, fetch_one
from sqlalchemy.exc import ProgrammingError
from guards import require_recorder

# Optional AgGrid integration for clickable tables (nice UX). If st_aggrid is
# not available we'll fall back to a simpler list-based UI.
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
    HAS_AGGRID = True
except Exception:
    HAS_AGGRID = False
    AgGrid = GridOptionsBuilder = GridUpdateMode = None


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
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return _today_date()


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
    Build a mapping from member_id to AV number by inspecting the club_member
    table for an AV-related column. Falls back to member ID if not found.
    """
    member_ids = list({s['member_id'] for s in sessions})
    member_av_map: Dict[int, str] = {}
    
    if not member_ids:
        return member_av_map
    
    try:
        # Inspect club_member columns for a likely AV column name
        cols = fetch_all(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'club_member' "
            "AND COLUMN_NAME IN ('av_number','av','av_no','member_no','membership_no')"
        )
        av_col = cols[0]['COLUMN_NAME'] if cols else None
        
        if av_col:
            # Fetch AV values using the discovered column
            rows = fetch_all(
                f"SELECT id, {av_col} AS av FROM club_member WHERE id IN :ids",
                params={'ids': tuple(member_ids)}
            )
            for r in rows:
                member_av_map[r['id']] = str(r.get('av') or r['id'])
        else:
            # Fallback to member id string
            for mid in member_ids:
                member_av_map[mid] = str(mid)
    except Exception:
        # If inspection fails, use member IDs
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


def _render_arrow_editor(session_id: int, end_id: int, end_no: int, protected: bool):
    """Render the 6-arrow editor for a single end."""
    arrows = fetch_all(
        "SELECT arrow_no, arrow_value FROM arrow WHERE end_id = :end_id ORDER BY arrow_no",
        params={'end_id': end_id}
    )
    arrow_vals = [a['arrow_value'] for a in arrows]
    
    # Ensure length 6
    while len(arrow_vals) < 6:
        arrow_vals.append('M')
    
    if protected:
        st.write(f"**End {end_no}:** {' '.join(arrow_vals)}")
        return arrow_vals
    else:
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
                    key=f"arrow_{session_id}_{end_id}_{i}"
                )
                new_vals.append(new)
        
        # Persist changes per arrow
        if new_vals != arrow_vals:
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


def _render_status_editor(session: Dict, comp_end: datetime.date):
    """Render inline status editor when Status cell is clicked."""
    session_id = session['session_id']
    status = session['status']
    today = _today_date()
    protected = (today > comp_end and status in ('Final', 'Confirmed'))
    
    st.markdown("---")
    st.markdown(f"### Change Status: {session.get('av_number', 'N/A')} — {session['round_name']}")
    
    if protected:
        st.warning(f"Status is locked at '{status}' (competition ended on {comp_end})")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            new_status = st.selectbox(
                "Select new status",
                options=['Preliminary', 'Final', 'Confirmed'],
                index=['Preliminary', 'Final', 'Confirmed'].index(status),
                key=f"status_edit_{session_id}"
            )
        with col2:
            st.write("")  # Spacing
            if st.button("Apply", key=f"apply_status_{session_id}"):
                if new_status != status:
                    _update_session_status(session_id, status, new_status)
                    st.success(f"Status updated to {new_status}")
                    st.rerun()


def _render_bulk_status_editor(sess_list: List[Dict], comp_end: datetime.date, comp_id: int):
    """
    Render bulk status change interface with filtering and preview.
    
    Args:
        sess_list: List of session dictionaries for the competition
        comp_end: Competition end date for protection logic
        comp_id: Competition ID for unique keys
    """
    st.markdown("---")
    st.markdown("### 📋 Bulk Status Change")
    st.caption("Change status for multiple sessions at once with filtering options")
    
    today = _today_date()
    
    # Filter options
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        current_status_filter = st.multiselect(
            "Filter by Current Status",
            options=['Preliminary', 'Final', 'Confirmed'],
            default=['Preliminary'],
            key=f"bulk_current_status_{comp_id}"
        )
    
    with col_filter2:
        round_filter = st.multiselect(
            "Filter by Round",
            options=sorted(list(set(s['round_name'] for s in sess_list))),
            key=f"bulk_round_{comp_id}"
        )
    
    with col_filter3:
        av_filter = st.text_input(
            "Filter by AV Number (partial match)",
            key=f"bulk_av_{comp_id}"
        )
    
    # Apply filters
    filtered_sessions = [
        s for s in sess_list
        if (not current_status_filter or s['status'] in current_status_filter)
        and (not round_filter or s['round_name'] in round_filter)
        and (not av_filter or av_filter.lower() in s.get('av_number', '').lower())
    ]
    
    # Check for protected sessions
    protected_sessions = [
        s for s in filtered_sessions
        if today > comp_end and s['status'] in ('Final', 'Confirmed')
    ]
    editable_sessions = [
        s for s in filtered_sessions
        if not (today > comp_end and s['status'] in ('Final', 'Confirmed'))
    ]
    
    # Display summary
    st.markdown("---")
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
    st.markdown("---")
    st.markdown("**📊 Preview Affected Sessions**")
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
    st.markdown("---")
    col_action1, col_action2, col_action3 = st.columns([2, 1, 2])
    
    with col_action1:
        new_bulk_status = st.selectbox(
            "Change all filtered sessions to:",
            options=['Preliminary', 'Final', 'Confirmed'],
            key=f"bulk_new_status_{comp_id}"
        )
    
    with col_action2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        confirm_bulk = st.checkbox(
            "I confirm",
            key=f"bulk_confirm_{comp_id}",
            help="Check this box to enable the Apply button"
        )
    
    with col_action3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button(
            f"✓ Apply to {len(editable_sessions)} Session(s)",
            key=f"bulk_apply_{comp_id}",
            type="primary",
            disabled=not confirm_bulk,
            use_container_width=True
        ):
            _execute_bulk_status_change(editable_sessions, new_bulk_status, comp_id)


def _execute_bulk_status_change(sessions: List[Dict], new_status: str, comp_id: int):
    """
    Execute bulk status change with progress tracking and error handling.
    
    Args:
        sessions: List of session dictionaries to update
        new_status: New status to apply ('Preliminary', 'Final', 'Confirmed')
        comp_id: Competition ID for session state management
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
    
    # Display results
    st.markdown("---")
    st.markdown("### ✅ Bulk Update Complete")
    
    col_result1, col_result2, col_result3 = st.columns(3)
    with col_result1:
        st.metric("✓ Updated", success_count)
    with col_result2:
        st.metric("⊘ Skipped", skipped_count, help="Already at target status")
    with col_result3:
        st.metric("✗ Errors", error_count)
    
    if success_count > 0:
        st.success(f"Successfully updated {success_count} session(s) to '{new_status}'")
    
    # Clear bulk editor state and rerun to refresh data
    if success_count > 0 or error_count > 0:
        st.session_state.pop(f"show_bulk_{comp_id}", None)
        st.balloons()
        st.rerun()


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
    protected = (today > comp_end and status in ('Final', 'Confirmed'))
    
    st.markdown("---")
    st.markdown(f"### Score Editor: {session.get('av_number', 'N/A')} — {session['round_name']} ({session['shoot_date']})")
    
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
    range_key = f"range_selector_{session_id}"
    
    if range_key not in st.session_state:
        st.session_state[range_key] = 0
    
    selected_range_idx = st.selectbox(
        "Select Range",
        options=list(range(len(range_options))),
        format_func=lambda i: range_options[i],
        index=st.session_state[range_key],
        key=f"range_select_{session_id}"
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
    end_key = f"end_idx_{session_id}_{range_id}"
    if end_key not in st.session_state:
        st.session_state[end_key] = 0
    
    current_end_idx = st.session_state[end_key]
    total_ends = len(ends)
    
    st.markdown(f"**Editing End {current_end_idx + 1} of {total_ends}**")
    
    # Render arrow editor for current end
    current_end = ends[current_end_idx]
    arrow_vals = _render_arrow_editor(session_id, current_end['id'], current_end['end_no'], protected)
    
    # Calculate running total for current end
    end_score = sum(_score_from_arrow(a) for a in arrow_vals)
    
    # Calculate session running total
    session_total = _compute_session_total(session_id)
    
    # Display running totals
    st.markdown(f"**End Score:** {end_score} | **Running Total:** {session_total}")
    
    # Navigation buttons below the arrows (tightened spacing)
    st.markdown("")  # Small gap
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("◀ Prev", key=f"prev_end_{session_id}_{range_id}", 
                     disabled=(current_end_idx == 0 or protected),
                     use_container_width=True):
            st.session_state[end_key] = max(0, current_end_idx - 1)
            st.rerun()
    
    with col_next:
        if st.button("Next ▶", key=f"next_end_{session_id}_{range_id}", 
                     disabled=(current_end_idx >= total_ends - 1 or protected),
                     use_container_width=True):
            st.session_state[end_key] = min(total_ends - 1, current_end_idx + 1)
            st.rerun()


@require_recorder
def show_recorder_approval():
    st.title("Score Approval")
    st.caption("Select a competition, click a session row to edit arrows and change status.")
    
    # Fetch competitions that look like club comps or championships
    competitions = fetch_all("""
        SELECT id, name, DATE_FORMAT(start_date, '%Y-%m-%d') AS start_date,
               DATE_FORMAT(end_date, '%Y-%m-%d') AS end_date
        FROM competition
        WHERE name LIKE :club OR name LIKE :champ
        ORDER BY name
    """, params={'club': '%Club%', 'champ': '%Championship%'})
    
    if not competitions:
        st.info("No club competitions or championships found in the database.")
        return
    
    comp_options = [f"{c['id']}: {c['name']}" for c in competitions]
    selected = st.multiselect(
        "Select competitions to review",
        options=comp_options,
        default=comp_options
    )
    
    if not selected:
        st.info("Select at least one competition to proceed.")
        return
    
    selected_ids = [int(s.split(":", 1)[0]) for s in selected]
    
    # Load sessions that are entered into the selected competitions
    sessions = fetch_all("""
        SELECT s.id AS session_id, s.member_id, s.round_id,
               DATE_FORMAT(s.shoot_date, '%Y-%m-%d') AS shoot_date,
               s.status, ce.competition_id, c.name AS competition_name,
               DATE_FORMAT(c.end_date, '%Y-%m-%d') AS comp_end_date,
               r.round_name
        FROM session s
        JOIN competition_entry ce ON ce.session_id = s.id
        JOIN competition c ON c.id = ce.competition_id
        JOIN round r ON r.id = s.round_id
        WHERE ce.competition_id IN :ids
        ORDER BY c.name, s.shoot_date
    """, params={'ids': tuple(selected_ids)})
    
    if not sessions:
        st.info("No sessions found for the selected competitions.")
        return
    
    # Convert RowMapping objects to dicts (SQLAlchemy returns immutable RowMapping)
    sessions = [dict(s) for s in sessions]
    
    # Build AV number map
    av_map = _build_av_number_map(sessions)
    
    # Add AV numbers to sessions
    for s in sessions:
        s['av_number'] = av_map.get(s['member_id'], str(s['member_id']))
    
    # Group by competition id
    sessions_by_comp: Dict[int, List[Dict]] = {}
    for s in sessions:
        comp_id = s['competition_id']
        sessions_by_comp.setdefault(comp_id, []).append(s)
    
    st.markdown("---")
    
    # Per-competition listing
    for comp_id, sess_list in sessions_by_comp.items():
        comp = next((c for c in competitions if c['id'] == comp_id), None)
        comp_name = comp['name'] if comp else str(comp_id)
        comp_end = _parse_date(comp['end_date']) if comp else _today_date()
        
        st.markdown(f"## {comp_name} — ends {comp_end}")
        
        if HAS_AGGRID and sess_list:
            # Build dataframe for the grid with Total Score column
            rows = []
            for s in sess_list:
                total = _compute_session_total(s['session_id'])
                rows.append({
                    'session_id': s['session_id'],
                    'av_number': s['av_number'],
                    'round': s['round_name'],
                    'shoot_date': s['shoot_date'],
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
                    st.markdown("---")
                    st.markdown(f"**Selected:** {selected_session.get('av_number', 'N/A')} — {selected_session['round_name']} ({selected_session['shoot_date']})")
                    
                    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
                    with col1:
                        if st.button("📊 Edit Score", key=f"btn_score_{comp_id}_{editor_session_id}", use_container_width=True):
                            st.session_state[f"show_score_{comp_id}"] = True
                            st.session_state.pop(f"show_status_{comp_id}", None)
                            st.session_state.pop(f"show_bulk_{comp_id}", None)
                            st.rerun()
                    with col2:
                        if st.button("🔄 Change Status", key=f"btn_status_{comp_id}_{editor_session_id}", use_container_width=True):
                            st.session_state[f"show_status_{comp_id}"] = True
                            st.session_state.pop(f"show_score_{comp_id}", None)
                            st.session_state.pop(f"show_bulk_{comp_id}", None)
                            st.rerun()
                    with col3:
                        if st.button("📋 Bulk Change", key=f"btn_bulk_{comp_id}_{editor_session_id}", use_container_width=True):
                            st.session_state[f"show_bulk_{comp_id}"] = True
                            st.session_state.pop(f"show_score_{comp_id}", None)
                            st.session_state.pop(f"show_status_{comp_id}", None)
                            st.rerun()
                    with col4:
                        if st.button("✖ Clear Selection", key=f"btn_clear_{comp_id}_{editor_session_id}"):
                            # Clear all session states related to this competition
                            st.session_state.pop(session_key, None)
                            st.session_state.pop(f"show_score_{comp_id}", None)
                            st.session_state.pop(f"show_status_{comp_id}", None)
                            st.session_state.pop(f"show_bulk_{comp_id}", None)
                            # Increment grid reload counter to force recreation with no selection
                            current_reload = st.session_state.get(f"grid_reload_{comp_id}", 0)
                            st.session_state[f"grid_reload_{comp_id}"] = current_reload + 1
                            st.rerun()
                    
                    # Render the appropriate editor based on button clicks
                    if st.session_state.get(f"show_score_{comp_id}"):
                        _render_score_editor(selected_session, comp_end)
                    elif st.session_state.get(f"show_status_{comp_id}"):
                        _render_status_editor(selected_session, comp_end)
                    elif st.session_state.get(f"show_bulk_{comp_id}"):
                        _render_bulk_status_editor(sess_list, comp_end, comp_id)
        else:
            # Fallback: simple list (no AgGrid)
            st.info("AgGrid not available. Install streamlit-aggrid for enhanced table view.")
            for s in sess_list:
                st.write(f"- {s['av_number']} — {s['round_name']} ({s['shoot_date']}) [Status: {s['status']}]")