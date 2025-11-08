# ui_sidebar.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import streamlit as st

from auth import load_member_profile  # dependency injected at module level

# ---------- Paths & constants ----------

BASE_DIR = Path(__file__).resolve().parent
PAGES_DIR = BASE_DIR / "pages"

HOME_PAGE = "app.py"

# Minimum allowed member ID (used by the login widget)
MEMBER_ID_MIN = 100000

def _load_sidebar_css() -> str:
    """Load the sidebar CSS from the assets folder.

    Returns the raw CSS/html (which may include <style> tags). If the
    external file is missing, return an empty string so rendering still works.
    """
    try:
        css_path = BASE_DIR / "assets" / "sidebar.css"
        text = css_path.read_text(encoding="utf-8")
        # If the file already contains a <style> tag, return as-is. Otherwise
        # wrap the CSS in a <style> so Streamlit injects it rather than
        # rendering it as visible text.
        if "<style" in text:
            return text
        return f"<style>\n{text}\n</style>"
    except Exception:
        # Don't fail the app if the CSS file is missing; fall back to no CSS.
        return ""


# Page identifiers for navigation
PUBLIC_PAGES = [
    ("🏆 Competition Results", "competition_results"),
    ("🏆 Club Championship", "championship_ladder"),
]

ARCHER_PAGES = [
    ("🎯 Score Entry", "score_entry"),
    ("📊 My Scores", "score_history"),
    ("🏅 Personal Bests", "pbs_records"),
]

RECORDER_PAGES = [
    ("✅ Approve Scores", "recorder_approval"),
    ("⚙️ Manage Club", "recorder_management"),
]

# ---------- Lightweight auth model ----------

@dataclass
class AuthState:
    logged_in: bool = False
    id: int | None = None
    name: str | None = None
    is_recorder: bool = False
    av: str | None = None

def _get_auth() -> AuthState:
    raw = st.session_state.get("auth")
    if not raw:
        return AuthState()
    return AuthState(
        logged_in=bool(raw.get("logged_in")),
        id=raw.get("id"),
        name=raw.get("name"),
        is_recorder=bool(raw.get("is_recorder")),
        av=raw.get("av"),
    )

def _set_auth(a: AuthState) -> None:
    st.session_state["auth"] = {
        "logged_in": a.logged_in,
        "id": a.id,
        "name": a.name,
        "is_recorder": a.is_recorder,
        "av": a.av,
    }

def _reset_auth() -> None:
    _set_auth(AuthState())

# ---------- File helpers (decoupled from UI) ----------

def _exists(rel_path: str) -> bool:
    # Paths are resolved relative to this file (same dir as app.py)
    return (BASE_DIR / rel_path).exists()

# ---------- Navigation model ----------

def _visible_sections(auth: AuthState) -> dict[str, list[tuple[str, str]]]:
    """
    Build a pure data model of navigation sections -> [(label, page_id), ...]
    """
    sections = {
        "Home": [("🏠 Home", "home")],
        "Public": PUBLIC_PAGES.copy(),
    }

    # Archer (logged-in but not recorder)
    if auth.logged_in and not auth.is_recorder:
        sections["Archer"] = ARCHER_PAGES.copy()

    # Recorder
    if auth.logged_in and auth.is_recorder:
        sections["Recorder"] = RECORDER_PAGES.copy()

    return sections

# ---------- UI panels (small & focused) ----------

def _render_login_panel(auth: AuthState) -> None:
    if auth.logged_in:
        return
    
    # Custom CSS to hide the "Press Enter to submit" instruction
    hide_form_instructions_style = """
        <style>
            [data-testid="InputInstructions"] {
                display: none;
            }
        </style>
    """
    st.markdown(hide_form_instructions_style, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False, enter_to_submit=True):
        # Use st.numeric_input to enforce numeric values client-side.
        # initialize empty with value=None to use placeholder
        # return=None(default) until the user enters a value to notify error.
        member_id = st.number_input(
            label="Member ID",
            min_value=MEMBER_ID_MIN,
            value=None,  # Set to None to show the placeholder
            placeholder="Enter your Member ID",
            format="%d",
            step=1,
        )

        submitted = st.form_submit_button("Log in", use_container_width=True)
    if not submitted:
        return

    # Validate numeric input: require a positive integer and handle the
    # empty-initial state (None) returned when the user hasn't entered a value.
    if member_id is None:
        st.error("Please enter a valid numeric Member ID.")
        return

    profile = load_member_profile(member_id)
    if not profile:
        # Do not reveal whether the Member ID exists; use a generic message.
        st.error("Invalid credentials. Please check your Member ID and try again.")
        return

    _set_auth(AuthState(
        logged_in=True,
        id=profile["id"],
        # Name is intentionally omitted for privacy; only AV is exposed to the UI.
        name=None,
        is_recorder=profile["is_recorder"],
        av=profile["av_number"],
    ))
    st.success("Login successful!")
    st.rerun()

def _render_profile_panel(auth: AuthState) -> None:
    if not auth.logged_in:
        return

    # Keep HTML generation separate for easier testing and maintenance.
    st.markdown(_profile_card_html(auth), unsafe_allow_html=True)

    # Logout button below the card. Keep event handling here (loose coupling)
    if st.button("⤴ Logout", use_container_width=True):
        _reset_auth()
        st.rerun()


def _profile_card_html(auth: AuthState) -> str:
        """Return the HTML for the profile card. Pure function (no side-effects).

        Kept small so unit tests can verify HTML structure independently.
        """
        # Minimal card to avoid displaying personal names. Show AV only.
        # Keep the "Logged in as" label for clarity while omitting the name.
        return f"""
<div class="profile-card">
    <div class="profile-top">Logged in as</div>
    <div class="profile-av">{auth.av or ''}</div>
</div>
"""

def _render_nav(sections: dict[str, list[tuple[str, str]]]) -> None:
    # Navigation (Home first)
    for label, page_id in sections.get("Home", []):
        if st.button(label, key=f"nav_{page_id}", use_container_width=True,
                    type="primary" if st.session_state.get("current_page") == page_id else "secondary"):
            st.session_state.current_page = page_id
            st.rerun()

    # Remaining sections in order; rendering delegated to helper for clarity
    ordered = ["Public", "Archer", "Recorder"]
    for sec in ordered:
        links = sections.get(sec)
        if not links:
            continue
        _render_section(sec, links)


def _render_section(section_name: str, links: list[tuple[str, str]]) -> None:
    """Render a navigation section and its links.

    This helper centralizes the presentation of each section (headings,
    spacing) so `_render_nav` remains concise and the code is easier to
    modify.
    """
    if section_name == "Recorder":
        st.markdown('<div class="section-small">Recorder</div>', unsafe_allow_html=True)

    for label, page_id in links:
        # Wrap each button in a container to allow precise CSS targeting.
        container_key = f"nav_container_{page_id}"
        st.markdown(f'<div class="nav-button" id="{container_key}"></div>', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{page_id}", use_container_width=True,
                     type="primary" if st.session_state.get("current_page") == page_id else "secondary"):
            st.session_state.current_page = page_id
            st.rerun()

# ---------- Public API ----------

def render_sidebar() -> None:
    """
    Orchestrates the sidebar: title -> login/profile -> navigation -> footer.
    Minimal branching; rendering is delegated to focused helpers.
    """
    auth = _get_auth()

    # Load external scoped CSS (keeps presentation separate from logic)
    css_markup = _load_sidebar_css()

    # Ensure there's always a current page so the 'Home' button can be styled
    # as active by default.
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"

    with st.sidebar:
        # Wrap the sidebar content in a single wrapper so our CSS is reliably
        # scoped. Render the CSS first so it applies to the subsequent HTML.
        if css_markup:
            st.markdown(css_markup, unsafe_allow_html=True)
        st.markdown('<div id="custom-sidebar">', unsafe_allow_html=True)
        st.markdown("<h2>Archery Club</h2>", unsafe_allow_html=True)
        st.markdown("---")

        # Auth area
        if auth.logged_in:
            _render_profile_panel(auth)
        else:
            _render_login_panel(auth)

        st.markdown("---")

        # Nav (computed as pure data, then rendered)
        sections = _visible_sections(auth)
        _render_nav(sections)

        st.markdown("---")
        st.caption("©2025 Powerpuff Girls Group")
        st.markdown('</div>', unsafe_allow_html=True)
