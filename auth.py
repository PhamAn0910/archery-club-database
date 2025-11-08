from __future__ import annotations
from sqlalchemy import text
from db_core import fetch_one

def load_member_profile(member_id: int) -> dict | None:
    """
    Load member (id, name, is_recorder, av_number).
    """
    row = fetch_one(
        """
        SELECT id, full_name, COALESCE(is_recorder, false) AS is_recorder, av_number
        FROM club_member WHERE id=:id
        """,
        {"id": member_id},
    )
    if not row:
        return None
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "is_recorder": bool(row["is_recorder"]),
        "av_number": row["av_number"],
    }
