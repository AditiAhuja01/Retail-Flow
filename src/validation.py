import os
import pandas as pd

# Define paths relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

raw_data_path = os.path.join(DATA_DIR, "raw_online_retail.csv")
clean_data_path = os.path.join(DATA_DIR, "clean_online_retail.csv")
quarantine_path = os.path.join(DATA_DIR, "quarantine_records.csv")

def clean_data():
    print("Step 1: Reading raw dataset into memory...")
    if not os.path.exists(raw_data_path):
        print(f"[ERROR] Raw data file not found at {raw_data_path}. Please run download_data.py first.")
        return

    # Read CSV. We force InvoiceNo, StockCode, and CustomerID to be read as strings to keep formatting
    df = pd.read_csv(raw_data_path, dtype={
        'InvoiceNo': str,
        'StockCode': str,
        'CustomerID': str
    }, encoding='ISO-8859-1')
    
    initial_rows = len(df)
    print(f"Loaded {initial_rows} raw rows.")

    # 1. Remove Exact Duplicate Rows
    df = df.drop_duplicates()
    duplicate_count = initial_rows - len(df)
    print(f"Dropped {duplicate_count} duplicate rows.")

    # 2. Separate Dirty Records (Missing Customer ID or Unit Price <= 0)
    # These are invalid for client tracking, so we isolate them
    is_dirty = df['CustomerID'].isnull() | (df['UnitPrice'] <= 0)
    
    df_dirty = df[is_dirty].copy()
    df_clean = df[~is_dirty].copy()

    # Save dirty records to quarantine for auditing
    if len(df_dirty) > 0:
        df_dirty.to_csv(quarantine_path, index=False)
        print(f"Quarantined {len(df_dirty)} records with missing CustomerIDs or invalid prices to: {quarantine_path}")

    # 3. Clean Text Columns (Strip whitespace and convert to UPPERCASE)
    # This prevents duplicates like "red bag" vs "RED BAG" in SQL GROUP BY queries
    df_clean['Description'] = df_clean['Description'].astype(str).str.strip().str.upper()
    df_clean['Country'] = df_clean['Country'].astype(str).str.strip().str.upper()

    # 4. Standardize Date Format
    # Converts messy date strings (e.g. 12/1/2010 8:26) to standard SQL format (YYYY-MM-DD HH:MM:SS)
    print("Standardizing transaction timestamps...")
    df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'], errors='coerce')
    
    # Drop rows if date parsing completely failed (rare)
    df_clean = df_clean.dropna(subset=['InvoiceDate'])

    # 5. Add a Return Flag
    # In this dataset, cancelled orders have a negative quantity and InvoiceNo starting with 'C'
    df_clean['is_returned'] = df_clean['InvoiceNo'].str.startswith('C', na=False).astype(int)

    # Save clean dataset
    df_clean.to_csv(clean_data_path, index=False)
    print("[SUCCESS] Data cleaning complete!")
    print(f"Clean rows saved: {len(df_clean)} (Out of {initial_rows} original rows)")

if __name__ == "__main__":
    clean_data()
