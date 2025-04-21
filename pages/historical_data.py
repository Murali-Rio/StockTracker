import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import db_utils

# Set page configuration
st.set_page_config(
    page_title="Historical Data",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main page styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #1E88E5;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    h1 {
        background: linear-gradient(to right, #1E88E5, #42A5F5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
        padding: 0 1rem;
        font-size: 1rem;
    }
    
    /* Active tab styling */
    .stTabs [aria-selected="true"] {
        background-color: #e6f3ff !important;
        font-weight: bold;
    }
    
    /* Divider styling */
    hr {
        margin-top: 2rem;
        margin-bottom: 2rem;
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0));
    }
    
    /* Footer styling */
    footer {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #f0f2f6;
        text-align: center;
        font-size: 0.8rem;
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

# This is already handled by the earlier set_page_config

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
    # Get database connection
    db, _ = db_utils.get_database_connection()
    
    # Get historical top performers
    top_performers = db_utils.get_top_performers_history(db, days=lookback_days, limit=num_stocks)
    
    if not top_performers.empty:
        # Create visualization tabs
        top_viz_tabs = st.tabs(["Bar Chart", "Radar Chart", "Bubble Chart"])
        
        with top_viz_tabs[0]:
            # Bar chart
            fig_top_bar = px.bar(
                top_performers,
                x='ticker',
                y='percent_change',
                color='percent_change',
                color_continuous_scale=['red', 'green'],
                title=f"Top Performers Over the Last {lookback_days} Days",
                hover_data=['current_price', 'volume'],
                text='percent_change'
            )
            fig_top_bar.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig_top_bar.update_layout(height=500)
            st.plotly_chart(fig_top_bar, use_container_width=True)
            
        with top_viz_tabs[1]:
            # Radar chart
            fig_top_radar = px.line_polar(
                top_performers,
                r='percent_change',
                theta='ticker',
                color_discrete_sequence=['green'],
                line_close=True,
                title=f"Top Performers Radar - Last {lookback_days} Days",
                hover_data=['current_price', 'volume']
            )
            fig_top_radar.update_layout(height=500)
            st.plotly_chart(fig_top_radar, use_container_width=True)
            
        with top_viz_tabs[2]:
            # Bubble chart
            fig_top_bubble = px.scatter(
                top_performers,
                x='ticker',
                y='percent_change',
                size='volume',
                color='percent_change',
                hover_data=['current_price'],
                size_max=60,
                color_continuous_scale=['red', 'green'],
                title=f"Top Performers Bubble Chart - Size represents trading volume"
            )
            fig_top_bubble.update_layout(height=500)
            st.plotly_chart(fig_top_bubble, use_container_width=True)
        
        # Display data table
        top_performers = top_performers.rename(columns={
            'ticker': 'Ticker',
            'percent_change': 'Percent Change (%)',
            'current_price': 'Current Price',
            'volume': 'Volume'
        })
        top_performers['Percent Change (%)'] = top_performers['Percent Change (%)'].round(2)
        st.dataframe(top_performers, use_container_width=True)
    else:
        st.info("No historical data available for top performers. Run the app for a few days to collect data.")
        
    # Add spacing
    st.markdown("---")
    
    # Get historical bottom performers
    st.header("Historical Bottom Performers")
    bottom_performers = db_utils.get_bottom_performers_history(db, days=lookback_days, limit=num_stocks)
    
    if not bottom_performers.empty:
        # Create visualization tabs
        bottom_viz_tabs = st.tabs(["Bar Chart", "Radar Chart", "Bubble Chart"])
        
        with bottom_viz_tabs[0]:
            # Bar chart
            fig_bottom_bar = px.bar(
                bottom_performers,
                x='ticker',
                y='percent_change',
                color='percent_change',
                color_continuous_scale=['red', 'green'],
                title=f"Bottom Performers Over the Last {lookback_days} Days",
                hover_data=['current_price', 'volume'],
                text='percent_change'
            )
            fig_bottom_bar.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig_bottom_bar.update_layout(height=500)
            st.plotly_chart(fig_bottom_bar, use_container_width=True)
            
        with bottom_viz_tabs[1]:
            # Radar chart
            fig_bottom_radar = px.line_polar(
                bottom_performers,
                r='percent_change',
                theta='ticker',
                color_discrete_sequence=['red'],
                line_close=True,
                title=f"Bottom Performers Radar - Last {lookback_days} Days",
                hover_data=['current_price', 'volume']
            )
            fig_bottom_radar.update_layout(height=500)
            st.plotly_chart(fig_bottom_radar, use_container_width=True)
            
        with bottom_viz_tabs[2]:
            # Bubble chart
            fig_bottom_bubble = px.scatter(
                bottom_performers,
                x='ticker',
                y='percent_change',
                size='volume',
                color='percent_change',
                hover_data=['current_price'],
                size_max=60,
                color_continuous_scale=['red', 'green'],
                title=f"Bottom Performers Bubble Chart - Size represents trading volume"
            )
            fig_bottom_bubble.update_layout(height=500)
            st.plotly_chart(fig_bottom_bubble, use_container_width=True)
        
        # Display data table
        bottom_performers = bottom_performers.rename(columns={
            'ticker': 'Ticker',
            'percent_change': 'Percent Change (%)',
            'current_price': 'Current Price',
            'volume': 'Volume'
        })
        bottom_performers['Percent Change (%)'] = bottom_performers['Percent Change (%)'].round(2)
        st.dataframe(bottom_performers, use_container_width=True)
    else:
        st.info("No historical data available for bottom performers. Run the app for a few days to collect data.")

except Exception as e:
    st.error(f"Error retrieving historical data: {e}")

# Show app information at the bottom
st.markdown("---")
