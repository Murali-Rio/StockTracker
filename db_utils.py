from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd
import os
import time

def get_database_connection():
    try:
        # MongoDB connection settings with timeout
        MONGODB_URL = 'mongodb://localhost:27017'
        client = MongoClient(MONGODB_URL, 
                           serverSelectionTimeoutMS=5000,  # 5 second timeout
                           connectTimeoutMS=5000,
                           socketTimeoutMS=5000)
        
        # Test the connection
        client.server_info()
        
        db = client['stocktracker']
        return db, db.stock_performance_history
    except Exception as e:
        raise Exception(f"Failed to connect to MongoDB: {str(e)}. Make sure MongoDB is running.")

def save_stock_data(collection, df, period):
    try:
        # Clear previous data for this period
        collection.delete_many({'period': period})
        
        # Save new data
        records = []
        for _, row in df.iterrows():
            record = {
                'ticker': row['Ticker'],
                'current_price': float(row['Current Price']),
                'percent_change': float(row['Percent Change']),
                'volume': float(row['Volume']),
                'timestamp': datetime.now(),
                'period': period
            }
            records.append(record)
        
        if records:
            collection.insert_many(records)
            return True, f'Data saved at {datetime.now().strftime("%H:%M:%S")}'
    except Exception as e:
        return False, f'Failed to save: {str(e)}'

def get_top_performers_history(db, days=7, limit=10):
    collection = db.stock_performance_history
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get historical data for the specified period
    historical_data = list(collection.find({
        'timestamp': {
            '$gte': start_date,
            '$lte': end_date
        }
    }))
    
    if historical_data:
        df = pd.DataFrame(historical_data)
        if '_id' in df.columns:
            df = df.drop('_id', axis=1)
        
        # Group by ticker and calculate average performance
        df = df.groupby('ticker').agg({
            'percent_change': 'mean',
            'current_price': 'last',
            'volume': 'mean'
        }).reset_index()
        
        # Sort by percent_change and limit results
        df = df.nlargest(limit, 'percent_change')
        return df
    return pd.DataFrame()

def get_bottom_performers_history(db, days=7, limit=10):
    collection = db.stock_performance_history
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get historical data for the specified period
    historical_data = list(collection.find({
        'timestamp': {
            '$gte': start_date,
            '$lte': end_date
        }
    }))
    
    if historical_data:
        df = pd.DataFrame(historical_data)
        if '_id' in df.columns:
            df = df.drop('_id', axis=1)
        
        # Group by ticker and calculate average performance
        df = df.groupby('ticker').agg({
            'percent_change': 'mean',
            'current_price': 'last',
            'volume': 'mean'
        }).reset_index()
        
        # Sort by percent_change and limit results
        df = df.nsmallest(limit, 'percent_change')
        return df
    return pd.DataFrame()

def save_daily_performers(db, top_stocks, bottom_stocks):
    collection = db.daily_performers
    today = datetime.now().date()
    
    # Remove old data for today
    collection.delete_many({'date': today.isoformat()})
    
    # Save top performers
    top_records = [{
        'ticker': stock['Ticker'],
        'price': float(stock['Current Price']),
        'percent_change': float(stock['Percent Change']),
        'volume': float(stock['Volume']),
        'type': 'top',
        'date': today.isoformat()
    } for stock in top_stocks.to_dict('records')]
    
    # Save bottom performers
    bottom_records = [{
        'ticker': stock['Ticker'],
        'price': float(stock['Current Price']),
        'percent_change': float(stock['Percent Change']),
        'volume': float(stock['Volume']),
        'type': 'bottom',
        'date': today.isoformat()
    } for stock in bottom_stocks.to_dict('records')]
    
    if top_records and bottom_records:
        collection.insert_many(top_records + bottom_records)
        return True
    return False

def get_daily_performers(db, days=7):
    collection = db.daily_performers
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get performers for the date range
    performers = list(collection.find({
        'date': {
            '$gte': start_date.isoformat(),
            '$lte': end_date.isoformat()
        }
    }))
    
    return pd.DataFrame(performers) if performers else pd.DataFrame()

def auto_update_data(db, collection, symbols, period):
    while True:
        try:
            # Get current data
            data = []
            for symbol in symbols:
                stock = yf.Ticker(symbol)
                hist = stock.history(period=period)
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[0]
                    percent_change = ((current_price - prev_price) / prev_price) * 100
                    volume = hist['Volume'].iloc[-1]
                    
                    data.append({
                        'ticker': symbol.replace('.NS', ''),
                        'current_price': round(float(current_price), 2),
                        'percent_change': round(float(percent_change), 2),
                        'volume': float(volume),
                        'timestamp': datetime.now(),
                        'period': period
                    })
            
            if data:
                # Update database
                collection.delete_many({'period': period})
                collection.insert_many(data)
                print(f"Data updated at {datetime.now().strftime('%H:%M:%S')}")
            
            # Wait for 30 seconds
            time.sleep(30)
            
        except Exception as e:
            print(f"Update failed: {str(e)}")
            time.sleep(30)  # Wait before retrying