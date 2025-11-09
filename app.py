from __future__ import annotations
import streamlit as st
from ui_sidebar import render_sidebar
# Inject React/Tailwind-based CSS variables and base styles so Streamlit UI closely
# matches the Archery Club Dashboard App look-and-feel.
try:
    from st_theme import inject_react_theme
    INJECT_THEME = True
except Exception:
    INJECT_THEME = False
from pages.round_definitions import show_round_definitions
from pages.score_entry import show_score_entry
from pages.score_history import show_score_history
from pages.pbs_records import show_pbs_records
from pages.competition_results import show_competition_results
from pages.championship_ladder import show_championship_ladder
from pages.recorder_approval import show_recorder_approval
from pages.recorder_management import show_recorder_management

st.set_page_config(
    page_title="Archery Score Hub",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

# Apply injected theme (if available). This reads the repository CSS files and
# places them into the Streamlit page head so spacing, variables and base
# typography are available to subsequent components.
if INJECT_THEME:
    try:
        inject_react_theme()
    except Exception:
        # Non-fatal: continue without injected theme if something goes wrong.
        pass

# NOTE: we no longer hide Streamlit's sidebar container wholesale here because
# that also hides any custom content we render into the sidebar. If you need
# to hide a specific built-in control in future, target that element more
# precisely (or hide it after rendering the custom sidebar).

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
