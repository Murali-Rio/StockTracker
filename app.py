import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os

# Import database utilities
import db_utils

# Set page configuration
st.set_page_config(
    page_title="Stock Market Performance Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
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

    h2 {
        font-size: 1.8rem;
        padding-top: 1rem;
        border-bottom: 2px solid #f0f2f6;
        padding-bottom: 0.5rem;
    }

    /* Stock cards styling */
    .stContainer {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 0.5rem;
        border: 1px solid #e6e6e6;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }

    .stContainer:hover {
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
        font-weight: bold;
    }

    /* Tab styling */
    div[data-testid="stHorizontalBlock"] {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

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

    /* Button styling */
    .stButton button {
        background-color: #1E88E5;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        background-color: #1976D2;
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0,0,0,0.1);
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

    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e6e6e6;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e6e6e6;
    }

    /* Make positive values green and negative values red */
    .positive {
        color: green !important;
        font-weight: bold;
    }

    .negative {
        color: red !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

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
    "Russell 2000": "^RUT",
    "NIFTY 50": "^NSEI",
    "BSE SENSEX": "^BSESN",
    "NIFTY Bank": "^NSEBANK"
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
auto_refresh = st.sidebar.checkbox("Auto-refresh (every minute)", value=False)
last_refresh_time = datetime.now()

@st.cache_data(ttl=60)  # Cache data for 60 seconds (1 minute)
def get_stock_data(index_symbol, period):
    try:
        # Get constituents of the selected index
        if index_symbol == "^NSEI":  # NIFTY 50
            tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "HINDUNILVR.NS", 
                      "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS", 
                      "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS", "SUNPHARMA.NS", "WIPRO.NS",
                      "NESTLEIND.NS", "TATAMOTORS.NS"]
        elif index_symbol == "^BSESN":  # BSE SENSEX
            tickers = ["RELIANCE.BO", "TCS.BO", "HDFCBANK.BO", "ICICIBANK.BO", "INFY.BO", "HINDUNILVR.BO",
                      "ITC.BO", "SBIN.BO", "BHARTIARTL.BO", "KOTAKBANK.BO", "LT.BO", "AXISBANK.BO",
                      "BAJFINANCE.BO", "ASIANPAINT.BO", "MARUTI.BO", "TITAN.BO", "SUNPHARMA.BO", "WIPRO.BO",
                      "NESTLEIND.BO", "TATAMOTORS.BO"]
        elif index_symbol == "^NSEBANK":  # NIFTY Bank
            tickers = ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", 
                      "INDUSINDBK.NS", "BANKBARODA.NS", "PNB.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS"]
        elif index_symbol == "^GSPC":  # S&P 500
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

        # Save data to database
        try:
            db_utils.save_stock_performance(top_10, selected_index, selected_period)
            db_utils.save_stock_performance(bottom_10, selected_index, selected_period)
        except Exception as e:
            st.warning(f"Could not save to database: {e}")

        # Display last updated timestamp


        # Create columns for top and bottom performers
        col1, col2 = st.columns(2)

        # Display top performers
        with col1:
            st.subheader("🚀 Top 10 Performers")

            # Create table for top performers
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

            # Create visualization tabs for top performers
            top_tabs = st.tabs(["Bar Chart", "Bubble Chart", "Polar Chart"])

            with top_tabs[0]:
                # Create bar chart visualization for top performers
                fig_top_bar = px.bar(
                    top_10, 
                    x='Ticker', 
                    y='Percent Change',
                    color='Percent Change',
                    color_continuous_scale=['red', 'green'],
                    title=f"Top 10 Performers - {selected_period}",
                    text='Percent Change',
                    hover_data=['Company', 'Current Price', 'Volume']
                )
                fig_top_bar.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                fig_top_bar.update_layout(height=400, uniformtext_minsize=8, uniformtext_mode='hide')
                st.plotly_chart(fig_top_bar, use_container_width=True)

            with top_tabs[1]:
                # Create bubble chart for top performers
                fig_top_bubble = px.scatter(
                    top_10,
                    x='Current Price',
                    y='Percent Change',
                    size='Volume',
                    size_max=60,
                    color='Percent Change',
                    color_continuous_scale=['red', 'green'],
                    hover_name='Company',
                    text='Ticker',
                    title=f"Top 10 Performers - Bubble Chart"
                )
                fig_top_bubble.update_traces(textposition='top center')
                fig_top_bubble.update_layout(height=400)
                st.plotly_chart(fig_top_bubble, use_container_width=True)

            with top_tabs[2]:
                # Create polar chart for top performers
                fig_top_polar = px.line_polar(
                    top_10, 
                    r='Percent Change', 
                    theta='Ticker',
                    color_discrete_sequence=['green'],
                    line_close=True,
                    title=f"Top 10 Performers - Polar View"
                )
                fig_top_polar.update_layout(height=400)
                st.plotly_chart(fig_top_polar, use_container_width=True)

        # Display bottom performers
        with col2:
            st.subheader("📉 Bottom 10 Performers")

            # Create table for bottom performers
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

            # Create visualization tabs for bottom performers
            bottom_tabs = st.tabs(["Bar Chart", "Bubble Chart", "Polar Chart"])

            with bottom_tabs[0]:
                # Create bar chart visualization for bottom performers
                fig_bottom_bar = px.bar(
                    bottom_10.iloc[::-1],  # Reverse to show lowest at the bottom
                    x='Ticker', 
                    y='Percent Change',
                    color='Percent Change',
                    color_continuous_scale=['red', 'green'],
                    title=f"Bottom 10 Performers - {selected_period}",
                    text='Percent Change',
                    hover_data=['Company', 'Current Price', 'Volume']
                )
                fig_bottom_bar.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                fig_bottom_bar.update_layout(height=400, uniformtext_minsize=8, uniformtext_mode='hide')
                st.plotly_chart(fig_bottom_bar, use_container_width=True)

            with bottom_tabs[1]:
                # Create bubble chart for bottom performers
                fig_bottom_bubble = px.scatter(
                    bottom_10,
                    x='Current Price',
                    y='Percent Change',
                    size='Volume',
                    size_max=60,
                    color='Percent Change',
                    color_continuous_scale=['red', 'green'],
                    hover_name='Company',
                    text='Ticker',
                    title=f"Bottom 10 Performers - Bubble Chart"
                )
                fig_bottom_bubble.update_traces(textposition='top center')
                fig_bottom_bubble.update_layout(height=400)
                st.plotly_chart(fig_bottom_bubble, use_container_width=True)

            with bottom_tabs[2]:
                # Create polar chart for bottom performers
                fig_bottom_polar = px.line_polar(
                    bottom_10, 
                    r='Percent Change', 
                    theta='Ticker',
                    color_discrete_sequence=['red'],
                    line_close=True,
                    title=f"Bottom 10 Performers - Polar View"
                )
                fig_bottom_polar.update_layout(height=400)
                st.plotly_chart(fig_bottom_polar, use_container_width=True)

        # Add details expandable section
        with st.expander("View Detailed Data"):
            # Create detailed table with all metrics
            view_data = pd.concat([top_10, bottom_10])
            if 'Market Cap Numeric' in view_data.columns:
                view_data = view_data.drop(columns=['Market Cap Numeric'])
            st.dataframe(view_data, use_container_width=True)

            # Add comparative visualizations for all stocks
            st.subheader("Comparative Analysis")

            # Create tabs for different comparative visualizations
            comp_tabs = st.tabs(["Price vs Change", "Volume Distribution", "Treemap View"])

            with comp_tabs[0]:
                # Scatter plot of price vs percent change
                fig_scatter = px.scatter(
                    view_data,
                    x='Current Price',
                    y='Percent Change',
                    color='Percent Change',
                    size='Volume',
                    hover_name='Company',
                    text='Ticker',
                    title="Stock Price vs Percent Change",
                    color_continuous_scale=['red', 'yellow', 'green']
                )
                fig_scatter.update_traces(textposition='top center')
                fig_scatter.update_layout(height=500)
                st.plotly_chart(fig_scatter, use_container_width=True)

            with comp_tabs[1]:
                # Create sunburst chart for volume distribution
                fig_sunburst = px.sunburst(
                    view_data,
                    path=['Ticker'],
                    values='Volume',
                    color='Percent Change',
                    hover_name='Company',
                    title="Trading Volume Distribution",
                    color_continuous_scale=['red', 'yellow', 'green']
                )
                fig_sunburst.update_layout(height=500)
                st.plotly_chart(fig_sunburst, use_container_width=True)

            with comp_tabs[2]:
                # Create treemap of market cap vs performance
                fig_treemap = px.treemap(
                    view_data,
                    path=['Ticker'],
                    values='Volume',
                    color='Percent Change',
                    hover_name='Company',
                    hover_data=['Current Price', 'Price Change'],
                    title="Market Overview Treemap",
                    color_continuous_scale=['red', 'yellow', 'green']
                )
                fig_treemap.update_layout(height=500)
                st.plotly_chart(fig_treemap, use_container_width=True)

# Display the stock data
display_stock_data()

# Auto-refresh mechanism
if auto_refresh:
    # Add a placeholder for the countdown timer
    countdown_placeholder = st.empty()

    # Calculate time until next refresh (1 minute from last refresh)
    next_refresh = last_refresh_time + timedelta(minutes=1)

    # Update countdown every second
    while datetime.now() < next_refresh and auto_refresh:
        time_left = (next_refresh - datetime.now()).total_seconds()
        mins, secs = divmod(int(time_left), 60)
        countdown_placeholder.markdown(f"Next refresh in: **{mins:02d}:{secs:02d}**")
        time.sleep(1)  # Update every second

        # Check if it's time to refresh
        if datetime.now() >= next_refresh:
            st.rerun()

# Show app information at the bottom
st.markdown("---")