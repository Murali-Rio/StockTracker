import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import db_utils

# Set page configuration
st.set_page_config(
    page_title="Stock Analysis",
    page_icon="📈",
    layout="wide"
)

# Page title
st.title("📈 Individual Stock Analysis")
st.markdown("Search and analyze individual stocks with historical data")

# Sidebar filters
st.sidebar.header("Stock Selection")

# Search box for ticker input
ticker_input = st.sidebar.text_input("Enter Stock Ticker", value="AAPL").upper()

# Time period selector
time_periods = {
    "1 Week": "1wk",
    "1 Month": "1mo", 
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y"
}

selected_period = st.sidebar.selectbox(
    "Select Time Period",
    list(time_periods.keys()),
    index=3
)

# Data interval selector
intervals = ["1d", "1wk", "1mo"]
interval_names = ["Daily", "Weekly", "Monthly"]
selected_interval = st.sidebar.selectbox(
    "Select Data Interval",
    interval_names,
    index=0
)
interval = intervals[interval_names.index(selected_interval)]

# Main content
if ticker_input:
    try:
        # Get stock data from Yahoo Finance
        stock = yf.Ticker(ticker_input)
        info = stock.info
        hist_data = stock.history(period=time_periods[selected_period], interval=interval)
        
        # Display stock information
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Company name and basic info
            company_name = info.get('shortName', ticker_input)
            st.header(f"{company_name} ({ticker_input})")
            sector = info.get('sector', 'N/A')
            industry = info.get('industry', 'N/A')
            st.markdown(f"**Sector:** {sector} | **Industry:** {industry}")
        
        with col2:
            # Current price and market data
            current_price = info.get('currentPrice', hist_data['Close'].iloc[-1] if not hist_data.empty else 0)
            previous_close = info.get('previousClose', 0)
            price_change = current_price - previous_close
            percent_change = (price_change / previous_close * 100) if previous_close else 0
            
            color = "green" if price_change >= 0 else "red"
            arrow = "↑" if price_change >= 0 else "↓"
            
            st.metric(
                label="Current Price",
                value=f"${current_price:.2f}",
                delta=f"{arrow} ${abs(price_change):.2f} ({abs(percent_change):.2f}%)",
                delta_color=color.replace("green", "normal").replace("red", "inverse")
            )
            
        with col3:
            # Market cap and volume
            market_cap = info.get('marketCap', 0)
            market_cap_display = f"${market_cap/1e9:.2f}B" if market_cap else "N/A"
            
            volume = info.get('volume', 0)
            volume_display = f"{volume:,}" if volume else "N/A"
            
            st.metric(label="Market Cap", value=market_cap_display)
            st.metric(label="Volume", value=volume_display)
        
        # Price chart
        st.subheader(f"Price History - {selected_period} ({selected_interval})")
        
        if not hist_data.empty:
            # Create figure with candlestick chart
            fig = go.Figure(data=[go.Candlestick(
                x=hist_data.index,
                open=hist_data['Open'],
                high=hist_data['High'],
                low=hist_data['Low'],
                close=hist_data['Close'],
                name="Price"
            )])
            
            # Add volume as a bar chart on a secondary axis
            fig.add_trace(go.Bar(
                x=hist_data.index,
                y=hist_data['Volume'],
                name="Volume",
                yaxis="y2",
                opacity=0.3
            ))
            
            # Set up layout with secondary y-axis for volume
            fig.update_layout(
                title=f"{company_name} Stock Price",
                yaxis_title="Price ($)",
                xaxis_title="Date",
                yaxis2=dict(
                    title="Volume",
                    overlaying="y",
                    side="right",
                    showgrid=False
                ),
                height=600,
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate and display key metrics
            st.subheader("Key Metrics")
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            
            # Current period metrics
            with metrics_col1:
                st.metric(
                    label="Open",
                    value=f"${hist_data['Open'].iloc[-1]:.2f}"
                )
            with metrics_col2:
                st.metric(
                    label="High", 
                    value=f"${hist_data['High'].iloc[-1]:.2f}"
                )
            with metrics_col3:
                st.metric(
                    label="Low", 
                    value=f"${hist_data['Low'].iloc[-1]:.2f}"
                )
            with metrics_col4:
                st.metric(
                    label="Close", 
                    value=f"${hist_data['Close'].iloc[-1]:.2f}"
                )
            
            # Performance metrics
            st.subheader("Performance Metrics")
            perf_col1, perf_col2, perf_col3 = st.columns(3)
            
            # Calculate performance metrics
            period_high = hist_data['High'].max()
            period_low = hist_data['Low'].min()
            period_avg = hist_data['Close'].mean()
            period_start = hist_data['Open'].iloc[0]
            period_end = hist_data['Close'].iloc[-1]
            period_change = period_end - period_start
            period_percent = (period_change / period_start * 100) if period_start else 0
            
            with perf_col1:
                st.metric(
                    label=f"{selected_period} High", 
                    value=f"${period_high:.2f}"
                )
                st.metric(
                    label=f"{selected_period} Low", 
                    value=f"${period_low:.2f}"
                )
            
            with perf_col2:
                st.metric(
                    label=f"{selected_period} Avg. Price", 
                    value=f"${period_avg:.2f}"
                )
                st.metric(
                    label=f"{selected_period} Avg. Volume", 
                    value=f"{hist_data['Volume'].mean():,.0f}"
                )
            
            with perf_col3:
                color = "normal" if period_change >= 0 else "inverse"
                st.metric(
                    label=f"{selected_period} Change", 
                    value=f"${period_end:.2f}",
                    delta=f"${period_change:.2f} ({period_percent:.2f}%)",
                    delta_color=color
                )
            
            # Historical trends
            st.subheader("Historical Data")
            st.dataframe(hist_data, use_container_width=True)
            
            # Check if there is historical data in the database
            try:
                db_data = db_utils.get_historical_performance(ticker_input)
                
                if not db_data.empty:
                    st.subheader("Database Historical Records")
                    
                    # Create a more readable dataframe
                    display_cols = [
                        'ticker', 'current_price', 'price_change', 
                        'percent_change', 'volume', 'market_cap',
                        'index_name', 'time_period', 'recorded_date'
                    ]
                    
                    if all(col in db_data.columns for col in display_cols):
                        display_df = db_data[display_cols].copy()
                        
                        # Format the data
                        display_df = display_df.rename(columns={
                            'ticker': 'Ticker',
                            'current_price': 'Price',
                            'price_change': 'Price Change',
                            'percent_change': 'Percent Change (%)',
                            'volume': 'Volume',
                            'market_cap': 'Market Cap',
                            'index_name': 'Index',
                            'time_period': 'Time Period',
                            'recorded_date': 'Date'
                        })
                        
                        display_df['Price'] = display_df['Price'].round(2)
                        display_df['Price Change'] = display_df['Price Change'].round(2)
                        display_df['Percent Change (%)'] = display_df['Percent Change (%)'].round(2)
                        display_df['Market Cap'] = display_df['Market Cap'].apply(
                            lambda x: f"${x/1e9:.2f}B" if x else 'N/A'
                        )
                        
                        st.dataframe(display_df, use_container_width=True)
                        
                        # Create a line chart of historical price changes
                        if len(display_df) > 1:
                            chart_data = display_df.sort_values('Date')
                            
                            fig = px.line(
                                chart_data,
                                x='Date',
                                y='Price',
                                title=f"{ticker_input} Historical Price (Database Records)",
                                markers=True
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Database records found but missing expected columns.")
                else:
                    st.info("No database records found for this stock.")
            except Exception as e:
                st.warning(f"Error retrieving database records: {e}")
        else:
            st.warning("No historical data available for the selected time period.")
    except Exception as e:
        st.error(f"Error retrieving stock data: {e}")
else:
    st.warning("Please enter a valid stock ticker symbol.")

# Show app information at the bottom
st.markdown("---")
st.markdown("""
**About this page:**  
This page provides detailed analysis for individual stocks with historical price data.
Enter a stock ticker in the sidebar to analyze any publicly traded company.
""")