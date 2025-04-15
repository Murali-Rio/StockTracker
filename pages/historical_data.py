import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import db_utils

# Set page configuration
st.set_page_config(
    page_title="Stock Performance History",
    page_icon="📊",
    layout="wide"
)

# Page title
st.title("📊 Stock Performance History")
st.markdown("View historical performance data for stocks from the database")

# Sidebar filters
st.sidebar.header("Historical Data Filters")

# Add lookback period filter
lookback_days = st.sidebar.slider(
    "Lookback Period (Days)",
    min_value=1,
    max_value=30,
    value=7,
    step=1
)

# Add number of stocks to display
num_stocks = st.sidebar.slider(
    "Number of Stocks to Display",
    min_value=5,
    max_value=20,
    value=10,
    step=1
)

# Main content
st.header("Historical Top Performers")

try:
    # Get historical top performers
    top_performers = db_utils.get_top_performers_history(days=lookback_days, limit=num_stocks)
    
    if not top_performers.empty:
        # Create visualization tabs
        top_viz_tabs = st.tabs(["Bar Chart", "Radar Chart", "Bubble Chart"])
        
        with top_viz_tabs[0]:
            # Bar chart
            fig_top_bar = px.bar(
                top_performers,
                x='ticker',
                y='avg_percent_change',
                color='avg_percent_change',
                color_continuous_scale=['red', 'green'],
                title=f"Top Performers Over the Last {lookback_days} Days",
                hover_data=['company_name', 'appearance_count'],
                text='avg_percent_change'
            )
            fig_top_bar.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig_top_bar.update_layout(height=500)
            st.plotly_chart(fig_top_bar, use_container_width=True)
            
        with top_viz_tabs[1]:
            # Radar chart
            fig_top_radar = px.line_polar(
                top_performers,
                r='avg_percent_change',
                theta='ticker',
                color='avg_percent_change',
                color_continuous_scale=['red', 'green'],
                line_close=True,
                title=f"Top Performers Radar - Last {lookback_days} Days",
                hover_name='company_name'
            )
            fig_top_radar.update_layout(height=500)
            st.plotly_chart(fig_top_radar, use_container_width=True)
            
        with top_viz_tabs[2]:
            # Bubble chart
            fig_top_bubble = px.scatter(
                top_performers,
                x='ticker',
                y='avg_percent_change',
                size='appearance_count',
                color='avg_percent_change',
                hover_name='company_name',
                size_max=60,
                color_continuous_scale=['red', 'green'],
                title=f"Top Performers Bubble Chart - Size represents frequency of appearance"
            )
            fig_top_bubble.update_layout(height=500)
            st.plotly_chart(fig_top_bubble, use_container_width=True)
        
        # Display data table
        top_performers = top_performers.rename(columns={
            'ticker': 'Ticker',
            'company_name': 'Company',
            'appearance_count': 'Appearances in Top List',
            'avg_percent_change': 'Avg. Percent Change (%)'
        })
        top_performers['Avg. Percent Change (%)'] = top_performers['Avg. Percent Change (%)'].round(2)
        st.dataframe(top_performers, use_container_width=True)
    else:
        st.info("No historical data available for top performers. Run the app for a few days to collect data.")
        
    # Add spacing
    st.markdown("---")
    
    # Get historical bottom performers
    st.header("Historical Bottom Performers")
    bottom_performers = db_utils.get_bottom_performers_history(days=lookback_days, limit=num_stocks)
    
    if not bottom_performers.empty:
        # Create visualization tabs
        bottom_viz_tabs = st.tabs(["Bar Chart", "Radar Chart", "Bubble Chart"])
        
        with bottom_viz_tabs[0]:
            # Bar chart
            fig_bottom_bar = px.bar(
                bottom_performers,
                x='ticker',
                y='avg_percent_change',
                color='avg_percent_change',
                color_continuous_scale=['red', 'green'],
                title=f"Bottom Performers Over the Last {lookback_days} Days",
                hover_data=['company_name', 'appearance_count'],
                text='avg_percent_change'
            )
            fig_bottom_bar.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig_bottom_bar.update_layout(height=500)
            st.plotly_chart(fig_bottom_bar, use_container_width=True)
            
        with bottom_viz_tabs[1]:
            # Radar chart
            fig_bottom_radar = px.line_polar(
                bottom_performers,
                r='avg_percent_change',
                theta='ticker',
                color='avg_percent_change',
                color_continuous_scale=['red', 'green'],
                line_close=True,
                title=f"Bottom Performers Radar - Last {lookback_days} Days",
                hover_name='company_name'
            )
            fig_bottom_radar.update_layout(height=500)
            st.plotly_chart(fig_bottom_radar, use_container_width=True)
            
        with bottom_viz_tabs[2]:
            # Bubble chart
            fig_bottom_bubble = px.scatter(
                bottom_performers,
                x='ticker',
                y='avg_percent_change',
                size='appearance_count',
                color='avg_percent_change',
                hover_name='company_name',
                size_max=60,
                color_continuous_scale=['red', 'green'],
                title=f"Bottom Performers Bubble Chart - Size represents frequency of appearance"
            )
            fig_bottom_bubble.update_layout(height=500)
            st.plotly_chart(fig_bottom_bubble, use_container_width=True)
        
        # Display data table
        bottom_performers = bottom_performers.rename(columns={
            'ticker': 'Ticker',
            'company_name': 'Company',
            'appearance_count': 'Appearances in Bottom List',
            'avg_percent_change': 'Avg. Percent Change (%)'
        })
        bottom_performers['Avg. Percent Change (%)'] = bottom_performers['Avg. Percent Change (%)'].round(2)
        st.dataframe(bottom_performers, use_container_width=True)
    else:
        st.info("No historical data available for bottom performers. Run the app for a few days to collect data.")

except Exception as e:
    st.error(f"Error retrieving historical data: {e}")

# Show app information at the bottom
st.markdown("---")
st.markdown("""
**About this page:**  
This page shows historical stock performance data that is collected and stored in the database.
The data is updated each time the main page refreshes or when you manually trigger a refresh.
""")