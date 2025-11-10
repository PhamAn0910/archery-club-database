"""Quick test to see what HTML Streamlit generates for buttons"""
import streamlit as st

st.markdown("### Default button (no type):")
st.button("Default Button", key="btn1")

st.markdown("### Primary button:")
st.button("Primary Button", type="primary", key="btn2")

st.markdown("### Secondary button:")
st.button("Secondary Button", type="secondary", key="btn3")

# Add JavaScript to log button attributes
st.markdown("""
<script>
setTimeout(() => {
    const buttons = document.querySelectorAll('button');
    buttons.forEach((btn, i) => {
        console.log(`Button ${i}:`, {
            text: btn.innerText,
            kind: btn.getAttribute('kind'),
            class: btn.className,
            allAttributes: Array.from(btn.attributes).map(a => `${a.name}="${a.value}"`).join(', ')
        });
    });
}, 1000);
</script>
""", unsafe_allow_html=True)
