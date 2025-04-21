import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Stock Comparison",
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
    
    /* Stock cards styling */
    .stock-card {
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
</style>
""", unsafe_allow_html=True)

# Page title
st.title("📊 Stock Comparison")
st.markdown("Compare multiple stocks and analyze their performance")

# Sidebar for stock selection and options
st.sidebar.header("Comparison Options")

# Sample list of Indian stock symbols
stocks = {
    "Reliance Industries": "RELIANCE.BO",
    "Tata Consultancy Services": "TCS.BO",
    "Infosys": "INFY.BO",
    "HDFC Bank": "HDFCBANK.BO",
    "ICICI Bank": "ICICIBANK.BO",
    "Hindustan Unilever": "HINDUNILVR.BO",
    "Bharti Airtel": "BHARTIARTL.BO",
    "State Bank of India": "SBIN.BO",
    "Kotak Mahindra Bank": "KOTAKBANK.BO",
    "Wipro": "WIPRO.BO"
}

# Time period options
periods = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "YTD": "ytd",
    "Max": "max"
}

# Allow user to select multiple stocks
selected_stocks = st.sidebar.multiselect(
    "Select stocks to compare",
    list(stocks.keys()),
    default=["Reliance Industries", "Tata Consultancy Services"]
)

# Time period selection
selected_period = st.sidebar.selectbox(
    "Select time period",
    list(periods.keys()),
    index=2
)

# Get data for selected stocks
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_stock_data(symbols, period):
    data = {}
    for symbol in symbols:
        try:
            stock = yf.Ticker(stocks[symbol])
            hist = stock.history(period=periods[period])
            if not hist.empty:
                # Calculate daily returns
                hist['Daily Return'] = hist['Close'].pct_change() * 100
                data[symbol] = {
                    'data': hist,
                    'current': hist['Close'].iloc[-1],
                    'change': hist['Close'].iloc[-1] - hist['Close'].iloc[0],
                    'percent_change': ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100,
                    'high': hist['High'].max(),
                    'low': hist['Low'].min(),
                    'volume': hist['Volume'].mean()
                }
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {e}")
    return data

if selected_stocks:
    # Get data for selected stocks
    stock_data = get_stock_data(selected_stocks, selected_period)
    
    if stock_data:
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Price Comparison", "Performance Analysis", "Volume Analysis"])
        
        with tab1:
            # Price comparison chart
            fig_price = go.Figure()
            
            for symbol, data in stock_data.items():
                fig_price.add_trace(go.Scatter(
                    x=data['data'].index,
                    y=data['data']['Close'],
                    name=symbol,
                    mode='lines'
                ))
            
            fig_price.update_layout(
                title=f"Price Comparison - {selected_period}",
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                height=600
            )
            st.plotly_chart(fig_price, use_container_width=True)
            
            # Display current metrics
            st.subheader("Current Metrics")
            cols = st.columns(len(selected_stocks))
            
            for i, (symbol, data) in enumerate(stock_data.items()):
                with cols[i]:
                    st.markdown(f"### {symbol}")
                    st.metric("Current Price", f"₹{float(data['current']):.2f}")
                    st.metric("Change", f"₹{float(data['change']):.2f}", 
                             f"{float(data['percent_change']):.2f}%")
                    st.metric("High", f"₹{float(data['high']):.2f}")
                    st.metric("Low", f"₹{float(data['low']):.2f}")
        
        with tab2:
            # Performance comparison
            st.subheader("Performance Analysis")
            
            # Calculate normalized performance (starting at 100)
            fig_performance = go.Figure()
            
            for symbol, data in stock_data.items():
                normalized = (data['data']['Close'] / data['data']['Close'].iloc[0]) * 100
                fig_performance.add_trace(go.Scatter(
                    x=data['data'].index,
                    y=normalized,
                    name=symbol,
                    mode='lines'
                ))
            
            fig_performance.update_layout(
                title=f"Normalized Performance (Base 100) - {selected_period}",
                xaxis_title="Date",
                yaxis_title="Performance (Base 100)",
                height=600
            )
            st.plotly_chart(fig_performance, use_container_width=True)
            
            # Daily returns comparison
            fig_returns = go.Figure()
            
            for symbol, data in stock_data.items():
                fig_returns.add_trace(go.Box(
                    y=data['data']['Daily Return'],
                    name=symbol,
                    boxpoints='outliers'
                ))
            
            fig_returns.update_layout(
                title="Daily Returns Distribution",
                yaxis_title="Daily Return (%)",
                height=400
            )
            st.plotly_chart(fig_returns, use_container_width=True)
        
        with tab3:
            # Volume analysis
            st.subheader("Volume Analysis")
            
            # Volume comparison chart
            fig_volume = go.Figure()
            
            for symbol, data in stock_data.items():
                fig_volume.add_trace(go.Bar(
                    x=data['data'].index,
                    y=data['data']['Volume'],
                    name=symbol,
                    opacity=0.7
                ))
            
            fig_volume.update_layout(
                title=f"Trading Volume Comparison - {selected_period}",
                xaxis_title="Date",
                yaxis_title="Volume",
                height=600,
                barmode='group'
            )
            st.plotly_chart(fig_volume, use_container_width=True)
            
            # Volume statistics
            st.subheader("Volume Statistics")
            volume_data = []
            
            for symbol, data in stock_data.items():
                volume_data.append({
                    'Stock': symbol,
                    'Average Volume': f"{float(data['volume']):,.0f}",
                    'Max Volume': f"{float(data['data']['Volume'].max()):,.0f}",
                    'Min Volume': f"{float(data['data']['Volume'].min()):,.0f}"
                })
            
            st.dataframe(pd.DataFrame(volume_data), use_container_width=True)
    else:
        st.warning("No data available for the selected stocks. Please try different stocks or time period.")
else:
    st.info("Please select at least one stock to compare.")

# Footer
st.markdown("---")
