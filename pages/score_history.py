import streamlit as st
from guards import require_archer
from db_core import fetch_all

# ==========================================================
# MAIN PAGE FUNCTION
# ==========================================================
@require_archer
def show_score_history():
    st.title("Score History Page")