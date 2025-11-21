from __future__ import annotations
import datetime
import pandas as pd
import streamlit as st
from guards import require_archer
from db_core import fetch_all, fetch_one, exec_sql

# ==========================================================
# CONSTANTS & CONFIG
# ==========================================================
DATE_FORMAT_UI = "%d-%m-%Y"
DATE_FORMAT_DB = "%Y-%m-%d"
ARROW_VALUES = ['X', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', 'M']

try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
    HAS_AGGRID = True
except ImportError:
    HAS_AGGRID = False

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def _get_member_context():
    """Retrieve logged-in archer's details."""
    auth = st.session_state.get("auth", {})
    if not auth.get("id"):
        return None
    
    sql = """
        SELECT id, full_name, av_number, birth_year, gender_id, division_id
        FROM club_member WHERE id = :mid
    """
    return fetch_one(sql, {"mid": auth["id"]})

def _calculate_age_class(birth_year):
    """Determine Age Class code based on birth year and current policy year."""
    current_year = 2025
    policies = fetch_all("SELECT age_class_code, min_birth_year, max_birth_year FROM age_class WHERE policy_year = :year", {"year": current_year})
    
    # Convert RowMapping to list to allow sorting
    policies_list = [dict(p) for p in policies]
    # Prioritize specific classes (smallest range) over 'Open'
    policies_list.sort(key=lambda x: x['max_birth_year'] - x['min_birth_year'])

    for p in policies_list:
        if p['min_birth_year'] <= birth_year <= p['max_birth_year']:
            return p['age_class_code']
    return "Open"

def _get_category_string(age_class_code, gender_id, division_code):
    g_code = fetch_one("SELECT gender_code FROM gender WHERE id = :gid", {"gid": gender_id})
    g_str = "Male" if g_code and g_code['gender_code'] == 'M' else "Female"
    
    div_map = {'R': 'Recurve', 'C': 'Compound', 'L': 'Longbow', 'RB': 'Recurve Barebow', 'CB': 'Compound Barebow'}
    d_str = div_map.get(division_code, division_code)
    
    return f"{age_class_code} {g_str} {d_str}"

def _score_from_val(val):
    if val == 'X': return 10
    if val == 'M': return 0
    if not val: return 0
    try:
        return int(val)
    except:
        return 0

def _ensure_db_structure(session_id, range_id, ends_count):
    """Ensure ends exist in DB for the session (creates structure if missing)."""
    existing = fetch_all("SELECT end_no FROM `end` WHERE session_id=:sid AND round_range_id=:rid", 
                         {"sid": session_id, "rid": range_id})
    existing_ends = {e['end_no'] for e in existing}
    
    for i in range(1, ends_count + 1):
        if i not in existing_ends:
            exec_sql("INSERT INTO `end` (session_id, round_range_id, end_no) VALUES (:sid, :rid, :no)",
                     {"sid": session_id, "rid": range_id, "no": i})
            
    # Ensure arrows exist (placeholder 'M')
    all_ends = fetch_all("SELECT id FROM `end` WHERE session_id=:sid AND round_range_id=:rid", 
                         {"sid": session_id, "rid": range_id})
    
    for end_rec in all_ends:
        arrow_count = fetch_one("SELECT COUNT(*) as cnt FROM arrow WHERE end_id=:eid", {"eid": end_rec['id']})
        if arrow_count['cnt'] < 6: #type: ignore
            curr = fetch_all("SELECT arrow_no FROM arrow WHERE end_id=:eid", {"eid": end_rec['id']})
            exist_nos = {a['arrow_no'] for a in curr}
            for ano in range(1, 7):
                if ano not in exist_nos:
                    exec_sql("INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES (:eid, :ano, 'M')",
                             {"eid": end_rec['id'], "ano": ano})

def _get_arrows_from_buffer_or_db(session_id, range_id, end_no, total_ends):
    """Get arrows from Session State Buffer. If not in buffer, load from DB."""
    state_key = f"buffer_{session_id}_{range_id}"
    
    # Initialize buffer for this range if missing
    if state_key not in st.session_state:
        st.session_state[state_key] = {}
        # Load all ends for this range from DB
        db_data = fetch_all("""
            SELECT e.end_no, a.arrow_no, a.arrow_value 
            FROM `end` e JOIN arrow a ON a.end_id = e.id
            WHERE e.session_id = :sid AND e.round_range_id = :rid
        """, {"sid": session_id, "rid": range_id})
        
        # Populate buffer
        for i in range(1, total_ends + 1):
            # Default to 'M'
            st.session_state[state_key][i] = ['M'] * 6
            
        for row in db_data:
            e_no = row['end_no']
            a_idx = row['arrow_no'] - 1
            if e_no in st.session_state[state_key] and 0 <= a_idx < 6:
                st.session_state[state_key][e_no][a_idx] = row['arrow_value']

    return st.session_state[state_key].get(end_no, ['M']*6)

def _update_buffer(session_id, range_id, end_no, arrow_idx, val):
    """Update the session state buffer (UI only)."""
    state_key = f"buffer_{session_id}_{range_id}"
    if state_key in st.session_state:
        st.session_state[state_key][end_no][arrow_idx] = val

def _calculate_running_total_from_buffer(session_id, range_id):
    """Calculate sum of arrows currently in buffer for this range."""
    state_key = f"buffer_{session_id}_{range_id}"
    total = 0
    if state_key in st.session_state:
        for end_arrows in st.session_state[state_key].values():
            total += sum(_score_from_val(v) for v in end_arrows)
    return total

def _commit_buffer_to_db(session_id, range_id):
    """Save buffered arrows to database (On Submit)."""
    state_key = f"buffer_{session_id}_{range_id}"
    if state_key not in st.session_state:
        return

    for end_no, arrows in st.session_state[state_key].items():
        # Get End ID
        end_rec = fetch_one("SELECT id FROM `end` WHERE session_id=:sid AND round_range_id=:rid AND end_no=:no",
                            {"sid": session_id, "rid": range_id, "no": end_no})
        if end_rec:
            eid = end_rec['id']
            for i, val in enumerate(arrows):
                ano = i + 1
                # Check/Update
                exists = fetch_one("SELECT id FROM arrow WHERE end_id=:eid AND arrow_no=:ano", {"eid": eid, "ano": ano})
                if exists:
                    exec_sql("UPDATE arrow SET arrow_value=:val WHERE id=:aid", {"val": val, "aid": exists['id']})
                else:
                    exec_sql("INSERT INTO arrow (end_id, arrow_no, arrow_value) VALUES (:eid, :ano, :val)",
                             {"eid": eid, "ano": ano, "val": val})

# ==========================================================
# MAIN PAGE
# ==========================================================

@require_archer
def show_score_entry():
    st.title("🎯 Enter New Scores")
    
    member = _get_member_context()
    if not member:
        st.error("Member profile not found. Please contact support.")
        return

    # ------------------------------------------------------
    # 1. FILTERS
    # ------------------------------------------------------
    with st.container():
        c1, c2, c3 = st.columns([2, 2, 2])
        
        with c1:
            today = datetime.date.today()
            # Fix tuple handling for date_input
            d_input = st.date_input("Filter by Date", value=[today - datetime.timedelta(days=30), today + datetime.timedelta(days=60)])
            
            if isinstance(d_input, (list, tuple)):
                if len(d_input) == 2:
                    start_date, end_date = d_input
                elif len(d_input) == 1:
                    start_date = end_date = d_input[0]
                else:
                    start_date, end_date = today, today
            else:
                start_date, end_date = today, today

        with c2:
            divs = fetch_all("SELECT id, bow_type_code FROM division WHERE is_active = 1")
            div_map = {d['bow_type_code']: d['id'] for d in divs}
            
            # Default to member's division if possible
            def_idx = 0
            if member['division_id']:
                for i, code in enumerate(div_map.keys()):
                    if div_map[code] == member['division_id']:
                        def_idx = i
                        break
            
            sel_div = st.selectbox("Division", list(div_map.keys()), index=def_idx)
            sel_div_id = div_map[sel_div]

        with c3:
            st.write("")
            st.write("")
            champ_only = st.checkbox("Championships Only")

    st.divider()

    # ------------------------------------------------------
    # 2. FETCH DATA
    # ------------------------------------------------------
    age_code = _calculate_age_class(member['birth_year'])
    cat_str = _get_category_string(age_code, member['gender_id'], sel_div)

    # Fetch Active Competitions
    sql = """
        SELECT c.id, c.name, c.start_date, c.end_date 
        FROM competition c
        WHERE c.end_date >= :s AND c.start_date <= :e
    """
    if champ_only:
        sql += " AND c.name LIKE '%Championship%'"
    sql += " ORDER BY c.end_date ASC"
    
    comps = fetch_all(sql, {"s": start_date, "e": end_date})
    
    if not comps:
        st.info("No active competitions found for these filters.")
        return

    # ------------------------------------------------------
    # 3. TABS (Competitions)
    # ------------------------------------------------------
    tabs = st.tabs([c['name'] for c in comps])

    for tab, comp in zip(tabs, comps):
        with tab:
            # Deadline Warning
            days_left = (comp['end_date'] - datetime.date.today()).days
            if 0 <= days_left <= 2:
                st.info(f"⚠️ Competition ends in {days_left} day(s)! Please complete your scores.", icon="⏳")
            elif days_left < 0:
                st.warning("Competition has ended. Editing is disabled.")

            # Title
            st.markdown(f"### {member['av_number']} - {comp['name']}")
            st.caption(f"**Category:** {cat_str} | **Date:** {comp['start_date']} to {comp['end_date']}")

            # Fetch Existing Session for this specific Archer/Comp/Division
            # Using LEFT JOIN to category to ensure we match the SELECTED division
            sess_sql = """
                SELECT s.id, s.status, r.round_name, r.id as rid
                FROM session s
                JOIN competition_entry ce ON ce.session_id = s.id
                JOIN category cat ON cat.id = ce.category_id
                JOIN round r ON r.id = s.round_id
                WHERE ce.competition_id = :cid 
                  AND s.member_id = :mid
                  AND cat.division_id = :did
            """
            sess = fetch_one(sess_sql, {"cid": comp['id'], "mid": member['id'], "did": sel_div_id})

            # Grid Data
            grid_rows = []
            if sess:
                # Calculate total from DB for the Grid View (Initial state)
                # Note: If user edits below, we might want to show that, but Grid usually reflects DB.
                tot_res = fetch_one("""
                    SELECT SUM(CASE 
                        WHEN arrow_value = 'X' THEN 10 
                        WHEN arrow_value = 'M' THEN 0 
                        ELSE CAST(arrow_value AS UNSIGNED) 
                    END) as total 
                    FROM arrow a JOIN `end` e ON a.end_id = e.id 
                    WHERE e.session_id = :sid
                """, {"sid": sess['id']})
                
                grid_rows.append({
                    "Round Name": sess['round_name'],
                    "Category": cat_str,
                    "Running Total": int(tot_res['total']) if tot_res and tot_res['total'] else 0,
                    "Status": sess['status'],
                    "_sid": sess['id'],
                    "_rid": sess['rid']
                })

            # "Start New Score" if no session exists
            if not grid_rows and days_left >= 0:
                st.info("No score entry found for this competition & division.")
                if st.button("Start New Score", key=f"new_{comp['id']}"):
                    rounds = fetch_all("SELECT id, round_name FROM round ORDER BY round_name")
                    r_map = {r['round_name']: r['id'] for r in rounds}
                    r_sel = st.selectbox("Select Round", list(r_map.keys()), key=f"rsel_{comp['id']}")
                    
                    if st.button("Create Entry", key=f"crt_{comp['id']}"):
                        # Find Category ID
                        cat_res = fetch_one("""
                            SELECT id FROM category 
                            WHERE age_class_id = (SELECT id FROM age_class WHERE age_class_code=:ac LIMIT 1)
                            AND gender_id = :gid AND division_id = :did
                        """, {"ac": age_code, "gid": member['gender_id'], "did": sel_div_id})
                        
                        if cat_res:
                            exec_sql("INSERT INTO session (member_id, round_id, shoot_date, status) VALUES (:m, :r, :d, 'Preliminary')",
                                     {"m": member['id'], "r": r_map[r_sel], "d": datetime.date.today()})
                            sid_res = fetch_one("SELECT LAST_INSERT_ID() as id")
                            exec_sql("INSERT INTO competition_entry (session_id, competition_id, category_id) VALUES (:s, :c, :cat)",
                                     {"s": sid_res['id'], "c": comp['id'], "cat": cat_res['id']}) #type: ignore
                            st.success("Entry created!")
                            st.rerun()
                        else:
                            st.error(f"Category '{cat_str}' not found in database. Please contact Recorder.")
                continue 

            # Render Grid
            if HAS_AGGRID and grid_rows:
                df = pd.DataFrame(grid_rows)
                gb = GridOptionsBuilder.from_dataframe(df) #type: ignore
                gb.configure_column("_sid", hide=True)
                gb.configure_column("_rid", hide=True)
                gb.configure_selection("single", use_checkbox=False)
                grid_response = AgGrid(df, gridOptions=gb.build(), height=120, key=f"ag_{comp['id']}") #type: ignore
                selected = grid_response['selected_rows']
            else:
                st.dataframe(pd.DataFrame(grid_rows))
                # Fallback selection: simple selectbox if no AG Grid or if user prefers
                sel_idx = st.selectbox("Select Row to Edit", range(len(grid_rows)), format_func=lambda i: grid_rows[i]['Round Name'], key=f"fb_{comp['id']}") if grid_rows else None
                selected = [grid_rows[sel_idx]] if sel_idx is not None else []

            # ------------------------------------------------------
            # 4. SCORE EDITOR
            # ------------------------------------------------------
            if selected:
                # Handle AG Grid return format (list of dicts or DataFrame)
                row = selected.iloc[0] if isinstance(selected, pd.DataFrame) else selected[0]
                
                sid = row['_sid']
                rid = row['_rid']
                status = row['Status']
                is_locked = (days_left < 0) or (status != 'Preliminary')

                st.divider()
                if is_locked:
                    st.warning(f"Editing disabled. Score is {status}.")

                # Fetch Ranges
                ranges = fetch_all("SELECT id, distance_m, face_size, ends_per_range FROM round_range WHERE round_id=:rid ORDER BY distance_m DESC", {"rid": rid})
                
                if ranges:
                    # Range Selector
                    r_opts = {f"{r['distance_m']}m ({r['face_size']}cm)": r for r in ranges}
                    sel_r_lbl = st.selectbox("Select Range", list(r_opts.keys()), key=f"rng_{sid}")
                    curr_range = r_opts[sel_r_lbl]
                    range_id = curr_range['id']
                    total_ends = curr_range['ends_per_range']

                    # Ensure DB structure
                    if not is_locked:
                        _ensure_db_structure(sid, range_id, total_ends)

                    # Initialize Buffer / Smart Nav
                    # Check where the user left off (first end with 'M')
                    nav_key = f"nav_{sid}_{range_id}"
                    if nav_key not in st.session_state:
                        # Check buffer first, then DB
                        current_first_empty = 1
                        # Pre-load buffer to check for Ms
                        _get_arrows_from_buffer_or_db(sid, range_id, 1, total_ends)
                        buf = st.session_state[f"buffer_{sid}_{range_id}"]
                        
                        for i in range(1, total_ends + 1):
                            if 'M' in buf[i]:
                                current_first_empty = i
                                break
                        st.session_state[nav_key] = current_first_empty

                    curr_end = st.session_state[nav_key]

                    # Title
                    st.markdown(f"#### End {curr_end} / {total_ends}")

                    # Arrow Inputs
                    cols = st.columns(6)
                    # Get values from buffer (or DB if first load)
                    current_vals = _get_arrows_from_buffer_or_db(sid, range_id, curr_end, total_ends)
                    
                    for i, col in enumerate(cols):
                        val = col.selectbox(
                            f"Arrow {i+1}", 
                            options=ARROW_VALUES,
                            index=ARROW_VALUES.index(current_vals[i]) if current_vals[i] in ARROW_VALUES else 11, # Default M
                            key=f"a_{sid}_{range_id}_{curr_end}_{i}",
                            disabled=is_locked,
                            label_visibility="collapsed"
                        )
                        # Update Buffer ONLY (No DB write)
                        if val != current_vals[i]:
                            _update_buffer(sid, range_id, curr_end, i, val)
                            st.rerun()

                    # Nav Buttons
                    c_prev, c_next = st.columns(2)
                    if c_prev.button("⬅️ Previous", key=f"p_{sid}", disabled=curr_end==1):
                        st.session_state[nav_key] -= 1
                        st.rerun()
                    if c_next.button("Next ➡️", key=f"n_{sid}", disabled=curr_end==total_ends):
                        st.session_state[nav_key] += 1
                        st.rerun()

                    # Running Total (UI Only)
                    # We display the total for THIS range based on buffered values
                    rng_total = _calculate_running_total_from_buffer(sid, range_id)
                    st.metric("Range Running Total (Preview)", rng_total)

                    # Responsibility & Submit
                    st.markdown("---")
                    if not is_locked:
                        agree = st.checkbox("I confirm that I am responsible for the accuracy of this score.", key=f"chk_{sid}")
                        if st.button("Submit Score", key=f"sub_{sid}", disabled=not agree, type="primary"):
                            # 1. Save Buffer to DB
                            _commit_buffer_to_db(sid, range_id)
                            # 2. Update Status? (Requirement says "once... clicks submit")
                            # Usually submit implies Final, but maybe they just want to save?
                            # Assuming 'Submit' implies finalizing or at least saving progress. 
                            # Requirements say "Archers' only permission is that they can edit... when they haven't pressed the submit button".
                            # This implies Submit LOCKS it.
                            exec_sql("UPDATE session SET status='Final' WHERE id=:sid", {"sid": sid})
                            st.success("✅ Score Submitted and Saved to Database.")
                            st.rerun()