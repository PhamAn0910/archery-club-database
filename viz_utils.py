from __future__ import annotations
from datetime import date, datetime
from typing import Union, Optional
import plotly.graph_objects as go
import plotly.express as px

def apply_chart_theme(fig: go.Figure) -> go.Figure:
    """
    Apply consistent styling to all Plotly figures for the Archery Club Dashboard.

    Args:
        fig (go.Figure): The Plotly figure to style.

    Returns:
        go.Figure: The styled figure.
    """
    fig.update_layout(
        font_family="Inter, system-ui, sans-serif",
        autosize=True,
        height=400,
        margin={'t': 40, 'b': 40, 'l': 40, 'r': 20},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        hovermode="x unified",
        colorway=px.colors.qualitative.Set2,
    )
    
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#E5E7EB",
        zeroline=False
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#E5E7EB",
        zeroline=False
    )
    
    return fig

def arrow_value_to_score(arrow_value: str) -> int:
    """
    Convert arrow value to numeric score.
    
    Args:
        arrow_value (str): The arrow value (e.g., 'X', '10', '9', 'M').
        
    Returns:
        int: The numeric score. Returns 0 for 'M' or invalid input.
        
    Examples:
        >>> arrow_value_to_score('X')
        10
        >>> arrow_value_to_score('M')
        0
        >>> arrow_value_to_score('9')
        9
    """
    if not arrow_value:
        return 0
        
    val = arrow_value.strip().upper()
    
    if val == 'X':
        return 10
    elif val == 'M':
        return 0
    
    try:
        return int(val)
    except ValueError:
        return 0

def format_date_for_display(date_val: Union[date, str, None]) -> str:
    """
    Format dates consistently as DD-MM-YYYY.
    
    Args:
        date_val (date | str | None): The date object or 'YYYY-MM-DD' string.
        
    Returns:
        str: The formatted date string or empty string if input is None.
        
    Examples:
        >>> format_date_for_display('2023-11-21')
        '21-11-2023'
    """
    if date_val is None:
        return ""
        
    if isinstance(date_val, str):
        try:
            # Parse YYYY-MM-DD
            dt = datetime.strptime(date_val, "%Y-%m-%d")
            return dt.strftime("%d-%m-%Y")
        except ValueError:
            return date_val # Return original if parse fails
            
    if isinstance(date_val, (date, datetime)):
        return date_val.strftime("%d-%m-%Y")
        
    return str(date_val)

def get_color_by_score(score: int, max_score: int) -> str:
    """
    Color-code by performance percentage.
    
    Args:
        score (int): The achieved score.
        max_score (int): The maximum possible score.
        
    Returns:
        str: Hex color code.
        
    Rules:
        - >90%: Green (#099268)
        - 70-90%: Blue (#1c7ed6)
        - 50-70%: Orange (#f59f00)
        - <50%: Red (#fa5252)
    """
    if max_score <= 0:
        return "#fa5252" # Default to red if invalid max_score
        
    percentage = (score / max_score) * 100
    
    if percentage > 90:
        return "#099268"
    elif percentage >= 70:
        return "#1c7ed6"
    elif percentage >= 50:
        return "#f59f00"
    else:
        return "#fa5252"
