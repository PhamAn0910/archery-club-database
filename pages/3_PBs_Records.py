
import streamlit as st
from app import get_logged_in_av_number

def main():
    st.title("🏆 PBs & Records")
    av_number = get_logged_in_av_number()
    if av_number:
        st.info(f"Your AV Number: {av_number}")
    st.write("This page displays personal bests and records for the archer.")

if __name__ == "__main__":
    main()
