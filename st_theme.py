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
            content = _read_file_text(p)
            css_parts.append(content)
            # DEBUG: Print what's being loaded
            print(f"✓ Loaded CSS from: {p.name} ({len(content)} chars)")
        else:
            print(f"✗ NOT FOUND: {p}")

    if not css_parts:
        # Nothing to inject
        print("⚠ No CSS files found to inject!")
        return
    
    print(f"📦 Combining {len(css_parts)} CSS files...")

    combined_css = "\n\n".join(css_parts)

    # Use components.html to inject CSS into PARENT window
    # Encode CSS as base64 to avoid escaping issues with special characters
    import streamlit.components.v1 as components
    import base64
    
    # Add wrapper styles for Streamlit
    full_css = f"""{combined_css}

/* Streamlit defaults */
html, body {{
  background: var(--color-background, #ffffff);
  color: var(--color-foreground, #000);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
}}

.stApp {{
  padding: 1rem 1.5rem;
}}"""
    
    # Encode to base64 to avoid JavaScript escaping issues
    css_b64 = base64.b64encode(full_css.encode('utf-8')).decode('ascii')
    
    components.html(f"""
<script>
(function() {{
    const parentDoc = window.parent.document;
    
    // Remove old injection if exists
    const old = parentDoc.getElementById('injected-theme-css');
    if (old) old.remove();
    
    // Decode base64 CSS
    const cssB64 = '{css_b64}';
    const cssText = atob(cssB64);
    
    // Create and inject style element
    const style = parentDoc.createElement('style');
    style.id = 'injected-theme-css';
    style.textContent = cssText;
    parentDoc.head.appendChild(style);
    
    console.log('✅ Injected', cssText.length, 'chars of CSS');
}})();
</script>
""", height=0)
    
    print(f"✅ Injected {len(full_css)} chars of CSS via base64 encoding")
