# =====================================================
# IMPORTS
# =====================================================
import datetime
from typing import List, Dict, Optional, Any  # Added 'Any' to fix type errors

import streamlit as st
import pandas as pd
from db_core import fetch_all, exec_sql, fetch_one
from sqlalchemy.exc import ProgrammingError
from guards import require_archer

# =====================================================
# AGGRID INTEGRATION (OPTIONAL)
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
DAYS_BEFORE_WARNING = 2
DATE_FORMAT_UI = "%d-%m-%Y"
DATE_FORMAT_DB = "%Y-%m-%d"


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def _get_member_id() -> Optional[int]:
    """Get the current user's member ID from session state."""
    auth = st.session_state.get("auth", {})
    return auth.get("id")


def _today_date() -> datetime.date:
    return datetime.date.today()


def _parse_date(s: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(s, DATE_FORMAT_DB).date()
    except Exception:
        return _today_date()


def _format_date_for_ui(date: datetime.date | str) -> str:
    if isinstance(date, str):
         return date # Already formatted or string
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


def _compute_session_total(session_id: int) -> int:
    """Compute total score for a session."""
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
# ARROW EDITOR
# =====================================================

def _render_arrow_editor(session_id: int, end_id: int, end_no: int, protected: bool, comp_end: datetime.date, key_suffix: str = ""):
    """Render the 6-arrow editor for a single end.
    
    Args:
        key_suffix: A unique string (e.g., competition ID) to append to widget keys to prevent duplicates.
    """
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
                key=f"arrow_{session_id}_{end_id}_{i}_{comp_end.strftime(DATE_FORMAT_DB)}{key_suffix}",
                disabled=protected
            )
            new_vals.append(new)
    
    # Only persist changes if not protected and values changed
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
    
    return new_vals


# =====================================================
# SCORE EDITOR
# =====================================================

def _render_score_editor(session: Dict, comp_end: datetime.date, key_suffix: str = ""):
    """
    Render the score editor panel (Ranges -> Ends -> Arrows).
    
    Args:
        key_suffix: A unique string (e.g., competition ID) to append to widget keys to prevent duplicates.
    """
    session_id = session['session_id']
    status = session['status']
    today = _today_date()
    
    # -------------------------------------------------------------------------
    # PROTECTION LOGIC:
    # 1. Competition has ended (today > comp_end)
    # 2. Status is 'Final' or 'Confirmed' (only 'Preliminary' is editable by archer)
    # -------------------------------------------------------------------------
    protected = (today > comp_end) or (status in ['Final', 'Confirmed'])
    
    view_mode = " (View Only)" if protected else ""
    
    # Ensure shoot_date is a date object before formatting
    s_date = session['shoot_date']
    if isinstance(s_date, str):
        s_date = _parse_date(s_date)
        
    st.markdown(f"### Score Detail{view_mode}: {session.get('av_number', 'N/A')} — {session['round_name']} ({_format_date_for_ui(s_date)})")
    
    if today > comp_end:
        st.info("This score is locked because the Competition has ended.", icon=":material/lock:")
    elif status in ['Final', 'Confirmed']:
        st.info(f"This score is locked as its status is '{status}'.", icon=":material/lock:")

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
    
    range_key = f"range_selector_{session_id}_{comp_end.strftime(DATE_FORMAT_DB)}{key_suffix}"
    
    if range_key not in st.session_state:
        st.session_state[range_key] = 0
    
    selected_range_idx = st.selectbox(
        "Select Range",
        options=list(range(len(range_options))),
        format_func=lambda i: range_options[i],
        index=st.session_state[range_key],
        key=f"range_select_{session_id}_{comp_end.strftime(DATE_FORMAT_DB)}{key_suffix}"
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
    end_key = f"end_idx_{session_id}_{range_id}_{comp_end.strftime(DATE_FORMAT_DB)}{key_suffix}"
    if end_key not in st.session_state:
        st.session_state[end_key] = 0
    
    current_end_idx = st.session_state[end_key]
    total_ends = len(ends)
    
    st.markdown("") # Spacing
    st.markdown(f"#### End {current_end_idx + 1} of {total_ends}")
    
    # Render arrow editor for current end
    current_end = ends[current_end_idx]
    arrow_vals = _render_arrow_editor(session_id, current_end['id'], current_end['end_no'], protected, comp_end, key_suffix)
    
    # Calculate totals
    end_score = sum(_score_from_arrow(a) for a in arrow_vals)
    session_total = _compute_session_total(session_id)
    
    # Display running totals
    col_summary1, col_summary2 = st.columns(2)
    with col_summary1:
        st.metric("End Score", end_score)
    with col_summary2:
        st.metric("Total Score", session_total)
    
    # Navigation buttons
    st.markdown("")
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("◀ Previous End", key=f"prev_end_{session_id}_{range_id}{key_suffix}", 
                     disabled=current_end_idx == 0,
                     use_container_width=True):
            st.session_state[end_key] = max(0, current_end_idx - 1)
            st.rerun()
    
    with col_next:
        if st.button("Next End ▶", key=f"next_end_{session_id}_{range_id}{key_suffix}", 
                     disabled=current_end_idx >= total_ends - 1,
                     use_container_width=True):
            st.session_state[end_key] = min(total_ends - 1, current_end_idx + 1)
            st.rerun()


# ==========================================================
# MAIN PAGE FUNCTION
# ==========================================================
@require_archer
def show_score_history():
    st.title("My Scores")
    st.caption("View your score history and edit preliminary scores.")
    
    # 1. Get current member ID
    member_id = _get_member_id()
    if not member_id:
        st.error("Could not identify current user.")
        return
    
    today = _today_date()
    
    # =================================================
    # FILTERS UI (3 Columns)
    # =================================================
    # Fetch round names for filter
    all_rounds = fetch_all("SELECT DISTINCT round_name FROM round ORDER BY round_name")
    round_names = [r['round_name'] for r in all_rounds]
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        # (1) Status Filter (Session Status)
        selected_statuses = st.multiselect(
            "Status",
            options=['Preliminary', 'Final', 'Confirmed'],
            default=['Preliminary', 'Final', 'Confirmed'],
            help="Filter by score status"
        )
        
    with col_f2:
        # (2) Date Range Filter
        default_start = today - datetime.timedelta(days=365)
        default_end = today + datetime.timedelta(days=180)
        
        date_range = st.date_input(
            "Date Range",
            value=(default_start, default_end),
            help="Filter by shoot date"
        )
        
        # Handle date range logic safely
        start_date = default_start
        end_date = default_end
        
        if isinstance(date_range, (list, tuple)):
            if len(date_range) == 2:
                start_date, end_date = date_range
            elif len(date_range) == 1:
                start_date = date_range[0]
                end_date = date_range[0]
        elif isinstance(date_range, datetime.date):
            start_date = date_range
            end_date = date_range

    with col_f3:
        # (3) Round Filter
        selected_rounds = st.multiselect(
            "Rounds",
            options=round_names,
            default=[],
            help="Leave empty to show all rounds"
        )

    # =================================================
    # DATA FETCHING
    # =================================================
    
    # FIX: Explicitly type the params dict to prevent "type 'date' not assignable to 'int'" error
    params: Dict[str, Any] = {'mid': member_id}
    
    query = """
        SELECT s.id AS session_id, s.member_id, s.round_id,
               s.shoot_date,
               s.status, ce.competition_id, c.name AS competition_name,
               c.end_date AS comp_end_date,
               r.round_name, cm.full_name AS member_name, cm.av_number
        FROM session s
        JOIN competition_entry ce ON ce.session_id = s.id
        JOIN competition c ON c.id = ce.competition_id
        JOIN round r ON r.id = s.round_id
        JOIN club_member cm ON cm.id = s.member_id
        WHERE s.member_id = :mid
    """
    
    # Apply Status Filter
    if selected_statuses:
        query += " AND s.status IN :statuses"
        params['statuses'] = tuple(selected_statuses)
    else:
        st.info("Please select at least one status.")
        return

    # Apply Date Filter
    query += " AND s.shoot_date BETWEEN :start_date AND :end_date"
    params['start_date'] = start_date
    params['end_date'] = end_date
    
    # Apply Round Filter
    if selected_rounds:
        query += " AND r.round_name IN :rounds"
        params['rounds'] = tuple(selected_rounds)
        
    query += " ORDER BY c.end_date DESC, c.name, s.shoot_date"
    
    sessions_data = fetch_all(query, params=params)
    
    if not sessions_data:
        st.info("No scores found matching your filters.")
        return

    # Convert to dict list
    sessions = [dict(s) for s in sessions_data]
    
    # Group by Competition
    sessions_by_comp: Dict[int, List[Dict]] = {}
    comp_info: Dict[int, Dict] = {}
    
    for s in sessions:
        comp_key = s['competition_id']
        sessions_by_comp.setdefault(comp_key, []).append(s)
        comp_info[comp_key] = {
            'name': s['competition_name'],
            'end_date': s['comp_end_date']
        }

    # =================================================
    # RENDER TABS
    # =================================================
    
    active_comp_ids = sorted(list(sessions_by_comp.keys()), reverse=True)
    
    tab_labels = [comp_info[cid]['name'] for cid in active_comp_ids]
    tabs = st.tabs(tab_labels)

    for i, comp_key in enumerate(active_comp_ids):
        with tabs[i]:
            sess_list = sessions_by_comp[comp_key]
            c_info = comp_info[comp_key]
            
            comp_end = c_info['end_date']
            if isinstance(comp_end, str):
                comp_end = _parse_date(comp_end)
            elif not isinstance(comp_end, datetime.date):
                comp_end = _today_date()

            st.caption(f"Ends: {_format_date_for_ui(comp_end)}")
            
            if HAS_AGGRID and sess_list:
                # Prepare data for grid
                rows = []
                for s in sess_list:
                    total = _compute_session_total(s['session_id'])
                    s_date_display = s['shoot_date']
                    if not isinstance(s_date_display, str):
                         s_date_display = _format_date_for_ui(s_date_display)
                         
                    rows.append({
                        'session_id': s['session_id'],
                        'round': s['round_name'],
                        'shoot_date': s_date_display,
                        'status': s['status'],
                        'total': total,
                    })
                
                df = pd.DataFrame(rows)
                
                gb = GridOptionsBuilder.from_dataframe(df) #type: ignore
                gb.configure_default_column(flex=1, min_width=100)
                gb.configure_selection(selection_mode='single', use_checkbox=False)
                gb.configure_grid_options(suppressCellFocus=True)
                gb.configure_column('session_id', hide=True)
                gb.configure_column('round', header_name='Round')
                gb.configure_column('shoot_date', header_name='Date')
                gb.configure_column('status', header_name='Status')
                gb.configure_column('total', header_name='Score')
                
                grid_response = AgGrid( #type: ignore
                    df,
                    gridOptions=gb.build(),
                    update_mode=GridUpdateMode.SELECTION_CHANGED, #type: ignore
                    allow_unsafe_jscode=True,
                    fit_columns_on_grid_load=True,
                    height=200,
                    theme='balham',
                    key=f"aggrid_history_{comp_key}"
                )
                
                selected = grid_response.get('selected_rows', [])
                if isinstance(selected, pd.DataFrame):
                    selected = selected.to_dict('records')
                elif not isinstance(selected, list):
                     selected = list(selected) if selected is not None else []

                if selected:
                    sel_id = selected[0].get('session_id')
                    selected_session = next((s for s in sess_list if s['session_id'] == sel_id), None)
                    
                    if selected_session:
                        st.markdown("---")
                        _render_score_editor(selected_session, comp_end, key_suffix=f"_c{comp_key}")
            else:
                st.info("AgGrid not available. Please install streamlit-aggrid.")