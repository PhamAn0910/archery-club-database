"""Score History Page"""
import streamlit as st
from guards import require_archer

@require_archer
def show_score_history():
    st.header("📊 Score History")
    st.write("This page shows the archer's score history.")