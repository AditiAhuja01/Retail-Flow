import os
import requests
import urllib.request

# Define paths relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# 1. Download the Real E-Commerce Dataset (Flat File)
DATASET_URL = "https://raw.githubusercontent.com/databricks/Spark-The-Definitive-Guide/master/data/retail-data/all/online-retail-dataset.csv"
raw_data_path = os.path.join(DATA_DIR, "raw_online_retail.csv")

print("Step 1: Downloading 45MB retail transaction dataset...")
try:
    # Set User-Agent to avoid potential blocks
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    
    urllib.request.urlretrieve(DATASET_URL, raw_data_path)
    print(f"[SUCCESS] Raw dataset downloaded successfully at: {raw_data_path}")
except Exception as e:
    print(f"[ERROR] Error downloading dataset: {e}")

# 2. Integrate Live REST API (Currency Exchange Rates)
# Since the retail dataset is a UK dataset with prices in GBP, we fetch live conversion rates
API_URL = "https://open.er-api.com/v6/latest/GBP"

print("\nStep 2: Fetching live exchange rates from REST API...")
try:
    response = requests.get(API_URL)
    data = response.json()
    
    if response.status_code == 200:
        rates = data.get("rates", {})
        inr_rate = rates.get("INR")
        usd_rate = rates.get("USD")
        print("[SUCCESS] API Connection successful!")
        print(f"Current Rates for 1 GBP:")
        print(f" - Indian Rupee (INR): Rs.{inr_rate:.2f}")
        print(f" - US Dollar (USD): ${usd_rate:.2f}")
        
        # Save exchange rate metadata for downstream pipeline use
        meta_path = os.path.join(DATA_DIR, "exchange_rates.txt")
        with open(meta_path, "w") as f:
            f.write(f"INR_RATE={inr_rate}\n")
            f.write(f"USD_RATE={usd_rate}\n")
        print(f"[SUCCESS] Saved exchange rates locally in: {meta_path}")
    else:
        print(f"[ERROR] Failed to fetch exchange rates: HTTP {response.status_code}")
except Exception as e:
    print(f"[ERROR] API connection error: {e}")
