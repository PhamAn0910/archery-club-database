"""Personal Bests & Records Page"""
import streamlit as st
from guards import require_archer

@require_archer
def show_pbs_records():
    st.header("🏅 Personal Bests")
    st.write("This page displays personal bests and records for the archer.")