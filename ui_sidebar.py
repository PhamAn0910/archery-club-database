# ui_sidebar.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import streamlit as st
import streamlit.components.v1 as components

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
        # If the file already starts with a <style> tag, return as-is.
        # Using startswith avoids false-positives where the substring
        # '<style>' appears inside a comment or elsewhere.
        if text.lstrip().startswith("<style>"):
            return text
        return f"<style>\n{text}\n</style>"
    except Exception:
        # Don't fail the app if the CSS file is missing; fall back to no CSS.
        return ""


# Page identifiers for navigation
PUBLIC_PAGES = [
    (":material/leaderboard: Competition Results", "competition_results"),
    (":material/social_leaderboard: Club Championship", "championship_ladder"),
    (":material/rewarded_ads: Round Bests", "club_pbs"),
]

ARCHER_PAGES = [
    (":material/target: Score Entry", "score_entry"),
    (":material/bar_chart_4_bars: My Scores", "score_history"),
    (":material/workspace_premium: Personal Bests", "pbs_records"),
]

RECORDER_PAGES = [
    (":material/done_all: Approve Scores", "recorder_approval"),
    (":material/manage_accounts: Manage Club", "recorder_management"),
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
        "Home": [(":material/home: Home", "home")],
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

    # We'll render a simple input and place the submit button outside the
    # Streamlit form container so the button isn't affected by OS-level
    # dark-mode form rendering. Use a number input and validate on submit.

    # Hide the small InputInstructions Streamlit widget (if present)
    hide_form_instructions_style = """
        <style>
            [data-testid="InputInstructions"] {
                display: none;
            }
        </style>
    """
    st.markdown(hide_form_instructions_style, unsafe_allow_html=True)

    # Use a numeric input for Member ID (original behaviour). This
    # enforces integer input and makes validation simpler.
    # Use typing.cast to keep the runtime value as None but satisfy the
    # type-checker (Streamlit's number_input expects a numeric default).
    # At runtime this still produces an empty input with the placeholder
    # visible; cast silences Pylance's reportArgumentType.
    member_id = st.number_input(
        label="Member ID",
        min_value=MEMBER_ID_MIN,
        value=cast(int, MEMBER_ID_MIN),
        # placeholder="Enter your Member ID",
        step=1,
        format="%d",
        key="ui.login_member_id",
    )

    # Render the login button outside of any form so it's not styled by
    # Streamlit's form submit variants (this helps avoid OS dark-mode visual
    # treatments on the submit control).
    if st.button("Log in", use_container_width=True, key="ui.login_submit", type="tertiary"):
        # Explicit None check first (clear, local validation). This avoids
        # catching unrelated exceptions and communicates intent.
        if member_id is None:
            st.error("Please enter a valid numeric Member ID.")
            return

        # Convert to a plain Python int for downstream code. Keep the
        # conversion local to this handler so we don't mutate stored data
        # globally.
        try:
            member_id_int = int(member_id)
        except (TypeError, ValueError):
            st.error("Please enter a valid numeric Member ID.")
            return

        profile = load_member_profile(member_id_int)
        if not profile:
            # Do not reveal whether the Member ID exists; use a generic
            # message.
            st.error("Invalid credentials. Please check your Member ID and try again.")
            return

        _set_auth(AuthState(
            logged_in=True,
            id=profile["id"],
            name=profile["full_name"],
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
    if st.button("⤴ Logout", use_container_width=True, key="ui.logout_submit", type="tertiary"):
        _reset_auth()
        st.rerun()


def _profile_card_html(auth: AuthState) -> str:
        """Return the HTML for the profile card. Pure function (no side-effects).

        Kept small so unit tests can verify HTML structure independently.
        """
        return f"""
        <div class="profile-card">
            <div class="profile-top">Logged in as</div>
            <div class="profile-name">{auth.name or ''}</div>
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
    # Render a section header for any section except the Home section so
    if section_name != "Home" and (section_name == "Recorder" or section_name == "Archer"): 
        # Keep the small styling for role-based section.
        st.markdown(f'<div class="section-small">{section_name}</div>', unsafe_allow_html=True)
    else:
        # Default section header for Public section.
        st.markdown(f'<div class="section-header">{section_name}</div>', unsafe_allow_html=True)

    for label, page_id in links:
        if st.button(
            label,
            key=f"nav_{page_id}",
            use_container_width=True,
            type="primary" if st.session_state.get("current_page") == page_id else "secondary",
        ):
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

    # Render the entire sidebar inside the `st.sidebar` context so our
    # scoped CSS variables and the #custom-sidebar wrapper apply to every
    # control we add here.
    with st.sidebar:
        # Wrap the sidebar content in a single wrapper so our CSS is reliably
        # scoped. Render the CSS first so it applies to the subsequent HTML.
        if css_markup:
            st.markdown(css_markup, unsafe_allow_html=True)

        # Local sidebar styles are now moved to assets/sidebar.css and
        # are loaded via _load_sidebar_css(). This keeps presentation
        # separate from logic and makes the styles easier to test and
        # maintain.

        # Sidebar wrapper. Keep it minimal (no inline logo) so spacing
        # is controlled entirely via CSS.
        # st.markdown('<div id="custom-sidebar">', unsafe_allow_html=True)

        st.markdown("<h2>Archery Club</h2>", unsafe_allow_html=True)
        # Divider under the title 
        st.markdown('<hr class="title-divider">',
            unsafe_allow_html=True,
        )

        # Auth area
        if auth.logged_in:
            _render_profile_panel(auth)
        else:
            _render_login_panel(auth)

        # Section separator
        st.markdown('<hr class="section-divider">',
            unsafe_allow_html=True,
        )

        # Nav (computed as pure data, then rendered)
        sections = _visible_sections(auth)
        _render_nav(sections)

        # Footer rule
        st.markdown(
            '<hr class="footer-divider">',
            unsafe_allow_html=True,
        )
        st.caption("©2025 Powerpuff Girls Group")
        st.markdown('</div>', unsafe_allow_html=True)