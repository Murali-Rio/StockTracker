
import os
from sqlalchemy import create_engine, text

# Get database connection string from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

def init_db():
    """Initialize the database with required tables"""
    engine = create_engine(DATABASE_URL)
    
    # Create tables
    with engine.connect() as conn:
        conn.execute(text("""
        DROP TABLE IF EXISTS stock_performance_history;
        CREATE TABLE stock_performance_history (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(20) NOT NULL,
            company_name VARCHAR(255) NOT NULL,
            current_price DECIMAL(20, 2),
            price_change DECIMAL(20, 2),
            percent_change DECIMAL(10, 2),
            volume BIGINT,
            market_cap DECIMAL(20, 2),
            index_name VARCHAR(50) NOT NULL,
            time_period VARCHAR(50) NOT NULL,
            recorded_date TIMESTAMP NOT NULL,
            market_region VARCHAR(50)
        );
        
        CREATE INDEX IF NOT EXISTS idx_ticker ON stock_performance_history(ticker);
        """))
        conn.commit()

if __name__ == "__main__":
    init_db()
