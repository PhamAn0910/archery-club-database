"""Score Entry Page"""
import streamlit as st
from guards import require_archer

@require_archer
def show_score_entry():
    st.header("🎯 Score Entry")
    st.write("This page is for archers to enter their scores.")