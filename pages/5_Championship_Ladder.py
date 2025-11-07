
import streamlit as st
from sqlalchemy import text
from db_config import get_engine

def main():
    st.title("🥇 Championship Ladder")
    # Display a table with AV numbers for all archers in the ladder
    engine = get_engine()
    with engine.connect() as conn:
        query = text("""
            SELECT cm.av_number, cm.full_name, SUM(ce.final_total) AS total_score
            FROM club_member cm
            JOIN session s ON cm.id = s.member_id
            JOIN competition_entry ce ON ce.session_id = s.id
            GROUP BY cm.av_number, cm.full_name
            ORDER BY total_score DESC
        """)
        results = conn.execute(query).fetchall()
        if results:
            st.dataframe([
                {"AV Number": row.av_number, "Name": row.full_name, "Total Score": row.total_score} for row in results
            ])
        else:
            st.info("No championship ladder data available.")

if __name__ == "__main__":
    main()
