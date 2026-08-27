# Multi-Source E-Commerce ETL & Analytics Pipeline (RetailFlow-Pipeline)

## 📌 1. The Problem Statement
Retail platforms suffer significant profit margin losses due to two main challenges:
1. **High Product Return Rates (Reverse Logistics):** Identifying which product categories have defects or sizing issues, and flagging "serial returners" who abuse return policies.
2. **Poor Retention Strategies:** Understanding the customer base to separate high-value repeat buyers (VIPs) from inactive, dormant customers.

Additionally, global retail platforms struggle to evaluate net revenue when transactions span international boundaries with different currencies.

To solve this, we need an automated data engineering pipeline that ingests raw sales logs (~540,000 records) and live currency exchange rates via a REST API, validates and cleans the data, structures it into a dimensional database, and runs business analytics.

---

## 🛠️ 2. The Solution
We built a lightweight, end-to-end **Data Engineering Pipeline** using **Python, Pandas, SQLite, and Streamlit**. It pulls raw CSV transactions and live REST API exchange rates, runs a clean ETL (Extract, Transform, Load) flow, and stores them in a Star Schema Data Warehouse.

### The Pipeline Architecture
```mermaid
graph TD
    A[Raw Sales CSV File] -->|Python Pandas| C[validation.py Ingestion Engine]
    B[Live REST API exchange rates] -->|Python requests| C
    
    C -->|Sanitizes, deduplicates, formats dates| D[clean_online_retail.csv]
    C -->|Fails data quality checks| Q[quarantine_records.csv]

    D --> E[db_pipeline.py Star Schema Builder]
    E -->|Loads Relational DB| F[(retailflow_data_warehouse.db)]

    F --> H[run_analytics.py SQL Queries]
    H --> I[reports/ CSV Aggregates]
    I --> J[app.py Streamlit Dashboard]
```

### The Data Warehouse Schema (Star Schema)
To optimize analytical query performance, the flat transaction data is normalized into a relational Star Schema:

*   **`fact_sales` (Fact Table):** Contains transactional facts (`quantity`, `unit_price`, converted currency amounts `amount_inr` / `amount_gbp`) and links to dimension tables.
*   **`dim_customers` (Dimension Table):** Stores unique customer IDs and their country of origin.
*   **`dim_products` (Dimension Table):** Stores product codes, cleaned names, and categories (automatically classified using description text).
*   **`dim_dates` (Dimension Table):** Simplifies time-series grouping by storing parsed day, month, year, quarter, and day-of-week attributes.

---

## 📊 3. Key SQL Insights & Business Analytics
We run standard SQL analytical queries (using `JOIN`s, aggregations, `CASE` statements, and `CTE`s) in [`run_analytics.py`](file:///c:/Users/Aditi%20Ahuja/CV-Projects/neoretail_pipeline/src/run_analytics.py) to answer critical retail questions:

1. **Category Performance:** Which product category generates the most net revenue, and which has the highest return rate?
2. **Customer Lifetime Value (LTV):** Who are our top 10 most profitable customers?
3. **RFM Segmentation:** Grouping customers into *Champions, Lost, At-Risk,* and *Active* based on their Recency, Frequency, and Monetary metrics.

---

## 🚀 4. How to Run the Pipeline

### Step 1: Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### Step 2: Run Ingestion & Currency Conversion (Extract)
Downloads the 45MB raw transaction CSV and calls the live API for conversion rates:
```bash
python src/download_data.py
```

### Step 3: Clean & Standardize Data (Transform)
Removes duplicate rows, formats dates, strips whitespace, and isolates error records:
```bash
python src/validation.py
```

### Step 4: Build Data Warehouse Schema (Load)
Builds the relational Star Schema and loads tables with indexes:
```bash
python src/db_pipeline.py
```

### Step 5: Execute Business Analytics
Runs all SQL analytical scripts and exports metrics:
```bash
python src/run_analytics.py
```

### Step 6: Start Dashboard
Launch the visual Streamlit dashboard:
```bash
streamlit run app.py
```
