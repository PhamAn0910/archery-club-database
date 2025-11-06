import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from db_config import get_engine
from models import Archer, Gender, Division, Base # Import models and Base
import datetime

# --- Database Setup (cached to avoid re-initialization) ---
@st.cache_resource
def init_db():
    """Initialize database engine and create tables (runs once per session)."""
    try:
        engine = get_engine()
        # Test the connection before creating tables
        with engine.connect() as conn:
            pass  # Just test if connection works
        Base.metadata.create_all(engine)  # Ensure tables exist
        return sessionmaker(bind=engine), None
    except Exception as e:
        # Return None for SessionLocal and the error message
        return None, str(e)

SessionLocal, db_error = init_db() 

# --- App ---
st.title("🏹 Archery Score Recording")

# Check if database connection failed
if db_error or SessionLocal is None:
    st.error("⚠️ Database Connection Failed")
    st.warning(f"**Error:** {db_error}")
    st.info("""
    **Possible reasons:**
    - You're using `localhost` which only works on your local machine
    - For Streamlit Cloud deployment, you need a cloud-hosted database
    - Check your secrets configuration in Streamlit Cloud dashboard
    
    **To fix this:**
    1. Set up a cloud-hosted MySQL database
    2. Update your secrets in Streamlit Cloud (Settings → Secrets)
    3. Use the cloud database host instead of 'localhost'
    """)
    st.stop()  # Stop execution here

# At this point, SessionLocal is guaranteed to be valid
st.header("All Archers")

# --- Read and Display Archers ---
try:
    with SessionLocal() as session:
        # Query to get all archers and their related gender/division
        statement = select(Archer, Gender.gender_code, Division.bow_type_code) \
                        .join(Archer.gender) \
                        .join(Archer.division) \
                        .order_by(Archer.id)
        
        results = session.execute(statement).all()
        
        # Display in a simple way
        if results:
            st.subheader("Current Archers in Database:")
            for row in results:
                archer = row[0] # The Archer object
                gender = row[1]
                division = row[2]
                st.write(f"ID: {archer.id} | Birth Year: {archer.birth_year} | Category: {gender} {division}")
        else:
            st.write("No archers found in the database.")

except Exception as e:
    st.error(f"Error connecting to database: {e}")


# --- Form to Create a New Archer ---
st.header("Add New Archer")

# Pre-load options (this is just an example)
# In a real app, you'd query these from the Gender/Division tables
gender_options = {"Male": "M", "Female": "F"}
div_options = {"Recurve": "R", "Compound": "C", "Longbow": "L"}

with st.form("new_archer_form"):
    birth_year = st.number_input("Birth Year", min_value=1920, max_value=2025, value=2000)
    gender_choice = st.selectbox("Gender", options=gender_options.keys())
    div_choice = st.selectbox("Division", options=div_options.keys())
    
    submitted = st.form_submit_button("Add Archer")
    
    if submitted:
        try:
            with SessionLocal() as session:
                # Find the actual Gender and Division objects
                gender_code = gender_options[gender_choice]
                div_code = div_options[div_choice]
                
                gender_obj = session.execute(select(Gender).where(Gender.gender_code == gender_code)).scalar_one()
                div_obj = session.execute(select(Division).where(Division.bow_type_code == div_code)).scalar_one()
                
                # Create and add the new archer
                new_archer = Archer(
                    birth_year=birth_year,
                    gender=gender_obj,
                    division=div_obj
                )
                session.add(new_archer)
                session.commit()
                
                st.success(f"Successfully added new archer with ID: {new_archer.id}!")
                st.rerun() # Rerun the script to show the new archer in the list
                
        except Exception as e:
            st.error(f"Error adding archer: {e}")
            st.warning("Note: Make sure your Gender (M, F) and Division (R, C, L) tables are pre-filled with data!")