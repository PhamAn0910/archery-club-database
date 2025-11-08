from __future__ import annotations
import functools
import streamlit as st

def get_auth() -> dict:
    return st.session_state.get("auth", {})

def require_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        auth = get_auth()
        if not auth.get("logged_in"):
            st.info("Please log in to view this page.")
            return
        return func(*args, **kwargs)
    return wrapper

def require_recorder(func):
    @functools.wraps(func)
    @require_login
    def wrapper(*args, **kwargs):
        auth = get_auth()
        if not auth.get("is_recorder"):
            st.info("Recorder access required.")
            return
        return func(*args, **kwargs)
    return wrapper

def require_archer(func):
    @functools.wraps(func)
    @require_login
    def wrapper(*args, **kwargs):
        auth = get_auth()
        if auth.get("is_recorder"):
            st.info("This page is for archers only.")
            return
        return func(*args, **kwargs)
    return wrapper
