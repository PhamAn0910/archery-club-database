"""Recorder Management Page"""
import streamlit as st
from guards import require_recorder

@require_recorder
def show_recorder_management():
# ==========================================================
#  RECORDER PAGE 2: ADMIN MANAGEMENT
# ==========================================================
    st.title("Admin Management")
    st.caption("Manage club data and system configuration")

    st.markdown("### 👥 User Management")
    st.info("Add, edit, or deactivate club users.")
    st.write("🧑‍💻 Coming soon: Create or edit user accounts")

    st.markdown("### 🎯 Round Management")
    st.info("Add or update official round definitions.")
    st.write("⚙️ Coming soon: Import or modify round data")

    st.markdown("### 🏆 Competition Setup")
    st.info("Define club competitions and link them to rounds.")
    st.write("📅 Coming soon: Schedule competitions for the season")

