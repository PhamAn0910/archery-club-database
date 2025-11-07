

# --- Imports ---
import streamlit as st
from sqlalchemy import text
from db_config import get_engine
import random
import string

# --- Utility Functions ---
def generate_unique_av_number(conn, prefix="VIC", length=3):
    while True:
        suffix = ''.join(random.choices(string.digits, k=length))
        av_number = f"{prefix}{suffix}"
        result = conn.execute(text("SELECT 1 FROM club_member WHERE av_number = :av_number"), {"av_number": av_number}).fetchone()
        if not result:
            return av_number

def get_member_info(member_id):
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Fetch member info including av_number
            query = text("""
                SELECT id, full_name, is_recorder, av_number
                FROM club_member
                WHERE id = :member_id
            """)
            result = conn.execute(query, {"member_id": member_id}).fetchone()
            if result:
                av_number = result.av_number
                # If av_number is missing, generate and update it
                if not av_number:
                    av_number = generate_unique_av_number(conn)
                    update_query = text("UPDATE club_member SET av_number = :av_number WHERE id = :id")
                    conn.execute(update_query, {"av_number": av_number, "id": result.id})
                    conn.commit()
                return {
                    "id": result.id,
                    "full_name": result.full_name,
                    "is_recorder": bool(result.is_recorder),
                    "av_number": av_number
                }
            return None
    except Exception as e:
        st.error(f"Database error during login: {e}")
        return None

def get_logged_in_av_number():
    """Return the AV number for the currently logged-in user, or None if not logged in."""
    if not st.session_state.get("logged_in", False):
        return None
    try:
        engine = get_engine()
        with engine.connect() as conn:
            query = text("SELECT av_number FROM club_member WHERE id = :id")
            result = conn.execute(query, {"id": st.session_state.archer_id}).fetchone()
            if result:
                return result.av_number
    except Exception as e:
        st.warning(f"Could not fetch AV number: {e}")
    return None

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Archery Score Hub",
    page_icon="🎯",
    layout="wide"
)


# --- Page Functions ---
def login_page():
    st.title("🎯 Archery Score Hub Login")
    st.write("Enter your 6-digit club Member ID to log in.")
    login_id_str = st.text_input("Member ID", placeholder="e.g., 123456", max_chars=6)
    if st.button("Log In", type="primary"):
        try:
            login_id = int(login_id_str)
            member = get_member_info(login_id)
            if member:
                st.session_state.archer_id = member["id"]
                st.session_state.archer_name = member["full_name"]
                st.session_state.is_recorder = member["is_recorder"]
                st.session_state.logged_in = True
                st.session_state.view_mode = "Archer"
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Member ID not found.")
        except ValueError:
            st.error("Please enter a valid 6-digit numeric ID.")


def round_definitions_page():
    st.header("📖 Round Definitions (Home)")
    st.write("This is the home page for all users. Display round definitions here.")

def score_entry_page():
    st.header("🎯 Score Entry")
    st.write("This page is for archers to enter their scores.")

def score_history_page():
    st.header("📊 Score History")
    st.write("This page shows the archer's score history.")

def pbs_records_page():
    st.header("🏆 PBs & Records")
    st.write("This page displays personal bests and records for the archer.")

def competition_results_page():
    st.header("🏁 Competition Results")
    st.write("This page shows competition results for the archer.")

def championship_ladder_page():
    st.header("🥇 Championship Ladder")
    st.write("This page displays the championship ladder for archers.")

def recorder_approval_page():
    if not st.session_state.get("logged_in", False) or not st.session_state.get("is_recorder", False):
        st.info("You must be logged in as a recorder to view this page.")
        return
    st.header("🔒 Recorder Approval")
    st.write("This page is for recorders to approve scores.")

def recorder_management_page():
    if not st.session_state.get("logged_in", False) or not st.session_state.get("is_recorder", False):
        st.info("You must be logged in as a recorder to view this page.")
        return
    st.header("⚙️ Recorder Management")
    st.write("This page is for recorders to manage club data and users.")

# --- Main App Routing ---
def main():
    st.title("🏹 Archery Club Score System")
    PAGES = {
        "Home": round_definitions_page,
        "Login": login_page,
        "Score Entry": score_entry_page,
        "Score History": score_history_page,
        "PBs & Records": pbs_records_page,
        "Competition Results": competition_results_page,
        "Championship Ladder": championship_ladder_page,
        "Recorder Approval": recorder_approval_page,
        "Recorder Management": recorder_management_page,
    }
    menu = list(PAGES.keys())
    choice = st.sidebar.selectbox("Navigation", menu)
    # Call the selected page function
    PAGES[choice]()

if __name__ == "__main__":
    main()