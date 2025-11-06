import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

def get_engine():
    """
    Creates and returns a SQLAlchemy engine configured from Streamlit secrets.
    """
    # Load secrets from Streamlit
    db_creds = st.secrets["database"]
    
    # Create the connection URL
    connection_url = URL.create(
        drivername=f"{db_creds['db_type']}+pymysql",
        username=db_creds['username'],
        password=db_creds['password'],
        host=db_creds['host'],
        port=db_creds['port'],
        database=db_creds['database_name']
    )
    
    # Create and return the engine
    # echo=True is useful for debugging, it logs all SQL queries
    engine = create_engine(connection_url, echo=True)
    return engine

if __name__ == "__main__":
    # Test the connection
    engine = get_engine()
    try:
        with engine.connect() as connection:
            print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")