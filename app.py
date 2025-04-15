import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time

# Set page configuration
st.set_page_config(
    page_title="Stock Market Performance Tracker",
    page_icon="📈",
    layout="wide"
)

# Page title
st.title("📈 Stock Market Performance Tracker")
st.markdown("Track the top and bottom performing stocks with real-time data")

# Sidebar for filters and controls
st.sidebar.header("Filters & Controls")

# Default indices to get stock list
market_indices = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "Russell 2000": "^RUT"
}

selected_index = st.sidebar.selectbox(
    "Select Market Index", 
    list(market_indices.keys()),
    index=0
)

# Time period for analysis
period_options = {
    "1 Day": "1d",
    "5 Days": "5d",
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y"
}

selected_period = st.sidebar.selectbox(
    "Select Time Period", 
    list(period_options.keys()),
    index=2
)

# Metrics to sort by
sort_metric = st.sidebar.selectbox(
    "Sort Stocks By",
    ["Percent Change", "Price Change", "Volume", "Market Cap"],
    index=0
)

# Manual refresh button
if st.sidebar.button("Refresh Data"):
    st.rerun()

# Auto-refresh option
auto_refresh = st.sidebar.checkbox("Auto-refresh (daily)", value=False)
last_refresh_time = datetime.now()

@st.cache_data(ttl=86400)  # Cache data for 24 hours (daily)
def get_stock_data(index_symbol, period):
    try:
        # Get constituents of the selected index
        if index_symbol == "^GSPC":  # S&P 500
            # For S&P 500, we'll get a list of top companies by market cap
            tickers = ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "BRK-B", "UNH", "XOM", 
                      "TSLA", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "KO", "PEP", "AVGO",
                      "COST", "LLY", "BAC", "TMO", "MCD", "ABT", "CSCO", "ACN", "DIS", "ADBE", "WMT",
                      "CRM", "DHR", "PFE", "VZ", "NEE", "TXN", "PM", "CMCSA", "NFLX", "AMD", "ORCL",
                      "NKE", "RTX", "HON", "UPS", "IBM", "QCOM", "LOW", "INTC", "CAT", "AMGN", "SPGI",
                      "DE", "AXP", "INTU", "GE", "BA", "AMAT", "BKNG", "SBUX", "MDLZ", "ADI", "LMT",
                      "MMC", "GS", "TJX", "MS", "GILD", "BLK", "C", "ISRG", "SYK", "BMY", "REGN",
                      "EOG", "COP", "MO", "VRTX", "TMUS", "CB", "SO", "AMT", "NOC", "ZTS", "DUK",
                      "SLB", "PLD", "APD", "BSX", "CME", "WM", "SCHW", "ETN", "CL", "CSX"]
        elif index_symbol == "^DJI":  # Dow Jones
            tickers = ["AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "DOW", 
                      "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", 
                      "MRK", "MSFT", "NKE", "PG", "TRV", "UNH", "V", "VZ", "WBA", "WMT"]
        elif index_symbol == "^IXIC":  # NASDAQ
            # For NASDAQ, we'll get a list of top companies
            tickers = ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "COST", 
                      "ADBE", "CSCO", "PEP", "CMCSA", "NFLX", "AMD", "TMUS", "INTC", "INTU", "AMAT", 
                      "BKNG", "AMGN", "ADI", "ISRG", "REGN", "VRTX", "MDLZ", "SBUX", "ABNB", "KLAC", 
                      "GILD", "PYPL", "LRCX", "PANW", "SNPS", "MRVL", "CDNS", "ASML", "CTAS", "MU", 
                      "NXPI", "DXCM", "CRWD", "FTNT", "MELI", "WDAY", "ADSK", "PCAR", "MNST", "ADP"]
        else:  # Russell 2000 - just get a sample of small caps
            tickers = ["APPF", "PLMR", "HCCI", "TRNS", "BRC", "ICFI", "SPSC", "MOD", "CRAI", "TWNK", 
                      "SAFT", "SPWH", "SMP", "PLUS", "PACW", "NTGR", "MGPI", "PRGS", "CCOI", "COHU", 
                      "CNXN", "FELE", "ITIC", "CWT", "SCSC", "MLAB", "CASS", "KMPR", "CTRL", "AAON",
                      "HOPE", "UCBI", "HBNC", "BOOM", "GIII", "UNFI", "MNRO", "NWBI", "MTRX", "AMSF", 
                      "PRAA", "ANIK", "DIOD", "CYBE", "FORR", "BCOR", "BHE", "CRVL", "PATK", "SCS"]
        
        # Download data for selected period
        data = yf.download(tickers, period=period_options[period], group_by='ticker')
        
        # Prepare DataFrame for analysis
        stock_data = []
        
        for ticker in tickers:
            try:
                # Get current and previous close prices
                ticker_data = data[ticker]
                current_price = ticker_data['Close'].iloc[-1]
                previous_price = ticker_data['Close'].iloc[0]
                
                # Calculate change metrics
                price_change = current_price - previous_price
                percent_change = (price_change / previous_price) * 100
                
                # Get volume (average over the period)
                volume = ticker_data['Volume'].mean()
                
                # Get additional info
                ticker_info = yf.Ticker(ticker).info
                company_name = ticker_info.get('shortName', ticker)
                market_cap = ticker_info.get('marketCap', 0)
                
                stock_data.append({
                    'Ticker': ticker,
                    'Company': company_name,
                    'Current Price': current_price,
                    'Price Change': price_change,
                    'Percent Change': percent_change,
                    'Volume': volume,
                    'Market Cap': market_cap
                })
            except Exception as e:
                continue  # Skip tickers with issues
        
        return pd.DataFrame(stock_data)
    
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return pd.DataFrame()

# Main function to display stock data
def display_stock_data():
    global last_refresh_time
    
    with st.spinner("Fetching latest stock data..."):
        # Get stock data
        df = get_stock_data(market_indices[selected_index], selected_period)
        
        if df.empty:
            st.warning("No data available. Please try another index or check your connection.")
            return
        
        # Format the data
        df['Current Price'] = df['Current Price'].round(2)
        df['Price Change'] = df['Price Change'].round(2)
        df['Percent Change'] = df['Percent Change'].round(2)
        df['Volume'] = df['Volume'].astype(int)
        df['Market Cap'] = df['Market Cap'].apply(lambda x: f"${x/1e9:.2f}B" if x else "N/A")
        
        # Sort based on selected metric
        sort_col = {
            "Percent Change": "Percent Change",
            "Price Change": "Price Change",
            "Volume": "Volume",
            "Market Cap": "Market Cap"
        }[sort_metric]
        
        if sort_col == "Market Cap":
            # Convert Market Cap back to numeric for sorting
            df['Market Cap Numeric'] = df['Market Cap'].apply(
                lambda x: float(x.replace('$', '').replace('B', '')) if x != "N/A" else 0
            )
            sort_col = "Market Cap Numeric"
        
        # Sort and get top/bottom performers
        df_sorted = df.sort_values(by=sort_col, ascending=False)
        top_10 = df_sorted.head(10).copy()
        bottom_10 = df_sorted.tail(10).copy()
        
        # Display last updated timestamp
        last_refresh_time = datetime.now()
        st.write(f"Last updated: {last_refresh_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create columns for top and bottom performers
        col1, col2 = st.columns(2)
        
        # Display top performers
        with col1:
            st.subheader("🚀 Top 10 Performers")
            for i, row in top_10.iterrows():
                with st.container():
                    cols = st.columns([3, 2, 2, 2])
                    with cols[0]:
                        st.markdown(f"**{row['Company']}** ({row['Ticker']})")
                    with cols[1]:
                        st.markdown(f"**${row['Current Price']}**")
                    with cols[2]:
                        color = "green" if row['Percent Change'] > 0 else "red"
                        arrow = "↑" if row['Percent Change'] > 0 else "↓"
                        st.markdown(f"<span style='color:{color}'>{arrow} {abs(row['Percent Change']):.2f}%</span>", unsafe_allow_html=True)
                    with cols[3]:
                        st.markdown(f"Vol: {row['Volume']:,}")
                    st.divider()
            
            # Create visualization for top performers
            fig_top = px.bar(
                top_10, 
                x='Ticker', 
                y='Percent Change',
                color='Percent Change',
                color_continuous_scale=['red', 'green'],
                title=f"Top 10 Performers - {selected_period}"
            )
            fig_top.update_layout(height=400)
            st.plotly_chart(fig_top, use_container_width=True)
        
        # Display bottom performers
        with col2:
            st.subheader("📉 Bottom 10 Performers")
            for i, row in bottom_10.iterrows():
                with st.container():
                    cols = st.columns([3, 2, 2, 2])
                    with cols[0]:
                        st.markdown(f"**{row['Company']}** ({row['Ticker']})")
                    with cols[1]:
                        st.markdown(f"**${row['Current Price']}**")
                    with cols[2]:
                        color = "green" if row['Percent Change'] > 0 else "red"
                        arrow = "↑" if row['Percent Change'] > 0 else "↓"
                        st.markdown(f"<span style='color:{color}'>{arrow} {abs(row['Percent Change']):.2f}%</span>", unsafe_allow_html=True)
                    with cols[3]:
                        st.markdown(f"Vol: {row['Volume']:,}")
                    st.divider()
            
            # Create visualization for bottom performers
            fig_bottom = px.bar(
                bottom_10.iloc[::-1],  # Reverse to show lowest at the bottom
                x='Ticker', 
                y='Percent Change',
                color='Percent Change',
                color_continuous_scale=['red', 'green'],
                title=f"Bottom 10 Performers - {selected_period}"
            )
            fig_bottom.update_layout(height=400)
            st.plotly_chart(fig_bottom, use_container_width=True)
        
        # Add details expandable section
        with st.expander("View Detailed Data"):
            # Create detailed table with all metrics
            view_data = pd.concat([top_10, bottom_10])
            if 'Market Cap Numeric' in view_data.columns:
                view_data = view_data.drop(columns=['Market Cap Numeric'])
            st.dataframe(view_data, use_container_width=True)

# Display the stock data
display_stock_data()

# Auto-refresh mechanism
if auto_refresh:
    # Add a placeholder for the countdown timer
    countdown_placeholder = st.empty()
    
    # Calculate time until next refresh (24 hours from last refresh)
    next_refresh = last_refresh_time + timedelta(hours=24)
    
    # Update countdown every minute
    while datetime.now() < next_refresh and auto_refresh:
        time_left = (next_refresh - datetime.now()).total_seconds()
        hours, remainder = divmod(int(time_left), 3600)
        mins, secs = divmod(remainder, 60)
        countdown_placeholder.markdown(f"Next refresh in: **{hours:02d}:{mins:02d}:{secs:02d}**")
        time.sleep(60)  # Update every minute instead of every second
        
        # Check if it's time to refresh
        if datetime.now() >= next_refresh:
            st.rerun()

# Show app information at the bottom
st.markdown("---")
st.markdown("""
**About this app:**  
This application displays real-time stock performance data using Yahoo Finance API.
Data is refreshed daily when auto-refresh is enabled, or you can manually refresh using the button.
""")
