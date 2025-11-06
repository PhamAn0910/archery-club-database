import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

def get_engine():
    """
    Creates and returns a SQLAlchemy engine configured from Streamlit secrets.
    """
    # Load secrets from Streamlit (using [connections.mysql])
    db_credentials = st.secrets["connections"]["mysql"]
    
    # Create the connection URL
    connection_url = URL.create(
        "mysql+pymysql",
        username=db_credentials['username'],
        password=db_credentials['password'],
        host=db_credentials['host'],
        port=db_credentials['port'],
        database=db_credentials['database']
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