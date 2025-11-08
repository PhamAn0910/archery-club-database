"""Recorder Management Page"""
import streamlit as st
from guards import require_recorder

@require_recorder
def show_recorder_management():
    st.header("⚙️ Recorder Management")
    st.write("This page is for recorders to manage club data and users.")