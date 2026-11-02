import os
import pandas as pd
import sqlite3

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

clean_data_path = os.path.join(DATA_DIR, "clean_online_retail.csv")
exchange_rates_path = os.path.join(DATA_DIR, "exchange_rates.txt")
db_path = os.path.join(DATA_DIR, "retailflow_data_warehouse.db")

def load_exchange_rate():
    """Reads the exchange rate we fetched from the API."""
    inr_rate = 100.0  # Default fallback rate if rate file is missing
    if os.path.exists(exchange_rates_path):
        with open(exchange_rates_path, "r") as f:
            for line in f:
                if line.startswith("INR_RATE="):
                    inr_rate = float(line.split("=")[1].strip())
    return inr_rate

def build_star_schema():
    print("Step 2: Connecting to SQLite and building Star Schema...")
    if not os.path.exists(clean_data_path):
        print(f"[ERROR] Clean data not found at {clean_data_path}. Please run validation.py first.")
        return

    # 1. Load clean CSV
    df = pd.read_csv(clean_data_path, dtype={
        'InvoiceNo': str,
        'StockCode': str,
        'CustomerID': str
    })

    # Get live exchange rate to convert values
    inr_rate = load_exchange_rate()
    print(f"Applying API Exchange Rate: 1 GBP = {inr_rate:.2f} INR")

    # Connect to SQLite (creates the database file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enforce foreign key constraints in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Drop existing tables to ensure a clean run every time
    cursor.execute("DROP TABLE IF EXISTS fact_sales;")
    cursor.execute("DROP TABLE IF EXISTS dim_customers;")
    cursor.execute("DROP TABLE IF EXISTS dim_products;")
    cursor.execute("DROP TABLE IF EXISTS dim_dates;")

    # 2. CREATE TABLE - dim_customers (Dimension Table)
    print("Creating dim_customers table...")
    cursor.execute("""
        CREATE TABLE dim_customers (
            customer_id TEXT PRIMARY KEY,
            country TEXT
        );
    """)
    # Extract unique customer profiles
    dim_cust_df = df[['CustomerID', 'Country']].drop_duplicates(subset=['CustomerID'])
    dim_cust_df.columns = ['customer_id', 'country']
    dim_cust_df.to_sql('dim_customers', conn, if_exists='append', index=False)

    # 3. CREATE TABLE - dim_products (Dimension Table)
    print("Creating dim_products table...")
    cursor.execute("""
        CREATE TABLE dim_products (
            product_code TEXT PRIMARY KEY,
            description TEXT,
            category TEXT
        );
    """)
    
    # Extract unique products
    dim_prod_df = df[['StockCode', 'Description']].drop_duplicates(subset=['StockCode'])
    dim_prod_df.columns = ['product_code', 'description']

    # Simple logic to assign a Product Category based on Description text
    def categorize_product(desc):
        desc = str(desc).upper()
        if "BAG" in desc or "BOX" in desc or "CASE" in desc:
            return "Bags & Storage"
        elif "LIGHT" in desc or "HOLDER" in desc or "CANDLE" in desc or "LANTERN" in desc or "LAMP" in desc:
            return "Lighting & Decor"
        elif "CLOCK" in desc or "FRAME" in desc or "MIRROR" in desc or "SIGN" in desc:
            return "Home Accessories"
        elif "TEA" in desc or "CUP" in desc or "MUG" in desc or "BOWL" in desc or "PLATE" in desc or "KITCHEN" in desc:
            return "Kitchen & Dining"
        else:
            return "Gifts & Novelties"

    dim_prod_df['category'] = dim_prod_df['description'].apply(categorize_product)
    dim_prod_df.to_sql('dim_products', conn, if_exists='append', index=False)

    # 4. CREATE TABLE - dim_dates (Dimension Table)
    print("Creating dim_dates table...")
    cursor.execute("""
        CREATE TABLE dim_dates (
            date_key INTEGER PRIMARY KEY,
            full_date TEXT,
            day INTEGER,
            month INTEGER,
            year INTEGER,
            quarter INTEGER,
            day_of_week TEXT
        );
    """)

    # Extract unique invoice dates, convert to date only, and build time attributes
    df['date_parsed'] = pd.to_datetime(df['InvoiceDate'])
    unique_dates = df['date_parsed'].dt.normalize().drop_duplicates()

    date_records = []
    for dt in unique_dates:
        # Date key format: YYYYMMDD (e.g. 20101201)
        date_key = int(dt.strftime('%Y%m%d'))
        date_records.append({
            'date_key': date_key,
            'full_date': dt.strftime('%Y-%m-%d'),
            'day': dt.day,
            'month': dt.month,
            'year': dt.year,
            'quarter': (dt.month - 1) // 3 + 1,
            'day_of_week': dt.strftime('%A')
        })
    dim_date_df = pd.DataFrame(date_records)
    dim_date_df.to_sql('dim_dates', conn, if_exists='append', index=False)

    # 5. CREATE TABLE - fact_sales (Fact Table)
    print("Creating fact_sales table...")
    cursor.execute("""
        CREATE TABLE fact_sales (
            sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT,
            customer_id TEXT,
            product_code TEXT,
            date_key INTEGER,
            quantity INTEGER,
            unit_price REAL,
            amount_gbp REAL,
            amount_inr REAL,
            is_returned INTEGER,
            FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
            FOREIGN KEY (product_code) REFERENCES dim_products(product_code),
            FOREIGN KEY (date_key) REFERENCES dim_dates(date_key)
        );
    """)

    # Prepare fact records
    fact_df = pd.DataFrame()
    fact_df['invoice_no'] = df['InvoiceNo']
    fact_df['customer_id'] = df['CustomerID']
    fact_df['product_code'] = df['StockCode']
    # Link date_key by formatting Date column to YYYYMMDD
    fact_df['date_key'] = df['date_parsed'].dt.strftime('%Y%m%d').astype(int)
    fact_df['quantity'] = df['Quantity']
    fact_df['unit_price'] = df['UnitPrice']
    
    # Financial metrics (net amounts)
    fact_df['amount_gbp'] = round(fact_df['quantity'] * fact_df['unit_price'], 2)
    fact_df['amount_inr'] = round(fact_df['amount_gbp'] * inr_rate, 2)
    fact_df['is_returned'] = df['is_returned']

    fact_df.to_sql('fact_sales', conn, if_exists='append', index=False)

    # 6. Optimize Database with Indexes
    # Creating indexes on join keys speeds up SQL queries significantly
    print("Creating database indexes for query performance...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fact_cust ON fact_sales(customer_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fact_prod ON fact_sales(product_code);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fact_date ON fact_sales(date_key);")
    
    conn.commit()
    conn.close()
    print("[SUCCESS] Star Schema created and tables loaded successfully!")

if __name__ == "__main__":
    build_star_schema()
