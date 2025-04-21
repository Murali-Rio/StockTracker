import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Set page config for better layout
st.set_page_config(
    page_title="Stock Market Analytics",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .top-performers {
        background-color: #e6f3ff;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .bottom-performers {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# App title with emoji and description
st.title("📊 Stock Market Analytics Dashboard")
st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h3 style='color: #666;'>Real-time Stock Performance Analysis</h3>
    </div>
    """, unsafe_allow_html=True)

# Sidebar for stock selection and options
st.sidebar.header("Options")

# Sample list of Indian stock symbols (you can expand this)
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
    "Wipro": "WIPRO.BO",
    "Asian Paints": "ASIANPAINT.BO",
    "Bajaj Finance": "BAJFINANCE.BO",
    "Larsen & Toubro": "LT.BO",
    "Maruti Suzuki": "MARUTI.BO",
    "Nestle India": "NESTLEIND.BO",
    "Sun Pharma": "SUNPHARMA.BO",
    "Titan Company": "TITAN.BO",
    "Axis Bank": "AXISBANK.BO",
    "Bajaj Finserv": "BAJAJFINSV.BO",
    "HCL Technologies": "HCLTECH.BO"
}

# Calculate performance for all stocks
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_stock_performance():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # 30-day performance
    
    performance_data = []
    for stock_name, symbol in stocks.items():
        try:
            stock = yf.Ticker(symbol)
            # Use period instead of start/end dates for more reliable data
            hist = stock.history(period="1mo")
            if not hist.empty and len(hist) > 1:
                initial_price = hist['Close'].iloc[0]
                final_price = hist['Close'].iloc[-1]
                performance = ((final_price - initial_price) / initial_price) * 100
                performance_data.append({
                    'Stock': stock_name,
                    'Symbol': symbol,
                    'Performance': performance,
                    'Current Price': final_price,
                    'Volume': hist['Volume'].mean()
                })
        except Exception as e:
            st.warning(f"Error fetching data for {stock_name}: {str(e)}")
            continue
    
    return pd.DataFrame(performance_data)

# Get and sort performance data
try:
    performance_df = get_stock_performance()
    if performance_df.empty:
        st.error("No data available. Please try again later.")
    else:
        top_10 = performance_df.nlargest(10, 'Performance')
        bottom_10 = performance_df.nsmallest(10, 'Performance')
except Exception as e:
    st.error(f"Error processing stock data: {str(e)}")
    st.stop()

# Create charts for top and bottom performers
st.markdown("### 📈 Performance Overview")
col1, col2 = st.columns(2)

with col1:
    # Top performers bar chart
    fig_top = px.bar(
        top_10,
        x='Stock',
        y='Performance',
        title='Top 10 Performers',
        color='Performance',
        color_continuous_scale='Greens',
        text='Performance',
        labels={'Performance': '30-Day Return (%)'}
    )
    fig_top.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_top.update_layout(
        xaxis_tickangle=-45,
        yaxis_title='Return (%)',
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    # Bottom performers bar chart
    fig_bottom = px.bar(
        bottom_10,
        x='Stock',
        y='Performance',
        title='Bottom 10 Performers',
        color='Performance',
        color_continuous_scale='Reds',
        text='Performance',
        labels={'Performance': '30-Day Return (%)'}
    )
    fig_bottom.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_bottom.update_layout(
        xaxis_tickangle=-45,
        yaxis_title='Return (%)',
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_bottom, use_container_width=True)

# Add a line chart showing all stocks' performance
st.markdown("### 📊 All Stocks Performance")
fig_all = px.line(
    performance_df.sort_values('Performance'),
    x='Stock',
    y='Performance',
    title='All Stocks 30-Day Performance',
    markers=True,
    labels={'Performance': 'Return (%)'}
)
fig_all.update_layout(
    xaxis_tickangle=-45,
    yaxis_title='Return (%)',
    height=500,
    showlegend=False
)
st.plotly_chart(fig_all, use_container_width=True)

# Display the dataframes below the charts
st.markdown("### 📋 Detailed Performance Data")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Top Performers")
    st.dataframe(
        top_10[['Stock', 'Performance']]
        .style
        .format({'Performance': '{:.2f}%'})
        .background_gradient(cmap='Greens')
        .set_properties(**{'text-align': 'left'})
    )

with col2:
    st.markdown("#### Bottom Performers")
    st.dataframe(
        bottom_10[['Stock', 'Performance']]
        .style
        .format({'Performance': '{:.2f}%'})
        .background_gradient(cmap='Reds')
        .set_properties(**{'text-align': 'left'})
    )

selected_stock = st.sidebar.selectbox("Select a stock", list(stocks.keys()))
stock_symbol = stocks[selected_stock]

# Time range
periods = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "YTD": "ytd",
    "Max": "max"
}
selected_period = st.sidebar.selectbox("Select period", list(periods.keys()))
analysis_period = periods[selected_period]

# Fetch stock data
try:
    stock = yf.Ticker(stock_symbol)
    # Use period parameter instead of days
    hist = stock.history(period=analysis_period)
    
    if hist.empty:
        st.error(f"No historical data available for {selected_stock}")
        st.stop()
        
    # Display basic stock info
    st.subheader(f"{selected_stock} ({stock_symbol})")

    info = stock.info
    if info:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Price", f"₹{info.get('currentPrice', 'N/A')}")
            st.metric("52-Week High", f"₹{info.get('fiftyTwoWeekHigh', 'N/A')}")
            st.metric("PE Ratio", info.get("trailingPE", 'N/A'))
        with col2:
            st.metric("Previous Close", f"₹{info.get('previousClose', 'N/A')}")
            st.metric("52-Week Low", f"₹{info.get('fiftyTwoWeekLow', 'N/A')}")
            st.metric("Market Cap", f"{round(info.get('marketCap', 0)/1e12, 2)} T INR")

    # Price chart
    st.subheader("Price History")
    fig_price = px.line(hist, y='Close', title=f'{selected_stock} Price Movement')
    fig_price.update_layout(yaxis_title="Price", xaxis_title="Date")
    st.plotly_chart(fig_price)

    # Volume chart
    st.subheader("Volume Analysis")
    fig_volume = px.bar(hist, y='Volume', title=f'{selected_stock} Trading Volume')
    fig_volume.update_layout(yaxis_title="Volume", xaxis_title="Date")
    st.plotly_chart(fig_volume)

    # Moving Average Analysis
    st.subheader("Moving Averages")
    ma_period = st.slider("Select moving average period (days)", 5, 50, 20)
    hist['MA'] = hist['Close'].rolling(window=ma_period).mean()
    fig_ma = px.line(hist, y=['Close', 'MA'], title=f'{selected_stock} {ma_period}-Day Moving Average')
    fig_ma.update_layout(yaxis_title="Price", xaxis_title="Date")
    st.plotly_chart(fig_ma)

    # Data table
    st.subheader("Raw Data")
    st.dataframe(hist.tail(20))

except Exception as e:
    st.error(f"Error retrieving data: {str(e)}")
    st.stop()

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center;'>
        <p style='color: #666; font-size: 0.8rem;'>Data updates hourly | Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
