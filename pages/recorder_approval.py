# =====================================================
# IMPORTS
# =====================================================
import datetime
from typing import List, Dict, Optional, Any

import streamlit as st
import pandas as pd
from db_core import fetch_all, exec_sql, fetch_one
from guards import require_recorder

# =====================================================
# AGGRID INTEGRATION (OPTIONAL)
# =====================================================
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
    HAS_AGGRID = True
except Exception:
    HAS_AGGRID = False
    AgGrid = GridOptionsBuilder = GridUpdateMode = None  # type: ignore


# =====================================================
# GLOBAL CONSTANTS
# =====================================================
DAYS_BEFORE_WARNING = 2
DATE_FORMAT_UI = "%d-%m-%Y"  # dd-mm-yyyy for UI display
DATE_FORMAT_DB = "%Y-%m-%d"  # yyyy-mm-dd for database/backend


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def _get_recorder_id() -> Optional[int]:
    """Get the current recorder's member ID from session state."""
    auth = st.session_state.get("auth", {})
    return auth.get("id")

def _today() -> datetime.date:
    return datetime.date.today()

def _to_date(d: Any) -> datetime.date:
    """Coerce a DB date (str / datetime / date) to datetime.date safely."""
    if isinstance(d, datetime.date) and not isinstance(d, datetime.datetime):
        return d
    if isinstance(d, datetime.datetime):
        return d.date()
    if isinstance(d, str):
        try:
            return datetime.datetime.strptime(d, DATE_FORMAT_DB).date()
        except ValueError:
            pass
    return _today()

def _fmt_date_ui(d: Any) -> str:
    """Format date for UI display."""
    return _to_date(d).strftime(DATE_FORMAT_UI)

def _parse_date_db(d: Any) -> datetime.date:
    """Parse DB string date to python date."""
    return _to_date(d)

def _compute_total_score(session_id: int) -> int:
    """Calculate total score for a session from DB."""
    res = fetch_one("""
        SELECT SUM(CASE 
            WHEN UPPER(TRIM(a.arrow_value)) = 'X' THEN 10 
            WHEN UPPER(TRIM(a.arrow_value)) = 'M' THEN 0 
            ELSE CAST(a.arrow_value AS UNSIGNED) END) as total 
        FROM arrow a 
        JOIN `end` e ON a.end_id = e.id 
        WHERE e.session_id = :sid
    """, params={'sid': session_id})
    return int(res['total']) if res and res['total'] is not None else 0

def _update_status(session_id: int, old_status: str, new_status: str):
    """Update session status and write audit log."""
    exec_sql(
        "UPDATE session SET status = :status WHERE id = :id",
        params={'status': new_status, 'id': session_id}
    )

    recorder_id = _get_recorder_id()
    try:
        exec_sql("""
            INSERT INTO session_audit (session_id, old_status, new_status, changed_by) 
            VALUES (:session_id, :old, :new, :by)
        """, params={
            'session_id': session_id,   # FIX: correct param name
            'old': old_status,
            'new': new_status,
            'by': recorder_id
        })
    except Exception:
        pass  # Audit failure shouldn't block workflow


# =====================================================
# AG GRID TABLE RENDERER
# =====================================================

def _render_session_grid(data: List[Dict], key_suffix: str) -> List[Dict]:
    """Helper to render AgGrid and return selected rows."""
    df = pd.DataFrame(data)

    if not HAS_AGGRID or df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        return []

    col_order = [
        "session_id",      # hidden
        "round_id",        # hidden
        "competition_id",  # hidden
        "av_number",
        "round_name",
        "shoot_date",
        "status",
        "total",
    ]

    # keep only existing columns, in that order
    df = df[[c for c in col_order if c in df.columns]]

    gb = GridOptionsBuilder.from_dataframe(df)  # type: ignore

    gb.configure_default_column(flex=1, min_width=100, resizable=True)
    gb.configure_selection(selection_mode='single', use_checkbox=False)
    gb.configure_grid_options(suppressCellFocus=True)

    for col in ['session_id', 'round_id', 'competition_id', 'member_id', 'full_name']:
        if col in df.columns:
            gb.configure_column(col, hide=True)

    gb.configure_column('av_number', header_name='AV Number')
    gb.configure_column('round_name', header_name='Round')
    gb.configure_column('shoot_date', header_name='Shooting Date')
    gb.configure_column('status', header_name='Status')
    gb.configure_column('total', header_name='Total Score')

    reload_key = st.session_state.get(f"grid_reload_{key_suffix}", 0)

    grid_response = AgGrid(  # type: ignore
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,  # type: ignore
        height=min(200 + len(data) * 35, 400),
        theme="balham",
        key=f"ag_{key_suffix}_{reload_key}"
    )

    selected = grid_response.get('selected_rows', [])
    if isinstance(selected, pd.DataFrame):
        return selected.to_dict('records')
    return list(selected) if selected else []


# =====================================================
# ARROW EDITOR
# =====================================================

def _render_arrow_editor(session_id: int, end_id: int, end_no: int, protected: bool):
    """Render inputs for 6 arrows in a specific end."""
    arrows = fetch_all(
        "SELECT arrow_no, arrow_value FROM arrow WHERE end_id=:eid ORDER BY arrow_no",
        params={'eid': end_id}
    )
    current_vals = [a['arrow_value'] for a in arrows]
    while len(current_vals) < 6:
        current_vals.append('M')

    st.markdown(f"**End {end_no}**")
    cols = st.columns(6)
    new_vals = []
    options = ['X', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', 'M']

    for i, col in enumerate(cols):
        val = current_vals[i]
        idx = options.index(val) if val in options else len(options) - 1
        nv = col.selectbox(
            f"Arr {i+1}",
            options,
            index=idx,
            key=f"arw_{session_id}_{end_id}_{i}",
            disabled=protected,
            label_visibility="collapsed"
        )
        new_vals.append(nv)

    if not protected and new_vals != current_vals:
        for i, nv in enumerate(new_vals):
            if i < len(arrows):
                exec_sql(
                    "UPDATE arrow SET arrow_value=:v WHERE end_id=:eid AND arrow_no=:no",
                    params={'v': nv, 'eid': end_id, 'no': i + 1}
                )
            else:
                exec_sql(
                    "INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES (:eid, :no, :v)",
                    params={'eid': end_id, 'no': i + 1, 'v': nv}
                )
    return new_vals


# =====================================================
# STATUS EDITOR
# =====================================================

def _render_status_editor(session: Dict, protected: bool):
    """Render status change UI."""
    sid = session['session_id']
    curr_status = session['status']

    st.markdown(f"### Change Status: {session.get('av_number')} - {session['round_name']}")

    if protected:
        st.warning(f"Status locked at '{curr_status}' (Competition ended).")
        return

    status_list = ['Preliminary', 'Final', 'Confirmed']
    new_status = st.selectbox(
        "New Status",
        status_list,
        index=status_list.index(curr_status) if curr_status in status_list else 0,
        key=f"stat_sel_{sid}"
    )

    if st.button("Apply Status", key=f"btn_stat_{sid}", type="primary"):
        if new_status != curr_status:
            _update_status(sid, curr_status, new_status)
        st.session_state.pop(f"show_status_{session.get('competition_id')}", None)
        st.rerun()


def _render_bulk_editor(sessions: List[Dict], protected: bool, comp_key: str):
    """Render bulk status update UI."""
    st.markdown("### Group Approve/Revert")

    c1, c2, c3 = st.columns(3)
    with c1:
        stat_filter = st.multiselect(
            "Current Status",
            ['Preliminary', 'Final', 'Confirmed'],
            default=['Preliminary'],
            key=f"bf_stat_{comp_key}"
        )
    with c2:
        rnd_filter = st.multiselect(
            "Round",
            sorted(list({s['round_name'] for s in sessions})),
            key=f"bf_rnd_{comp_key}"
        )
    with c3:
        av_filter = st.text_input("AV Number Search", key=f"bf_av_{comp_key}")

    filtered = [
        s for s in sessions
        if (not stat_filter or s['status'] in stat_filter)
        and (not rnd_filter or s['round_name'] in rnd_filter)
        and (not av_filter or av_filter.lower() in str(s.get('av_number', '')).lower())
    ]

    editable = [] if protected else [s for s in filtered if s['status'] not in ('Final', 'Confirmed')]

    st.caption(f"Found {len(filtered)} sessions. {len(editable)} editable.")

    if not editable:
        st.warning("No editable sessions match filters.")
        return

    c1, c2 = st.columns([2, 1])
    with c1:
        target_status = st.selectbox(
            "Set all to:",
            ['Preliminary', 'Final', 'Confirmed'],
            key=f"bf_target_{comp_key}"
        )
    with c2:
        st.write("")
        if st.button(
            f"Update {len(editable)} Sessions",
            type="primary",
            key=f"bf_apply_{comp_key}"
        ):
            count = 0
            for s in editable:
                if s['status'] != target_status:
                    _update_status(s['session_id'], s['status'], target_status)
                    count += 1
            st.success(f"Updated {count} sessions.")
            st.session_state.pop(f"show_bulk_{comp_key}", None)
            st.rerun()


# =====================================================
# SCORE EDITOR
# =====================================================

def _render_score_editor(session: Dict, protected: bool):
    """Render score editing interface."""
    sid = session['session_id']
    rid = session['round_id']

    view_text = " (Read Only)" if protected else ""
    st.markdown(f"### Score Editor{view_text}: {session.get('av_number')} - {session['round_name']}")

    ranges = fetch_all("""
        SELECT id, distance_m, face_size, ends_per_range
        FROM round_range
        WHERE round_id=:rid
        ORDER BY distance_m DESC
    """, params={'rid': rid})
    if not ranges:
        st.error("No ranges found.")
        return

    r_opts = [f"{r['distance_m']}m (face {r['face_size']})" for r in ranges]
    r_idx = st.selectbox(
        "Select Range",
        range(len(r_opts)),
        format_func=lambda x: r_opts[x],
        key=f"r_sel_{sid}"
    )
    sel_range = ranges[r_idx]

    ends = fetch_all("""
        SELECT id, end_no
        FROM `end`
        WHERE session_id=:sid AND round_range_id=:rrid
        ORDER BY end_no
    """, params={'sid': sid, 'rrid': sel_range['id']})

    if not ends:
        st.info("No ends recorded.")
        return

    nav_key = f"nav_{sid}_{sel_range['id']}"
    if nav_key not in st.session_state:
        st.session_state[nav_key] = 0

    curr_idx = st.session_state[nav_key]
    curr_end = ends[curr_idx]

    _render_arrow_editor(sid, curr_end['id'], curr_end['end_no'], protected)

    total = _compute_total_score(sid)
    st.metric("Running Total", total)

    c1, c2 = st.columns(2)
    if c1.button("◀ Previous End", key=f"prev_{sid}_{sel_range['id']}", disabled=curr_idx == 0):
        st.session_state[nav_key] -= 1
        st.rerun()
    if c2.button("Next End ▶", key=f"next_{sid}_{sel_range['id']}", disabled=curr_idx == len(ends) - 1):
        st.session_state[nav_key] += 1
        st.rerun()


# =====================================================
# MAIN PAGE FUNCTION
# =====================================================

@require_recorder
def show_recorder_approval():
    st.title("Score Approval")
    st.caption("Review, edit, and approve competition scores.")

    today = _today()

    # 1. Fetch competitions
    competitions = fetch_all("""
        SELECT id, name, start_date, end_date
        FROM competition
        ORDER BY start_date DESC
    """)
    if not competitions:
        st.info("No competitions found.")
        return

    # Normalize competition dates to python.date
    competitions = [dict(c) for c in competitions] # Convert to mutable dictionaries and normalize dates
    for c in competitions:
        c["start_date"] = _parse_date_db(c["start_date"])
        c["end_date"] = _parse_date_db(c["end_date"])

    # Deadline warnings
    for c in competitions:
        days_left = (c['end_date'] - today).days
        if 0 <= days_left <= DAYS_BEFORE_WARNING:
            count = fetch_one("""
                SELECT COUNT(*) as count
                FROM session s
                JOIN competition_entry ce ON ce.session_id = s.id
                WHERE ce.competition_id = :comp_id
                  AND s.status IN ('Preliminary', 'Final')
            """, params={'comp_id': c['id']})

            if count and count['count'] > 0:
                st.warning(
                    f"**{c['name']}** ends in {days_left} day(s) on {_fmt_date_ui(c['end_date'])}. "
                    f"There are {count['count']} unconfirmed session(s) that need review!",
                    icon=":material/warning:"
                )

    # 2. Filters (3 columns)
    st.markdown("#### Filter Competitions")

    all_rounds = fetch_all("SELECT DISTINCT round_name FROM round ORDER BY round_name")
    round_opts = [r['round_name'] for r in all_rounds]

    col1, col2, col3 = st.columns(3, vertical_alignment="bottom")

    with col1:
        comp_status_filter = st.selectbox(
            "Competition Status",
            ["All", "Active", "Ended"],
            index=0
        )

    with col2:
        default_start = today - datetime.timedelta(days=365)
        default_end = today + datetime.timedelta(days=180)
        date_range = st.date_input(
            "Date Range",
            value=(default_start, default_end)
        )
        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            date_start, date_end = date_range
        else:
            date_start = date_end = date_range

    with col3:
        selected_rounds = st.multiselect(
            "Rounds",
            options=round_opts,
            default=[]
        )

    # 3. Filter competitions
    filtered_competitions: List[Dict] = []
    for c in competitions:
        is_active = today <= c['end_date']
        if comp_status_filter == "Active" and not is_active:
            continue
        if comp_status_filter == "Ended" and is_active:
            continue
        if c['end_date'] < date_start or c['start_date'] > date_end:
            continue
        filtered_competitions.append(c)

    if not filtered_competitions:
        st.info("No competitions match the selected filters.")
        return

    # Auto-select ALL filtered competitions (no extra UI)
    comps_by_id = {c['id']: c for c in filtered_competitions}
    selected_ids = tuple(c['id'] for c in filtered_competitions)

    # 4. Fetch sessions
    sql = """
        SELECT s.id AS session_id, s.member_id, s.round_id, s.shoot_date, s.status,
               ce.competition_id, r.round_name, cm.av_number, cm.full_name
        FROM session s
        JOIN competition_entry ce ON ce.session_id = s.id
        JOIN round r ON r.id = s.round_id
        JOIN club_member cm ON cm.id = s.member_id
        WHERE ce.competition_id IN :ids
    """
    params = {'ids': selected_ids}

    if selected_rounds:
        sql += " AND r.round_name IN :rnames"
        params['rnames'] = tuple(selected_rounds)

    sql += " ORDER BY s.shoot_date DESC, cm.full_name"

    all_sessions = fetch_all(sql, params=params)

    if not all_sessions:
        st.info("No sessions found for the selected competitions/rounds.")
        return

    # Group sessions by comp
    grouped: Dict[int, List[Dict]] = {}
    for s in all_sessions:
        cid = s['competition_id']
        grouped.setdefault(cid, [])
        s_view = dict(s)
        s_view['shoot_date'] = _fmt_date_ui(s['shoot_date'])
        s_view['total'] = _compute_total_score(s['session_id'])
        grouped[cid].append(s_view)

    active_cids = sorted([cid for cid in selected_ids if cid in grouped], reverse=True)
    if not active_cids:
        st.info("No sessions after applying round filters.")
        return

    tabs = st.tabs([comps_by_id[cid]['name'] for cid in active_cids])

    for tab, cid in zip(tabs, active_cids):
        with tab:
            comp = comps_by_id[cid]
            is_protected = today > comp['end_date']
            session_data = grouped.get(cid, [])

            st.caption(f"Ends: {_fmt_date_ui(comp['end_date'])}")

            selected_rows = _render_session_grid(session_data, f"comp_{cid}")

            session_key = f"edit_session_{cid}"
            if selected_rows:
                st.session_state[session_key] = selected_rows[0]

            active_session = st.session_state.get(session_key)

            if active_session:
                valid_ids = {s['session_id'] for s in session_data}
                if active_session['session_id'] not in valid_ids:
                    st.session_state.pop(session_key, None)
                    active_session = None

            if active_session:
                st.divider()
                st.markdown(f"**Selected:** {active_session.get('av_number')} - {active_session['round_name']}")

                b1, b2, b3, b4 = st.columns([1, 1, 1, 2])

                with b1:
                    label = "View Score" if is_protected else "Edit Score"
                    icon = ":material/visibility:" if is_protected else ":material/edit:"
                    if st.button(label, icon=icon, key=f"btn_score_{cid}_{active_session['session_id']}"):
                        st.session_state[f"show_score_{cid}"] = True
                        st.session_state.pop(f"show_status_{cid}", None)
                        st.session_state.pop(f"show_bulk_{cid}", None)
                        st.rerun()

                with b2:
                    if st.button(
                        "Change Status",
                        icon=":material/swap_horiz:",
                        key=f"btn_status_{cid}_{active_session['session_id']}",
                        disabled=is_protected
                    ):
                        st.session_state[f"show_status_{cid}"] = True
                        st.session_state.pop(f"show_score_{cid}", None)
                        st.session_state.pop(f"show_bulk_{cid}", None)
                        st.rerun()

                with b3:
                    if st.button(
                        "Group Approve",
                        icon=":material/list:",
                        key=f"btn_bulk_{cid}_{active_session['session_id']}",
                        disabled=is_protected
                    ):
                        st.session_state[f"show_bulk_{cid}"] = True
                        st.session_state.pop(f"show_score_{cid}", None)
                        st.session_state.pop(f"show_status_{cid}", None)
                        st.rerun()

                with b4:
                    if st.button("Clear Selection", icon=":material/clear:", key=f"btn_clear_{cid}_{active_session['session_id']}"):
                        st.session_state.pop(session_key, None)
                        st.session_state.pop(f"show_score_{cid}", None)
                        st.session_state.pop(f"show_status_{cid}", None)
                        st.session_state.pop(f"show_bulk_{cid}", None)
                        st.session_state[f"grid_reload_comp_{cid}"] = st.session_state.get(f"grid_reload_comp_{cid}", 0) + 1
                        st.rerun()

                if is_protected:
                    st.info("This competition has ended — scores are view-only.", icon=":material/lock:")

                if st.session_state.get(f"show_score_{cid}"):
                    _render_score_editor(active_session, is_protected)
                elif st.session_state.get(f"show_status_{cid}"):
                    _render_status_editor(active_session, is_protected)
                elif st.session_state.get(f"show_bulk_{cid}"):
                    _render_bulk_editor(session_data, is_protected, str(cid))

"""Recorder Approval (DB-backed)

This page lists sessions entered into club competitions and lets recorders
edit arrow values (6 arrows per end), change status, and confirm sessions.
All edits persist to the archery_db via db_core.

Features implemented:
- Filter by competition to review entered sessions.
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

Note: Sessions are a database normalization concept. In the UI, they represent
an archer's score for a round shot on a specific date, which is then linked
to one or more competitions via competition_entry table.
"""