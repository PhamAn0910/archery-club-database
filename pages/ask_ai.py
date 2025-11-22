from __future__ import annotations

import re
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st
import google.generativeai as genai

from db_core import fetch_all
from guards import require_archer
from viz_utils import apply_chart_theme


@st.cache_resource
def _configure_gemini():
    api_key = st.secrets["google_ai"]["api_key"]
    genai.configure(api_key=api_key)
    
    # UPDATED SYSTEM INSTRUCTION with correct schema
    system_instruction = (
        "You are a MySQL expert for an archery database. "
        "The main tables and their relationships are: \n"
        "- session (id, member_id, round_id, shoot_date, status, division_id) - shooting sessions\n"
        "- competition_entry (id, competition_id, session_id, category_id, final_total, rank_in_category) - has final scores\n"
        "- round (id, round_name) - round definitions\n"
        "- division (id, bow_type_code) - equipment types\n"
        "- club_member (id, full_name) - member info\n"
        "- category (id, age_class_id, gender_id, division_id) - competition categories\n"
        "\n"
        "IMPORTANT SCHEMA NOTES:\n"
        "- Scores are in competition_entry.final_total (not in session directly)\n"
        "- Join session -> competition_entry to get scores\n"
        "- Arrow table is NOT directly linked to sessions\n"
        "\n"
        "RULES:\n"
        "1. The user is an Archer with ID :member_id.\n"
        "2. You MUST include 'WHERE s.member_id = :member_id' in every query.\n"
        "3. Only show the user's own data.\n"
        "4. Use 's' as alias for session, 'ce' for competition_entry.\n"
        "5. To get scores, JOIN session s with competition_entry ce ON s.id = ce.session_id.\n"
        "6. Return ONLY the raw SQL query. No markdown, no backticks, no explanations.\n"
        "7. For score analysis, use ce.final_total as the score column."
    )
    
    return genai.GenerativeModel(
        model_name="gemini-2.5-pro",  # Also fixed model name
        system_instruction=system_instruction,
    )


def _sanitize_sql(raw_sql: str) -> str:
    """Removes markdown formatting often added by LLMs."""
    cleaned = raw_sql.strip()
    cleaned = re.sub(r"```sql|```", "", cleaned, flags=re.IGNORECASE).strip()
    return cleaned


def _generate_sql(question: str) -> str:
    model = _configure_gemini()
    
    # clear prompt to guide the specific question
    prompt = (
        f"Generate a MySQL query for this question: '{question}'\n"
        "Ensure you join relevant tables (round, division) to make names readable."
    )
    
    try:
        response = model.generate_content(prompt)
        if not response or not response.text:
            raise RuntimeError("No SQL returned by AI model.")
        return _sanitize_sql(response.text)
    except Exception as e:
        raise RuntimeError(f"Gemini API Error: {str(e)}")


def _visualize(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No data found.")
        return

    # Identify column types
    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    date_cols = [col for col in df.columns if "date" in col.lower()]
    # Look for categorical columns (like round name or division)
    cat_cols = [col for col in df.columns if any(x in col.lower() for x in ["round", "division", "name", "type"])]

    # Scenario 1: Single value metric (e.g., "What is my highest score?")
    if len(df) == 1 and len(df.columns) == 1:
        value = df.iloc[0, 0]
        st.metric("Result", value)
        return

    # Scenario 2: Date-based trend (Line Chart)
    # e.g., "How have my scores changed over time?"
    if date_cols and numeric_cols:
        date_col = date_cols[0]
        val_col = numeric_cols[0]
        
        df_plot = df.copy()
        df_plot[date_col] = pd.to_datetime(df_plot[date_col])
        
        # Use round name as color if available
        color_col = cat_cols[0] if cat_cols else None
        
        fig = px.line(df_plot, x=date_col, y=val_col, color=color_col, markers=True)
        fig = apply_chart_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("View Data"):
            st.dataframe(df, use_container_width=True)
        return

    # Scenario 3: Categorical Comparison (Bar Chart)
    # e.g., "Average score by round"
    if cat_cols and numeric_cols:
        fig = px.bar(df, x=cat_cols[0], y=numeric_cols[0])
        fig = apply_chart_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)
        return

    # Default: Just show the table
    st.dataframe(df, use_container_width=True)


@require_archer
def show_ask_ai():
    st.title("🤖 AI Analyst (Beta)")
    st.caption("Ask natural language questions about your confirmed scores.")

    auth = st.session_state.get("auth", {})
    member_id = auth.get("id")
    if not member_id:
        st.info("Log in as an archer to use this tool.")
        return

    # Input Section
    with st.form("ai_query_form"):
        question = st.text_area(
            "Ask about your performance...",
            placeholder="e.g. What is my average score for WA 900?",
            height=100
        )
        submitted = st.form_submit_button("Analyze", type="primary")

    # Processing Section
    if submitted:
        if not question.strip():
            st.warning("Please enter a question first.")
            return

        with st.spinner("Analyzing data with Gemini..."):
            try:
                # 1. Generate SQL
                sql = _generate_sql(question)
                
                # 2. Debug Expander (Hidden by default)
                with st.expander("See generated SQL"):
                    st.code(sql, language="sql")

                # 3. Execute SQL safely with member_id param
                rows = fetch_all(sql, {"member_id": member_id})
                
                # 4. Visualize
                df = pd.DataFrame(rows)
                _visualize(df)

            except Exception as exc:
                st.error(f"Analysis failed: {exc}")
                # Show the specific 404 or API error if it happens again
                if "404" in str(exc):
                    st.error("Model not found. Please check `st.secrets` and ensure 'gemini-2.0-flash' is available.")