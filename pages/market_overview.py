import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Market Overview",
    page_icon="🌎",
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
    
    /* Stock cards styling */
    div[data-testid="stHorizontalBlock"] {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.3rem;
        font-weight: bold;
    }
    
    div[data-testid="stMetricDelta"] {
        font-size: 1rem;
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
import time

# This is already handled by the earlier set_page_config declaration

# Page title
st.title("🌎 Market Overview")
st.markdown("Track major market indices and their performance")

# Sidebar for filters and controls
st.sidebar.header("Market Filters")

# Time period for analysis
period_options = {
    "1 Day": "1d",
    "5 Days": "5d",
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y"
}

selected_period = st.sidebar.selectbox(
    "Select Time Period", 
    list(period_options.keys()),
    index=3
)

# Data interval
intervals = ["1d", "1wk", "1mo"]
interval_names = ["Daily", "Weekly", "Monthly"]
selected_interval = st.sidebar.selectbox(
    "Select Data Interval",
    interval_names,
    index=0
)
interval = intervals[interval_names.index(selected_interval)]

# Manual refresh button
if st.sidebar.button("Refresh Data"):
    st.rerun()

# Get major market indices data
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_indices_data(period, interval):
    # List of major market indices
    indices = {
        "S&P 500": "^GSPC",
        "Dow Jones": "^DJI",
        "NASDAQ": "^IXIC",
        "Russell 2000": "^RUT",
        "VIX Volatility": "^VIX",
        "FTSE 100": "^FTSE",
        "Nikkei 225": "^N225",
        "Hang Seng": "^HSI",
        "DAX": "^GDAXI"
    }
    
    # Get data for all indices
    data = {}
    for name, symbol in indices.items():
        try:
            df = yf.download(symbol, period=period, interval=interval)
            if not df.empty:
                # Calculate daily returns
                df['Daily Return'] = df['Close'].pct_change() * 100
                data[name] = {
                    'symbol': symbol,
                    'data': df,
                    'current': df['Close'].iloc[-1],
                    'change': df['Close'].iloc[-1] - df['Close'].iloc[0],
                    'percent_change': ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100,
                    'high': df['High'].max(),
                    'low': df['Low'].min()
                }
        except Exception as e:
            st.error(f"Error fetching data for {name}: {e}")
    
    return data

# Global indices data
indices_data = get_indices_data(period_options[selected_period], interval)

# Display indices overview
st.header("Major Market Indices")

if indices_data:
    # Create a heatmap of market performance
    heatmap_data = []
    for name, data in indices_data.items():
        heatmap_data.append({
            'Index': name,
            'Current Value': data['current'],
            'Change': data['change'],
            'Percent Change': data['percent_change']
        })
    
    heatmap_df = pd.DataFrame(heatmap_data)
    
    # Create heatmap with plotly
    fig_heatmap = px.imshow(
        heatmap_df.set_index('Index')[['Percent Change']].T,
        color_continuous_scale=['red', 'white', 'green'],
        labels=dict(x="Index", y="Metric", color="Value"),
        title="Global Market Performance Heatmap"
    )
    fig_heatmap.update_layout(height=200)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Create a matrix of metrics
    col1, col2, col3 = st.columns(3)
    
    for i, (name, data) in enumerate(indices_data.items()):
        # Determine which column to use
        col = [col1, col2, col3][i % 3]
        
        # Determine color based on change
        delta_color = "normal" if float(data['change'].iloc[0]) >= 0 else "inverse"
        
        # Display metric
        with col:
            current_val = float(data['current'])
            change_val = float(data['change'])
            percent_val = float(data['percent_change'])
            
            delta_color = "normal" if change_val >= 0 else "inverse"
            st.metric(
                label=name,
                value=f"{current_val:.2f}",
                delta=f"{change_val:.2f} ({percent_val:.2f}%)",
                delta_color=delta_color
            )
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Price Charts", "Performance Comparison", "Volatility Analysis"])
    
    with tab1:
        # Price charts for each index
        selected_index = st.selectbox(
            "Select Market Index to View",
            list(indices_data.keys())
        )
        
        if selected_index in indices_data:
            index_data = indices_data[selected_index]
            df = index_data['data']
            
            # Create chart
            fig = go.Figure()
            
            # Add price line
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='royalblue', width=2)
            ))
            
            # Add volume as bar chart
            fig.add_trace(go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                yaxis='y2',
                marker=dict(color='lightgray', opacity=0.5)
            ))
            
            # Update layout
            fig.update_layout(
                title=f"{selected_index} ({index_data['symbol']}) - {selected_period}",
                xaxis_title='Date',
                yaxis_title='Price',
                hovermode='x unified',
                yaxis2=dict(
                    title='Volume',
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display performance metrics
            st.subheader(f"{selected_index} Performance Metrics")
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            
            with metrics_col1:
                st.metric("High", f"{index_data['high']:.2f}")
            with metrics_col2:
                st.metric("Low", f"{index_data['low']:.2f}")
            with metrics_col3:
                st.metric("Current", f"{index_data['current']:.2f}")
            with metrics_col4:
                st.metric("Change %", f"{index_data['percent_change']:.2f}%")
    
    with tab2:
        # Performance comparison of all indices
        st.subheader("Comparative Performance")
        
        # Prepare data for comparison
        comparison_data = []
        for name, data in indices_data.items():
            df = data['data']
            
            # Normalize to starting value = 100
            normalized_series = (df['Close'] / df['Close'].iloc[0]) * 100
            
            for date, value in zip(normalized_series.index, normalized_series.values):
                comparison_data.append({
                    'Date': date,
                    'Index': name,
                    'Normalized Value': value
                })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            
            # Create comparison chart
            fig = px.line(
                comparison_df,
                x='Date',
                y='Normalized Value',
                color='Index',
                title=f"Normalized Performance Comparison (Starting Value = 100) - {selected_period}",
                labels={'Normalized Value': 'Performance (Base 100)'}
            )
            
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
        
    with tab3:
        # Volatility analysis
        st.subheader("Market Volatility Analysis")
        
        # Prepare volatility data
        volatility_data = []
        for name, data in indices_data.items():
            df = data['data']
            volatility = df['Daily Return'].std()
            
            volatility_data.append({
                'Index': name,
                'Volatility (%)': volatility,
                'Avg Daily Change (%)': df['Daily Return'].mean(),
                'Max Daily Gain (%)': df['Daily Return'].max(),
                'Max Daily Loss (%)': df['Daily Return'].min()
            })
        
        if volatility_data:
            volatility_df = pd.DataFrame(volatility_data)
            
            # Create volatility chart
            fig = px.bar(
                volatility_df.sort_values('Volatility (%)'),
                x='Index',
                y='Volatility (%)',
                title=f"Market Volatility - {selected_period}",
                color='Volatility (%)',
                color_continuous_scale=['green', 'yellow', 'red']
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display volatility data table
            st.dataframe(volatility_df, use_container_width=True)
else:
    st.warning("No market data available. Please check your connection or try a different time period.")

# Show app information at the bottom
st.markdown("---")
st.markdown("""
**About this page:**  
This page provides an overview of major market indices worldwide and their performance.
Compare different indices and analyze market trends across various time periods.
""")