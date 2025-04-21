
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB connection string from environment variables
MONGODB_URL = os.environ.get('MONGODB_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'stocktracker')

def init_db():
    """Initialize the MongoDB database with required collections"""
    client = MongoClient(MONGODB_URL)
    db = client[DB_NAME]
    
    # Drop existing collection if it exists
    if 'stock_performance_history' in db.list_collection_names():
        db.drop_collection('stock_performance_history')
    
    # Create collection
    collection = db.create_collection('stock_performance_history')
    
    # Create index on ticker field
    collection.create_index('ticker')
    
    print(f"MongoDB database '{DB_NAME}' initialized successfully!")

if __name__ == "__main__":
    init_db()
