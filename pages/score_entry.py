from __future__ import annotations
import streamlit as st
from datetime import date
from guards import require_archer
    
@require_archer
def show_score_entry():
    st.title("Score Entry Page")