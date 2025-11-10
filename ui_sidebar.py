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

    # Inject a small client-side script that submits the login when the
    # user presses Enter while focused in the Member ID input. This uses
    # the input's aria-label to locate it and clicks the visible 'Log in'
    # button; it doesn't change layout or widget types.
    components.html(
        """
        <script>
        (function(){
          const tryAttach = () => {
            const input = document.querySelector('input[aria-label="Member ID"]');
            const btn = Array.from(document.querySelectorAll('button')).find(b=>b.innerText && b.innerText.trim()==='Log in');
            if(input && btn){
              input.addEventListener('keydown', function(e){
                if(e.key === 'Enter'){
                  btn.click();
                }
              });
              return true;
            }
            return false;
          };
          const timer = setInterval(()=>{ if(tryAttach()) clearInterval(timer); }, 200);
          setTimeout(()=>clearInterval(timer), 5000);
        })();
        </script>
        """,
        height=0,
    )

    # Render the login button outside of any form so it's not styled by
    # Streamlit's form submit variants (this helps avoid OS dark-mode visual
    # treatments on the submit control).
    if st.button("Log in", use_container_width=True, key="ui.login_submit"):
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
    if st.button("⤴ Logout", use_container_width=True):
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
        st.markdown('<div id="custom-sidebar">', unsafe_allow_html=True)

        # Client-side behavior: mark the most recently clicked sidebar button
        # with an 'always-active' class so it remains highlighted even while
        # Streamlit processes the click. Remove the class from other buttons.
        # This provides instant visual feedback without changing the app logic.
        components.html(
            """
            <script>
            (function(){
              const attachButtonListeners = () => {
                const sidebarContainer = document.getElementById('custom-sidebar');
                if(!sidebarContainer) return false;
                
                // Get ALL buttons in sidebar
                const allButtons = Array.from(sidebarContainer.querySelectorAll('.stButton > button'));
                
                // DEBUG: Create visible debug output in the page
                const debugDiv = document.createElement('div');
                debugDiv.id = 'button-debug-output';
                debugDiv.style.cssText = 'position:fixed;top:10px;right:10px;background:#fff;border:2px solid red;padding:10px;max-width:400px;max-height:80vh;overflow:auto;z-index:9999;font-size:10px;font-family:monospace;';
                debugDiv.innerHTML = '<strong>BUTTON DEBUG (Total: ' + allButtons.length + ')</strong><br><br>';
                
                allButtons.forEach((btn, i) => {
                  const text = (btn.innerText || '').trim();
                  const kind = btn.getAttribute('kind');
                  const dataBaseweb = btn.getAttribute('data-baseweb');
                  const bgColor = window.getComputedStyle(btn).backgroundColor;
                  const border = window.getComputedStyle(btn).border;
                  
                  debugDiv.innerHTML += `<div style="margin-bottom:10px;padding:5px;background:#f0f0f0;">
                    <b>Button ${i}: "${text}"</b><br>
                    kind: ${kind}<br>
                    data-baseweb: ${dataBaseweb}<br>
                    class: ${btn.className}<br>
                    bg-color: ${bgColor}<br>
                    border: ${border}
                  </div>`;
                });
                
                document.body.appendChild(debugDiv);
                
                if(allButtons.length === 0) return false;
                
                // Filter to navigation buttons (exclude Login/Logout)
                const navButtons = allButtons.filter(btn => {
                  const text = btn.innerText || btn.textContent || '';
                  return !text.includes('Log in') && !text.includes('Logout');
                });
                
                navButtons.forEach(btn => {
                  if(btn.dataset._alwaysActiveAttached === '1') return;
                  btn.dataset._alwaysActiveAttached = '1';
                  
                  btn.addEventListener('click', (e) => {
                    navButtons.forEach(b => b.classList.remove('always-active'));
                    e.currentTarget.classList.add('always-active');
                  });
                  
                  btn.addEventListener('keydown', (e) => {
                    if(e.key === 'Enter' || e.key === ' ') {
                      navButtons.forEach(b => b.classList.remove('always-active'));
                      btn.classList.add('always-active');
                    }
                  });
                });
                return true;
              };
              
              const retryInterval = setInterval(() => {
                if(attachButtonListeners()) clearInterval(retryInterval);
              }, 200);
              
              setTimeout(() => clearInterval(retryInterval), 5000);
            })();
            </script>
                  
                  // Keyboard handler
                  btn.addEventListener('keydown', (e) => {
                    if(e.key === 'Enter' || e.key === ' ') {
                      navButtons.forEach(b => b.classList.remove('always-active'));
                      btn.classList.add('always-active');
                    }
                  });
                });
                return true;
              };
              
              // Retry until buttons are found
              const retryInterval = setInterval(() => {
                if(attachButtonListeners()) clearInterval(retryInterval);
              }, 200);
              
              setTimeout(() => clearInterval(retryInterval), 5000);
            })();
            </script>
            """,
            height=0,
        )

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
        
        # DEBUG using components.html instead of st.markdown
        components.html("""
            <script>
            (function() {
                const debug = document.createElement('div');
                debug.id = 'button-debug-box';
                debug.style.cssText = 'position:fixed;top:10px;right:10px;background:yellow;border:3px solid red;padding:15px;z-index:99999;font-family:monospace;font-size:11px;max-width:450px;max-height:600px;overflow:auto;';
                debug.innerHTML = '<b>DEBUG SCRIPT RUNNING...</b><br><br>';
                document.body.appendChild(debug);
                
                setTimeout(() => {
                    const sidebar = document.querySelector('[data-testid="stSidebar"]');
                    const customSidebar = document.getElementById('custom-sidebar');
                    
                    debug.innerHTML += sidebar ? '✓ Found [data-testid="stSidebar"]<br>' : '✗ NO stSidebar<br>';
                    debug.innerHTML += customSidebar ? '✓ Found #custom-sidebar<br>' : '✗ NO #custom-sidebar<br>';
                    
                    const allButtons = document.querySelectorAll('button');
                    debug.innerHTML += `<br>Total buttons in page: ${allButtons.length}<br><br>`;
                    
                    // Find buttons in sidebar
                    const sidebarButtons = sidebar ? Array.from(sidebar.querySelectorAll('button')) : [];
                    debug.innerHTML += `Buttons in sidebar: ${sidebarButtons.length}<br><hr>`;
                    
                    sidebarButtons.forEach((btn, i) => {
                        const text = (btn.innerText || '').substring(0, 25);
                        const kind = btn.getAttribute('kind') || 'null';
                        const dataBaseweb = btn.getAttribute('data-baseweb') || 'null';
                        const className = btn.className.substring(0, 50);
                        const bg = window.getComputedStyle(btn).backgroundColor;
                        
                        debug.innerHTML += `<div style="background:#f0f0f0;margin:5px 0;padding:5px;">
                            <b>${i}: "${text}"</b><br>
                            kind: ${kind}<br>
                            data-baseweb: ${dataBaseweb}<br>
                            class: ${className}<br>
                            bg: ${bg}
                        </div>`;
                    });
                }, 2000);
            })();
            </script>
        """, height=0)
