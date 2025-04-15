import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
            
            # Technical analysis section
            st.subheader("Technical Analysis")
            
            if not hist_data.empty and len(hist_data) > 14:  # Need at least 14 days for some indicators
                # Create tabs for different technical indicators
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["Moving Averages", "RSI & MACD", "Bollinger Bands", "Volume Analysis", "Performance Metrics"])
                
                with tab1:
                    # Moving averages
                    ma_periods = [5, 10, 20, 50, 200]
                    for period in ma_periods:
                        if len(hist_data) >= period:
                            hist_data[f'MA{period}'] = hist_data['Close'].rolling(window=period).mean()
                    
                    # Create figure
                    fig = go.Figure()
                    
                    # Add price
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['Close'],
                        mode='lines',
                        name='Price',
                        line=dict(color='black', width=2)
                    ))
                    
                    # Add moving averages
                    colors = ['blue', 'green', 'red', 'purple', 'orange']
                    for i, period in enumerate(ma_periods):
                        if f'MA{period}' in hist_data.columns:
                            fig.add_trace(go.Scatter(
                                x=hist_data.index,
                                y=hist_data[f'MA{period}'],
                                mode='lines',
                                name=f'{period}-day MA',
                                line=dict(color=colors[i % len(colors)])
                            ))
                    
                    fig.update_layout(
                        title="Moving Averages",
                        xaxis_title="Date",
                        yaxis_title="Price",
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add moving average crossover visualization
                    st.subheader("Moving Average Crossovers")
                    ma_short = st.selectbox("Select short-term MA", [5, 10, 20], index=0)
                    ma_long = st.selectbox("Select long-term MA", [20, 50, 200], index=1)
                    
                    if f'MA{ma_short}' in hist_data.columns and f'MA{ma_long}' in hist_data.columns:
                        # Calculate crossovers
                        hist_data['Crossover'] = hist_data[f'MA{ma_short}'] - hist_data[f'MA{ma_long}']
                        hist_data['Signal'] = np.where(hist_data['Crossover'] > 0, 1, -1)
                        
                        # Create crossover visualization
                        fig_cross = go.Figure()
                        
                        # Add MAs
                        fig_cross.add_trace(go.Scatter(
                            x=hist_data.index,
                            y=hist_data[f'MA{ma_short}'],
                            mode='lines',
                            name=f'{ma_short}-day MA',
                            line=dict(color='green', width=2)
                        ))
                        
                        fig_cross.add_trace(go.Scatter(
                            x=hist_data.index,
                            y=hist_data[f'MA{ma_long}'],
                            mode='lines',
                            name=f'{ma_long}-day MA',
                            line=dict(color='blue', width=2)
                        ))
                        
                        # Mark crossover points
                        crossover_points = hist_data.index[hist_data['Signal'].diff() != 0].tolist()
                        if len(crossover_points) > 0:
                            crossover_values = hist_data.loc[crossover_points, 'Close'].tolist()
                            
                            fig_cross.add_trace(go.Scatter(
                                x=crossover_points,
                                y=crossover_values,
                                mode='markers',
                                marker=dict(size=10, color='red', symbol='star'),
                                name='Crossover Points'
                            ))
                        
                        fig_cross.update_layout(
                            title=f"MA Crossover: {ma_short}-day vs {ma_long}-day",
                            xaxis_title="Date",
                            yaxis_title="Price",
                            height=400
                        )
                        
                        st.plotly_chart(fig_cross, use_container_width=True)
                
                with tab2:
                    # RSI
                    delta = hist_data['Close'].diff()
                    gain = delta.where(delta > 0, 0)
                    loss = -delta.where(delta < 0, 0)
                    
                    avg_gain = gain.rolling(window=14).mean()
                    avg_loss = loss.rolling(window=14).mean()
                    
                    rs = avg_gain / avg_loss
                    hist_data['RSI'] = 100 - (100 / (1 + rs))
                    
                    # MACD
                    hist_data['EMA12'] = hist_data['Close'].ewm(span=12, adjust=False).mean()
                    hist_data['EMA26'] = hist_data['Close'].ewm(span=26, adjust=False).mean()
                    hist_data['MACD'] = hist_data['EMA12'] - hist_data['EMA26']
                    hist_data['Signal'] = hist_data['MACD'].ewm(span=9, adjust=False).mean()
                    hist_data['Histogram'] = hist_data['MACD'] - hist_data['Signal']
                    
                    # Create subplot figure
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                       vertical_spacing=0.1, 
                                       subplot_titles=("RSI", "MACD"), 
                                       row_heights=[0.5, 0.5])
                    
                    # Add RSI
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['RSI'],
                        mode='lines',
                        name='RSI',
                        line=dict(color='blue', width=2)
                    ), row=1, col=1)
                    
                    # Add RSI levels
                    fig.add_trace(go.Scatter(
                        x=[hist_data.index[0], hist_data.index[-1]],
                        y=[70, 70],
                        mode='lines',
                        name='Overbought (70)',
                        line=dict(color='red', width=1, dash='dash')
                    ), row=1, col=1)
                    
                    fig.add_trace(go.Scatter(
                        x=[hist_data.index[0], hist_data.index[-1]],
                        y=[30, 30],
                        mode='lines',
                        name='Oversold (30)',
                        line=dict(color='green', width=1, dash='dash')
                    ), row=1, col=1)
                    
                    # Add MACD
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['MACD'],
                        mode='lines',
                        name='MACD',
                        line=dict(color='blue', width=2)
                    ), row=2, col=1)
                    
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['Signal'],
                        mode='lines',
                        name='Signal',
                        line=dict(color='red', width=1)
                    ), row=2, col=1)
                    
                    # Add histogram as bar chart
                    colors = ['green' if val >= 0 else 'red' for val in hist_data['Histogram']]
                    fig.add_trace(go.Bar(
                        x=hist_data.index,
                        y=hist_data['Histogram'],
                        name='Histogram',
                        marker_color=colors
                    ), row=2, col=1)
                    
                    fig.update_layout(height=600, showlegend=True)
                    
                    # Update y-axis ranges
                    fig.update_yaxes(range=[0, 100], row=1, col=1)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add RSI heatmap visualization
                    st.subheader("RSI Trend Analysis")
                    
                    # Ensure we have RSI data
                    if not hist_data['RSI'].isna().all() and len(hist_data['RSI'].dropna()) > 0:
                        # Create RSI heatmap data
                        rsi_categories = []
                        for rsi_value in hist_data['RSI'].dropna():
                            if rsi_value >= 70:
                                rsi_categories.append("Overbought")
                            elif rsi_value <= 30:
                                rsi_categories.append("Oversold")
                            elif 30 < rsi_value < 45:
                                rsi_categories.append("Bearish")
                            elif 45 <= rsi_value < 55:
                                rsi_categories.append("Neutral")
                            else:  # 55 <= rsi_value < 70
                                rsi_categories.append("Bullish")
                        
                        last_n = min(30, len(rsi_categories))  # Last 30 days or all available data
                        
                        rsi_df = pd.DataFrame({
                            'Date': hist_data.index[-last_n:].strftime('%Y-%m-%d'),
                            'RSI Value': hist_data['RSI'].values[-last_n:],
                            'Category': rsi_categories[-last_n:]
                        })
                        
                        fig_rsi_heat = px.scatter(
                            rsi_df, 
                            x='Date', 
                            y='RSI Value',
                            color='Category',
                            color_discrete_map={
                                'Overbought': 'red',
                                'Bullish': 'lightgreen',
                                'Neutral': 'yellow',
                                'Bearish': 'orange',
                                'Oversold': 'green'
                            },
                            size_max=15,
                            size=[10] * len(rsi_df),
                            title=f"RSI Trend Analysis (Last {last_n} Days)"
                        )
                        
                        fig_rsi_heat.update_layout(height=300)
                        st.plotly_chart(fig_rsi_heat, use_container_width=True)
                
                with tab3:
                    # Bollinger Bands
                    window = 20
                    hist_data['MA20'] = hist_data['Close'].rolling(window=window).mean()
                    hist_data['STD'] = hist_data['Close'].rolling(window=window).std()
                    hist_data['Upper'] = hist_data['MA20'] + (hist_data['STD'] * 2)
                    hist_data['Lower'] = hist_data['MA20'] - (hist_data['STD'] * 2)
                    
                    # Create figure
                    fig = go.Figure()
                    
                    # Add price
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['Close'],
                        mode='lines',
                        name='Price',
                        line=dict(color='black', width=2)
                    ))
                    
                    # Add Bollinger Bands
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['Upper'],
                        mode='lines',
                        name='Upper Band',
                        line=dict(color='red', width=1)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['MA20'],
                        mode='lines',
                        name='20-day MA',
                        line=dict(color='blue', width=1)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['Lower'],
                        mode='lines',
                        name='Lower Band',
                        line=dict(color='green', width=1),
                        fill='tonexty',
                        fillcolor='rgba(0, 100, 80, 0.2)'
                    ))
                    
                    fig.update_layout(
                        title="Bollinger Bands (20-day, 2 std)",
                        xaxis_title="Date",
                        yaxis_title="Price",
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calculate Bollinger Band width
                    hist_data['BBWidth'] = (hist_data['Upper'] - hist_data['Lower']) / hist_data['MA20']
                    
                    # Create Bollinger Band Width chart
                    fig_bbw = go.Figure()
                    
                    fig_bbw.add_trace(go.Scatter(
                        x=hist_data.index,
                        y=hist_data['BBWidth'],
                        mode='lines',
                        name='BB Width',
                        line=dict(color='purple', width=2)
                    ))
                    
                    fig_bbw.update_layout(
                        title="Bollinger Band Width (Volatility Indicator)",
                        xaxis_title="Date",
                        yaxis_title="Band Width",
                        height=300
                    )
                    
                    st.plotly_chart(fig_bbw, use_container_width=True)
                
                with tab4:
                    # Volume Analysis
                    
                    # Volume by price level analysis
                    price_buckets = pd.cut(hist_data['Close'], bins=10)
                    volume_by_price = hist_data.groupby(price_buckets)['Volume'].sum()
                    
                    # Convert to dataframe for plotting
                    price_volume_df = pd.DataFrame({
                        'Price Range': [str(x) for x in volume_by_price.index],
                        'Volume': volume_by_price.values
                    })
                    
                    # Create horizontal bar chart
                    fig_vol_price = px.bar(
                        price_volume_df,
                        y='Price Range',
                        x='Volume',
                        orientation='h',
                        title=f"Volume by Price Range - {selected_period}",
                        color='Volume',
                        color_continuous_scale=['lightblue', 'darkblue']
                    )
                    
                    fig_vol_price.update_layout(height=500)
                    st.plotly_chart(fig_vol_price, use_container_width=True)
                    
                    # Create candlestick with volume
                    colors = ['green' if row['Close'] >= row['Open'] else 'red' for _, row in hist_data.iterrows()]
                    
                    fig_vol = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                           vertical_spacing=0.03, 
                                           row_heights=[0.7, 0.3])
                    
                    # Add candlestick
                    fig_vol.add_trace(go.Candlestick(
                        x=hist_data.index,
                        open=hist_data['Open'],
                        high=hist_data['High'],
                        low=hist_data['Low'],
                        close=hist_data['Close'],
                        name="Price"
                    ), row=1, col=1)
                    
                    # Add volume
                    fig_vol.add_trace(go.Bar(
                        x=hist_data.index,
                        y=hist_data['Volume'],
                        marker_color=colors,
                        name="Volume"
                    ), row=2, col=1)
                    
                    fig_vol.update_layout(
                        title="Price and Volume Analysis",
                        xaxis_title="Date",
                        yaxis_title="Price",
                        xaxis_rangeslider_visible=False,
                        height=600
                    )
                    
                    fig_vol.update_yaxes(title_text="Volume", row=2, col=1)
                    
                    st.plotly_chart(fig_vol, use_container_width=True)
                
                with tab5:
                    # Performance Metrics
                    
                    # Calculate daily returns
                    hist_data['Daily Return'] = hist_data['Close'].pct_change() * 100
                    
                    # Calculate metrics
                    total_days = len(hist_data)
                    positive_days = len(hist_data[hist_data['Daily Return'] > 0])
                    negative_days = len(hist_data[hist_data['Daily Return'] < 0])
                    neutral_days = total_days - positive_days - negative_days
                    
                    avg_positive = hist_data[hist_data['Daily Return'] > 0]['Daily Return'].mean()
                    avg_negative = hist_data[hist_data['Daily Return'] < 0]['Daily Return'].mean()
                    
                    max_gain = hist_data['Daily Return'].max()
                    max_loss = hist_data['Daily Return'].min()
                    
                    volatility = hist_data['Daily Return'].std()
                    
                    # Create metrics visual
                    metrics_data = pd.DataFrame([
                        {'Metric': 'Positive Days', 'Value': positive_days, 'Percentage': positive_days/total_days*100},
                        {'Metric': 'Negative Days', 'Value': negative_days, 'Percentage': negative_days/total_days*100},
                        {'Metric': 'Neutral Days', 'Value': neutral_days, 'Percentage': neutral_days/total_days*100},
                    ])
                    
                    # Create pie chart
                    fig_pie = px.pie(
                        metrics_data, 
                        values='Value', 
                        names='Metric', 
                        title=f"Trading Days Analysis - {selected_period}",
                        color='Metric',
                        color_discrete_map={
                            'Positive Days': 'green', 
                            'Negative Days': 'red', 
                            'Neutral Days': 'gray'
                        }
                    )
                    
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    fig_pie.update_layout(height=300)
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # Create metrics table
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Average Gain on Up Days", f"{avg_positive:.2f}%", delta=f"{max_gain:.2f}% max")
                        st.metric("Daily Volatility", f"{volatility:.2f}%")
                    
                    with col2:
                        st.metric("Average Loss on Down Days", f"{avg_negative:.2f}%", delta=f"{max_loss:.2f}% max", delta_color="inverse")
                        st.metric("Total Return", f"{hist_data['Close'].iloc[-1]/hist_data['Close'].iloc[0]*100-100:.2f}%")
                    
                    # Return distribution chart
                    fig_dist = px.histogram(
                        hist_data,
                        x='Daily Return',
                        nbins=50,
                        title="Daily Return Distribution",
                        color_discrete_sequence=['lightblue']
                    )
                    
                    fig_dist.add_vline(x=0, line_width=2, line_dash="dash", line_color="black")
                    fig_dist.add_vline(x=hist_data['Daily Return'].mean(), line_width=2, line_color="green", annotation_text="Mean")
                    
                    fig_dist.update_layout(height=400)
                    st.plotly_chart(fig_dist, use_container_width=True)
            else:
                st.info("Insufficient historical data for technical analysis. Choose a longer time period.")
                
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