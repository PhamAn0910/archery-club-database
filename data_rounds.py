from __future__ import annotations
import streamlit as st
from db_core import fetch_all

@st.cache_data(ttl=60)
def list_rounds():
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
    return fetch_all(
        """
        SELECT id, distance_m, face_size, ends_per_range
        FROM round_range
        WHERE round_id=:rid
        ORDER BY distance_m
        """,
        {"rid": round_id},
    )
