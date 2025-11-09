from __future__ import annotations
import streamlit as st
from db_core import fetch_all, fetch_one, exec_sql


# ==========================================================
#  READ FUNCTIONS (unchanged)
# ==========================================================

@st.cache_data(ttl=60)
def list_rounds():
    """List all available rounds."""
    return fetch_all(
        """
        SELECT r.id, r.round_name,
               (SELECT COUNT(*) FROM round_range rr WHERE rr.round_id = r.id) AS range_count
        FROM round r
        ORDER BY r.round_name
        """
    )


@st.cache_data(ttl=60)
def list_ranges(round_id: int):
    """List all distances/ranges for a given round."""
    return fetch_all(
        """
        SELECT id, distance_m, face_size, ends_per_range
        FROM round_range
        WHERE round_id = :rid
        ORDER BY distance_m
        """,
        {"rid": round_id},
    )


# ==========================================================
#  WRITE FUNCTIONS (new)
# ==========================================================

def create_session(member_id: int, round_id: int, shoot_date: str, status: str = "Preliminary") -> int:
    """
    Create a new shooting session for an archer.
    Returns the newly created session ID.
    """
    sql = """
        INSERT INTO session (member_id, round_id, shoot_date, status)
        VALUES (:mid, :rid, :date, :status)
    """
    exec_sql(sql, {"mid": member_id, "rid": round_id, "date": shoot_date, "status": status})

    # Fetch the new session ID
    row = fetch_one(
        "SELECT MAX(id) AS session_id FROM session WHERE member_id = :mid AND round_id = :rid",
        {"mid": member_id, "rid": round_id},
    )
    return row["session_id"] if row else None


def save_end(session_id: int, round_range_id: int, end_no: int, arrow_values: list[str]):
    """
    Save a completed end and its six arrows.
    - session_id: current session
    - round_range_id: distance/face being shot
    - end_no: which end number (1–6)
    - arrow_values: list like ['10','9','8','X','M','7']
    """

    # 1 - Insert End
    sql_end = """
        INSERT INTO `end` (session_id, round_range_id, end_no)
        VALUES (:sid, :rrid, :end_no)
    """
    exec_sql(sql_end, {"sid": session_id, "rrid": round_range_id, "end_no": end_no})

    # 2️ - Fetch the new End ID
    end_row = fetch_one(
        "SELECT MAX(id) AS end_id FROM `end` WHERE session_id = :sid",
        {"sid": session_id},
    )
    end_id = end_row["end_id"]

    # 3️ - Insert all 6 arrows
    for i, token in enumerate(arrow_values, start=1):
        sql_arrow = """
            INSERT INTO arrow (end_id, arrow_no, arrow_value)
            VALUES (:eid, :ano, :aval)
        """
        exec_sql(sql_arrow, {"eid": end_id, "ano": i, "aval": token})


def finalize_session(session_id: int):
    """
    Optionally mark a session as 'Confirmed' after all ends are recorded.
    """
    sql = "UPDATE session SET status = 'Confirmed' WHERE id = :sid"
    exec_sql(sql, {"sid": session_id})
