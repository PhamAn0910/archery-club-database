from __future__ import annotations
import contextlib
import streamlit as st
from sqlalchemy import text
from db_config import get_engine as _get_engine

@st.cache_resource
def get_engine():
    """Cached SQLAlchemy Engine (shared across reruns)."""
    return _get_engine()

@contextlib.contextmanager
def ro_conn():
    """Read-only connection (no explicit commit)."""
    with get_engine().connect() as c:
        yield c

@contextlib.contextmanager
def rw_tx():
    """Read-write transaction; auto commit/rollback."""
    with get_engine().begin() as tx:
        yield tx

def fetch_one(sql: str, params: dict | None = None):
    with ro_conn() as c:
        return c.execute(text(sql), params or {}).mappings().fetchone()

def fetch_all(sql: str, params: dict | None = None):
    with ro_conn() as c:
        return c.execute(text(sql), params or {}).mappings().fetchall()

def exec_sql(sql: str, params: dict | None = None):
    with rw_tx() as tx:
        tx.execute(text(sql), params or {})
