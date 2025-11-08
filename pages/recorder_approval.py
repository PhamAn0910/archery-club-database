"""Recorder Approval Page"""
import streamlit as st
from guards import require_recorder

@require_recorder
def show_recorder_approval():
    st.header("✅ Recorder Approval")
    st.write("This page is for recorders to approve scores.")