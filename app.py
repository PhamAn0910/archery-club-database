from __future__ import annotations
import streamlit as st
from ui_sidebar import render_sidebar
from pages.round_definitions import show_round_definitions
from pages.score_entry import show_score_entry
from pages.score_history import show_score_history
from pages.pbs_records import show_pbs_records
from pages.competition_results import show_competition_results
from pages.championship_ladder import show_championship_ladder
from pages.recorder_approval import show_recorder_approval
from pages.recorder_management import show_recorder_management
from data_rounds import list_rounds, list_ranges 

st.set_page_config(
    page_title="Archery Score Hub",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

# Hide Streamlit's default navigation
st.markdown("""
<style>
[data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Initialize current page if not set
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

# Render the sidebar with navigation
render_sidebar()
## Map page keys to their rendering functions and call the selected one.
# This removes the long if/elif chain and makes adding pages simpler.
page_renderers = {
    "home": show_round_definitions,
    "score_entry": show_score_entry,
    "score_history": show_score_history,
    "pbs_records": show_pbs_records,
    "competition_results": show_competition_results,
    "championship_ladder": show_championship_ladder,
    "recorder_approval": show_recorder_approval,
    "recorder_management": show_recorder_management,
}

# Resolve the renderer for the current page (fall back to home)
renderer = page_renderers.get(st.session_state.get("current_page", "home"), show_round_definitions)
renderer()

# Session state for selection is page-local; simple key is fine
if "ui.selected_round_id" not in st.session_state:
    st.session_state["ui.selected_round_id"] = None
