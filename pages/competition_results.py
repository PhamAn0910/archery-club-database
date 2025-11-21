import streamlit as st
import pandas as pd
from datetime import date
from db_core import fetch_all
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from viz_utils import apply_chart_theme


# Category color palette - distinct vibrant colors
CATEGORY_COLORS = {
    0: '#ef4444',  # Red
    1: '#f59e0b',  # Amber/Orange  
    2: '#10b981',  # Green
    3: '#3b82f6',  # Blue
    4: '#8b5cf6',  # Purple
    5: '#ec4899',  # Pink
    6: '#06b6d4',  # Cyan
    7: '#f97316',  # Orange
}


def get_category_gradient(base_hex, rank_position, total_in_category):
    """
    Creates a color gradient from dark (best) to light (worst) within a category.
    
    Args:
        base_hex: Base color in hex format (e.g., '#ef4444')
        rank_position: 0-indexed position (0 = 1st place, 1 = 2nd, etc.)
        total_in_category: Total number of competitors in category
    
    Returns:
        Hex color string with gradient applied
    """
    # Convert hex to RGB
    base_hex = base_hex.lstrip('#')
    r, g, b = tuple(int(base_hex[i:i+2], 16) for i in (0, 2, 4))
    
    # Calculate intensity: 1st place = 1.0 (darkest), last = 0.4 (lightest)
    if total_in_category == 1:
        intensity = 1.0
    else:
        intensity = 1.0 - (rank_position / (total_in_category - 1)) * 0.6
    
    # Mix with white to lighten
    new_r = int(r + (255 - r) * (1 - intensity))
    new_g = int(g + (255 - g) * (1 - intensity))
    new_b = int(b + (255 - b) * (1 - intensity))
    
    return f'#{new_r:02x}{new_g:02x}{new_b:02x}'


def show_competition_results():
    # ==========================================================
    # PAGE HEADER
    # ==========================================================
    st.title("🏁 Competition Results")
    st.caption("View official results from completed competitions")

    # ==========================================================
    # FETCH COMPETITION LIST
    # ==========================================================
    comps = fetch_all(
        "SELECT id, name, start_date, end_date FROM competition ORDER BY start_date DESC"
    )
    if not comps:
        st.info("No competitions found in the database.")
        return

    # --------------------------------------------------
    # DATE RANGE FILTER
    # --------------------------------------------------
    min_start = min(c["start_date"] for c in comps)
    max_end = max(c["end_date"] for c in comps)

    default_range = (min_start, max_end)
    date_range = st.date_input(
        "Filter by Date Range",
        value=default_range,
        min_value=min_start,
        max_value=max_end,
    )

    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_filter, end_filter = date_range
    else:
        start_filter = end_filter = date_range

    if start_filter > end_filter:
        st.error("Start date must be on or before the end date.")
        st.stop()

    comps_in_range = [
        c for c in comps if start_filter <= c["start_date"] <= end_filter
    ]

    if not comps_in_range:
        st.warning("No competitions fall within the selected date range.")
        st.stop()

    comp_names = ["Choose a competition..."] + [
        f"{c['name']} ({c['start_date']})" for c in comps_in_range
    ]
    selected_comp = st.selectbox("Select Competition", comp_names)

    if selected_comp == "Choose a competition...":
        st.stop()

    comp_index = comp_names.index(selected_comp) - 1
    comp_id = comps_in_range[comp_index]["id"]

    # ==========================================================
    # FETCH COMPETITION RESULTS (DB)
    # ==========================================================
    results = fetch_all(
        """
        SELECT 
            ce.rank_in_category AS placement,
            m.full_name AS archer,
            CONCAT(ac.age_class_code, ' ', g.gender_code, ' ', d.bow_type_code) AS category_label,
            r.round_name AS round_name,
            ce.final_total AS total_score,
            s.shoot_date AS shoot_date
        FROM competition_entry ce
        JOIN session s ON s.id = ce.session_id
        JOIN club_member m ON m.id = s.member_id
        JOIN category cat ON cat.id = ce.category_id
        JOIN age_class ac ON ac.id = cat.age_class_id
        JOIN gender g ON g.id = cat.gender_id
        JOIN division d ON d.id = cat.division_id
        JOIN round r ON r.id = s.round_id
        WHERE ce.competition_id = :cid
          AND s.status = 'Confirmed'
          AND s.shoot_date BETWEEN :start_date AND :end_date
          AND ce.final_total IS NOT NULL
        ORDER BY category_label, placement, total_score DESC;
        """,
        {"cid": comp_id, "start_date": start_filter, "end_date": end_filter},
    )

    if not results:
        st.warning("No confirmed entries found for this competition in the chosen range.")
        return

    # ==========================================================
    # DISPLAY RESULTS BY DIVISION
    # ==========================================================
    df = pd.DataFrame(results)
    df["Date"] = pd.to_datetime(df["shoot_date"]).dt.date
    display_df = df.rename(
        columns={
            "placement": "Rank",
            "archer": "Archer",
            "category_label": "Category",
            "round_name": "Round",
            "total_score": "Score",
        }
    )[["Rank", "Archer", "Category", "Round", "Score", "Date"]]

    display_df = display_df.sort_values(["Score", "Rank"], ascending=[False, True])

    # Add overall ranking based purely on score (not by category)
    display_df = display_df.reset_index(drop=True)
    display_df['Overall_Rank'] = display_df['Score'].rank(method='min', ascending=False).astype(int)
    
    # Rename and reorder columns for display - show Overall_Rank as "Rank"
    display_columns = display_df[["Overall_Rank", "Archer", "Category", "Round", "Score", "Date"]].copy()
    display_columns = display_columns.rename(columns={"Overall_Rank": "Rank"})

    st.dataframe(
        display_columns.style.set_table_styles(
            [
                {
                    "selector": "thead th",
                    "props": [
                        ("background-color", "#f5f5f5"),
                        ("font-weight", "bold"),
                    ],
                }
            ]
        ),
        use_container_width=True,
    )

    # ==========================================================
    # VISUAL RANKINGS CHART
    # ==========================================================
    st.markdown("---")
    st.subheader("📊 Visual Rankings")
    
    # Prepare data for visualization
    viz_df = display_df.copy()
    
    # Remove any potential duplicates - keep only one entry per archer per category
    viz_df = viz_df.sort_values(['Category', 'Archer', 'Score', 'Rank'], 
                               ascending=[True, True, False, True])
    viz_df = viz_df.drop_duplicates(subset=['Category', 'Archer'], keep='first')
    
    # Diagnostic check - verify no duplicates
    duplicate_check = viz_df.groupby(['Category', 'Archer']).size()
    if duplicate_check.max() > 1:
        st.warning(f"⚠️ Data quality issue: Some archers have duplicate entries. Max duplicates: {duplicate_check.max()}")
    
    # Add medal emojis for top 3 overall (not by category)
    def add_medal_emoji(row):
        if row['Overall_Rank'] == 1:
            return f"🥇 {row['Archer']}"
        elif row['Overall_Rank'] == 2:
            return f"🥈 {row['Archer']}"
        elif row['Overall_Rank'] == 3:
            return f"🥉 {row['Archer']}"
        else:
            return row['Archer']
    
    viz_df['Archer_Display'] = viz_df.apply(add_medal_emoji, axis=1)
    
    # Calculate score gap from overall leader (highest score)
    overall_leader_score = viz_df['Score'].max()
    viz_df['score_gap'] = overall_leader_score - viz_df['Score']
    
    # Category filter
    categories = sorted(viz_df['Category'].unique())
    selected_category = st.selectbox(
        "Filter by category (optional)",
        options=['All Categories'] + categories,
        key='viz_category_filter'
    )
    
    # Get competition name for title
    comp_name = comps_in_range[comp_index]['name']
    custom_margin = dict(l=200, r=50, t=100, b=50)
    fig_height_override = None
    
    if selected_category == 'All Categories':
        # Show all categories with color-coded bars (one color per category with gradient)
        if len(categories) > 1:
            # Sort by category, then by score (descending for best-to-worst ordering)
            viz_df_sorted = viz_df.sort_values(['Category', 'Score'], ascending=[True, False]).reset_index(drop=True)
            
            # Create category-to-color mapping
            category_list = sorted(viz_df['Category'].unique())
            category_color_map = {}
            
            for idx, cat in enumerate(category_list):
                category_color_map[cat] = CATEGORY_COLORS[idx % len(CATEGORY_COLORS)]
            
            # Calculate gradient colors for each archer based on position within category
            colors_list = []
            y_positions = []  # Track cumulative positions for separator lines
            cumulative_position = 0
            
            for cat in category_list:
                cat_data = viz_df_sorted[viz_df_sorted['Category'] == cat].reset_index(drop=True)
                base_color = category_color_map[cat]
                
                # Verify no duplicates within category
                if cat_data['Archer'].nunique() != len(cat_data):
                    st.error(f"⚠️ Duplicate archers detected in {cat}!")
                
                for pos in range(len(cat_data)):
                    gradient_color = get_category_gradient(base_color, pos, len(cat_data))
                    colors_list.append(gradient_color)
                
                cumulative_position += len(cat_data)
                y_positions.append(cumulative_position)
            
            viz_df_sorted['bar_color'] = colors_list
            
            # Build y-axis positions with gaps (small between archers, larger between categories)
            archer_spacing = 1.0
            category_spacing_extra = 0.8
            position_map = {}
            tick_positions = []
            tick_labels = []
            current_y = 0.0
            for cat_index, cat in enumerate(category_list):
                cat_indices = viz_df_sorted[viz_df_sorted['Category'] == cat].index.tolist()
                for idx_val in cat_indices:
                    position_map[idx_val] = current_y
                    tick_positions.append(current_y)
                    tick_labels.append(viz_df_sorted.loc[idx_val, 'Archer_Display'])
                    current_y += archer_spacing
                # add extra spacing between categories (except after last)
                if cat_index != len(category_list) - 1:
                    current_y += category_spacing_extra
            viz_df_sorted['y_position'] = viz_df_sorted.index.map(position_map)
            
            # Create single horizontal bar chart
            fig = go.Figure()
            
            # Add bars - one trace per archer for individual hover control
            bar_width = 0.7
            for idx, row in viz_df_sorted.iterrows():
                fig.add_trace(go.Bar(
                    y=[row['y_position']],
                    x=[row['Score']],
                    orientation='h',
                    marker_color=row['bar_color'],
                    width=bar_width,
                    showlegend=False,
                    hovertemplate=(
                        f"<b>{row['Archer_Display']}</b><br>"
                        f"Category: {row['Category']}<br>"
                        f"Score: {row['Score']}<br>"
                        f"Overall Rank: {row['Overall_Rank']}<br>"
                        f"Gap from 1st: -{row['score_gap']} points<br>"
                        "<extra></extra>"
                    )
                ))
            
            # Calculate compact height: 35px per archer plus category gaps
            total_archers = len(viz_df_sorted)
            effective_vertical_units = max(current_y, total_archers)
            fig_height = max(400, effective_vertical_units * 35 + 120)
            
            # Calculate required right margin based on longest category name
            max_category_length = max(len(cat) for cat in category_list)
            # Approximate: 7px per character + 80px buffer for color square and padding
            right_margin = max(250, max_category_length * 7 + 80)
            custom_margin = dict(l=200, r=right_margin, t=80, b=60)
            fig_height_override = fig_height
            
            fig.update_layout(
                title=f"Rankings by Category - {comp_name}",
                height=fig_height,
                showlegend=False,
                margin=dict(l=200, r=right_margin, t=80, b=60),  # Dynamic right margin
                xaxis_title="Total Score",
                yaxis_title="",
                font=dict(size=12, family="Inter, system-ui, sans-serif"),
                title_font=dict(size=16, family="Inter, system-ui, sans-serif")
            )
            
            # Style axes
            fig.update_xaxes(
                showgrid=True,
                gridcolor='#E5E7EB',
                gridwidth=1,
                tickfont=dict(size=12)
            )
            fig.update_yaxes(
                showgrid=False,
                tickfont=dict(size=12),
                tickmode='array',
                tickvals=tick_positions,
                ticktext=tick_labels,
                autorange='reversed'
            )
            
            # Add custom category legend on the right side
            legend_x = 1.01  # Position closer to chart edge
            legend_y = 0.98  # Slightly down from top
            legend_spacing = 0.06  # Vertical spacing between items
            
            # Legend title
            fig.add_annotation(
                text="<b>Categories</b>",
                xref="paper", yref="paper",
                x=legend_x, y=legend_y,
                showarrow=False,
                font=dict(size=14, family="Inter, system-ui, sans-serif", color='#111827'),
                xanchor='left',
                yanchor='top'
            )
            
            # Add legend items for each category
            for idx, cat in enumerate(category_list):
                base_color = category_color_map[cat]
                y_pos = legend_y - (idx + 1) * legend_spacing - 0.03
                
                # Add colored square (larger for better visibility)
                fig.add_shape(
                    type="rect",
                    xref="paper", yref="paper",
                    x0=legend_x, y0=y_pos - 0.015,
                    x1=legend_x + 0.02, y1=y_pos + 0.015,
                    fillcolor=base_color,
                    line_color=base_color,
                    line_width=0
                )
                
                # Add category label with more spacing from square
                fig.add_annotation(
                    text=cat,
                    xref="paper", yref="paper",
                    x=legend_x + 0.03, y=y_pos,
                    showarrow=False,
                    font=dict(size=12, family="Inter, system-ui, sans-serif", color='#374151'),
                    xanchor='left',
                    yanchor='middle'
                )
            
        else:
            # Single category, no need for faceting
            category_data = viz_df.sort_values('Score', ascending=True)  # Ascending for horizontal bars
            
            fig = px.bar(
                category_data,
                y='Archer_Display',
                x='Score',
                orientation='h',
                title=f"Rankings - {comp_name}",
                labels={
                    'Score': 'Total Score',
                    'Archer_Display': 'Archer'
                },
                hover_data={
                    'Rank': True,
                    'Round': True,
                    'score_gap': True
                }
            )
            
            fig.update_traces(
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Rank: %{customdata[0]}<br>"
                    "Score: %{x}<br>"
                    "Round: %{customdata[1]}<br>"
                    "Gap from 1st: -%{customdata[2]} points<br>"
                    "<extra></extra>"
                )
            )
            
            single_height = max(300, len(category_data) * 40 + 100)
            fig_height_override = single_height
            custom_margin = dict(l=200, r=80, t=80, b=60)
            fig.update_layout(height=single_height)
    
    else:
        # Single category view
        filtered_df = viz_df[viz_df['Category'] == selected_category].copy()
        filtered_df = filtered_df.sort_values('Score', ascending=True)  # Ascending for horizontal bars
        
        fig = px.bar(
            filtered_df,
            y='Archer_Display',
            x='Score',
            orientation='h',
            title=f"Rankings - {selected_category} - {comp_name}",
            labels={
                'Score': 'Total Score',
                'Archer_Display': 'Archer'
            },
            hover_data={
                'Rank': True,
                'Round': True,
                'score_gap': True
            },
            color_discrete_sequence=['#1f77b4']  # Single color for single category
        )
        
        fig.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Rank: %{customdata[0]}<br>"
                "Score: %{x}<br>"
                "Round: %{customdata[1]}<br>"
                "Gap from 1st: -%{customdata[2]} points<br>"
                "<extra></extra>"
            )
        )
        
        filtered_height = max(300, len(filtered_df) * 40 + 100)
        fig_height_override = filtered_height
        custom_margin = dict(l=200, r=80, t=80, b=60)
        fig.update_layout(height=filtered_height)
    
    # Apply theme and display
    fig = apply_chart_theme(fig)
    
    # Override some chart theme settings for rankings chart specifically
    layout_overrides = dict(
        margin=custom_margin,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font_family="Inter, system-ui, sans-serif",
        hovermode="closest"
    )
    if fig_height_override is not None:
        layout_overrides["height"] = fig_height_override
    fig.update_layout(**layout_overrides)
    
    # Improve readability with consistent grid styling
    fig.update_xaxes(showgrid=True, gridcolor='#E5E7EB', gridwidth=1)
    fig.update_yaxes(showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    if len(viz_df) > 1:
        st.markdown("#### 📈 Competition Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Competitors", len(viz_df))
        with col2:
            st.metric("Categories", len(categories))
        with col3:
            highest_score = viz_df['Score'].max()
            top_archer = viz_df[viz_df['Score'] == highest_score]['Archer'].iloc[0]
            st.metric("Highest Score", f"{highest_score} ({top_archer})")
        with col4:
            avg_score = viz_df['Score'].mean()
            st.metric("Average Score", f"{avg_score:.1f}")
        
        # Show category breakdown
        st.markdown("#### 🏹 Category Breakdown")
        category_stats = viz_df.groupby('Category').agg({
            'Score': ['count', 'mean', 'max']
        }).round(1)
        
        # Flatten the multi-level column index
        category_stats.columns = ['Competitors', 'Avg Score', 'Highest Score']
        category_stats = category_stats.reset_index()
        
        st.dataframe(category_stats, use_container_width=True)