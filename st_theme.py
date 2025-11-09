from __future__ import annotations
from pathlib import Path
import streamlit as st


def _read_file_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def inject_react_theme() -> None:
    """Inject CSS from the React app into the Streamlit page.

    This function looks for the two primary CSS files used by the React
    dashboard in this repository:

    - Archery Club Dashboard App/src/styles/globals.css
    - Archery Club Dashboard App/src/index.css

    If found, their contents are embedded inside a <style> tag placed via
    st.markdown(..., unsafe_allow_html=True). This exposes CSS variables,
    base HTML styles, and many Tailwind utility classes so Streamlit's
    rendered HTML can more closely match the original styling.
    """
    repo_root = Path(__file__).parent
    # Paths relative to repository root
    react_src = repo_root / "Archery Club Dashboard App" / "src"
    css_paths = [
        react_src / "styles" / "globals.css",
        react_src / "index.css",
        # Global overrides for Streamlit widgets (maps tokens to selectors)
        repo_root / "assets" / "global_overrides.css",
        # Small project-specific CSS that customizes the Streamlit sidebar
        repo_root / "assets" / "sidebar.css",
    ]

    css_parts = []
    for p in css_paths:
        if p.exists():
            css_parts.append(_read_file_text(p))

    if not css_parts:
        # Nothing to inject
        return

    combined_css = "\n\n".join(css_parts)

    # Minimal wrapper to keep the CSS scoped to the Streamlit app.
    style_block = f"""
<style>
/* Injected React/Tailwind CSS - may be large. */
{combined_css}

/* Some helpful defaults so Streamlit-native widgets get similar spacing */
html, body {{
  background: var(--color-background, #ffffff);
  color: var(--color-foreground, #000);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI",
    Roboto, "Helvetica Neue", Arial;
}}

.stApp {{
  padding: 1rem 1.5rem;
}}
</style>
"""

    st.markdown(style_block, unsafe_allow_html=True)
