import os
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# Get database connection string from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_engine():
    """Create and return a SQLAlchemy database engine"""
    return create_engine(DATABASE_URL)

def save_stock_performance(df, index_name, time_period):
    """
    Save stock performance data to the database

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing stock performance data
    index_name : str
        Name of the stock index (e.g., 'S&P 500', 'Dow Jones')
    time_period : str
        Time period for the analysis (e.g., '1 Day', '1 Month')
    """
    if df.empty:
        return

    # Create database connection
    engine = get_db_engine()

    # Prepare data for database insertion
    records = []
    for _, row in df.iterrows():
        # Convert Market Cap from string to numeric if it exists
        market_cap = None
        if isinstance(row['Market Cap'], str) and row['Market Cap'] != 'N/A':
            try:
                market_cap = float(row['Market Cap'].replace('$', '').replace('B', '')) * 1e9
            except ValueError:
                pass

        record = {
            'ticker': row['Ticker'],
            'company_name': row['Company'],
            'current_price': row['Current Price'],
            'price_change': row['Price Change'],
            'percent_change': row['Percent Change'],
            'volume': int(row['Volume']),
            'market_cap': market_cap,
            'index_name': index_name,
            'time_period': time_period,
            'recorded_date': datetime.now()
        }
        records.append(record)

    # Add market region
    for record in records:
        if '.NS' in record['ticker'] or '.BO' in record['ticker']:
            record['market_region'] = 'India'
        else:
            record['market_region'] = 'US'

    # Convert to DataFrame and save to database
    df_to_save = pd.DataFrame(records)
    df_to_save.to_sql('stock_performance_history', engine, if_exists='append', index=False)

def get_historical_performance(ticker, limit=30):
    """
    Retrieve historical performance data for a specific ticker

    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    limit : int, optional
        Maximum number of records to retrieve, by default 30

    Returns:
    --------
    pandas.DataFrame
        DataFrame containing historical performance data
    """
    engine = get_db_engine()

    query = text("""
        SELECT * FROM stock_performance_history
        WHERE ticker = :ticker
        ORDER BY recorded_date DESC
        LIMIT :limit
    """)

    df = pd.read_sql(query, engine, params={'ticker': ticker, 'limit': limit})
    return df

def get_top_performers_history(days=7, limit=10):
    """
    Get historical data for stocks that appeared most frequently in top performers

    Parameters:
    -----------
    days : int, optional
        Number of days to look back, by default 7
    limit : int, optional
        Maximum number of top performers to return, by default 10

    Returns:
    --------
    pandas.DataFrame
        DataFrame containing top performers history
    """
    engine = get_db_engine()

    query = text("""
        WITH top_performers AS (
            SELECT ticker, company_name, COUNT(*) as appearance_count
            FROM stock_performance_history
            WHERE percent_change > 0
            AND recorded_date > CURRENT_DATE - INTERVAL ':days days'
            GROUP BY ticker, company_name
            ORDER BY appearance_count DESC, company_name
            LIMIT :limit
        )
        SELECT tp.ticker, tp.company_name, tp.appearance_count,
               AVG(sh.percent_change) as avg_percent_change
        FROM top_performers tp
        JOIN stock_performance_history sh ON tp.ticker = sh.ticker
        WHERE sh.recorded_date > CURRENT_DATE - INTERVAL ':days days'
        GROUP BY tp.ticker, tp.company_name, tp.appearance_count
        ORDER BY tp.appearance_count DESC, avg_percent_change DESC
    """)

    df = pd.read_sql(query, engine, params={'days': days, 'limit': limit})
    return df

def get_bottom_performers_history(days=7, limit=10):
    """
    Get historical data for stocks that appeared most frequently in bottom performers

    Parameters:
    -----------
    days : int, optional
        Number of days to look back, by default 7
    limit : int, optional
        Maximum number of bottom performers to return, by default 10

    Returns:
    --------
    pandas.DataFrame
        DataFrame containing bottom performers history
    """
    engine = get_db_engine()

    query = text("""
        WITH bottom_performers AS (
            SELECT ticker, company_name, COUNT(*) as appearance_count
            FROM stock_performance_history
            WHERE percent_change < 0
            AND recorded_date > CURRENT_DATE - INTERVAL ':days days'
            GROUP BY ticker, company_name
            ORDER BY appearance_count DESC, company_name
            LIMIT :limit
        )
        SELECT bp.ticker, bp.company_name, bp.appearance_count,
               AVG(sh.percent_change) as avg_percent_change
        FROM bottom_performers bp
        JOIN stock_performance_history sh ON bp.ticker = sh.ticker
        WHERE sh.recorded_date > CURRENT_DATE - INTERVAL ':days days'
        GROUP BY bp.ticker, bp.company_name, bp.appearance_count
        ORDER BY bp.appearance_count DESC, avg_percent_change ASC
    """)

    df = pd.read_sql(query, engine, params={'days': days, 'limit': limit})
    return df