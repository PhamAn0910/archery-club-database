
import streamlit as st
from app import get_logged_in_av_number

def main():
    st.title("⚙️ Recorder Management")
    if not st.session_state.get("logged_in", False) or not st.session_state.get("is_recorder", False):
        st.info("You must be logged in as a recorder to view this page.")
        return
    av_number = get_logged_in_av_number()
    if av_number:
        st.info(f"Your AV Number: {av_number}")
    st.write("This page is for recorders to manage club data and users.")

if __name__ == "__main__":
    main()
