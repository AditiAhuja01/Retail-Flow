# RetailFlow

An automated batch ETL pipeline and dimensional data warehouse that processes 540,000+ transaction records, normalizes international sales to INR via live Forex REST API, and delivers net revenue and customer retention analytics on an executive dashboard.

[Live Dashboard](https://retail-flow.streamlit.app) | [GitHub Repository](https://github.com/AditiAhuja01/retail-flow)

---

## Dashboard Preview

<!-- Replace with your dashboard screenshot path, e.g. docs/dashboard_preview.png -->
![RetailFlow Dashboard Preview](docs/dashboard_preview.png)

---

## 1. Business Problem & Impact (Product Context)

Retail platforms face significant profit leakage and reporting inaccuracy due to three factors:

* **Return Revenue Blindness:** Reporting gross sales without separating cancellations overstates realized revenue. In this dataset, returns account for Rs. 7.85 Crores (6.85% of gross sales).
* **Defective Product Categories:** High return rates in specific merchandise categories (Kitchen & Dining at 3.1%, Lighting at 2.9%) indicate supplier or packaging defects requiring operational intervention.
* **Customer Retention Gap:** 34% of customer accounts make only a single purchase, representing lost lifetime value without targeted re-engagement campaigns.

---

## 2. Pipeline Architecture

```mermaid
flowchart LR
    A["Raw Sales Logs"] --> C["validation.py<br>Data Cleaning"]
    B["Forex REST API"] --> C
    C -->|Clean Data| D[("retailflow.db<br>Star Schema")]
    C -->|Corrupt Rows| E["quarantine.csv<br>Audit Log"]
    D --> F["run_analytics.py<br>SQL Engine"]
    F --> G["Streamlit Dashboard<br>Executive UI"]
```

### Pipeline Stages
1. **Ingestion & Normalization (`download_data.py`):** Downloads raw transaction data and queries the `open.er-api.com` REST API for current exchange rates.
2. **Validation & Quarantine (`validation.py`):** Deduplicates records and routes 135,077 non-compliant rows (missing Customer IDs, zero-value prices) into an auditable quarantine file.
3. **Star Schema Modeling (`db_pipeline.py`):** Normalizes 401,564 clean line-items into indexed Fact and Dimension tables in SQLite with referential integrity enabled.
4. **Analytics & Presentation (`run_analytics.py` & `app.py`):** Executes relational SQL queries to calculate net financial metrics and serves an interactive dashboard.

---

## 3. Data Warehouse Design (Kimball Star Schema)

The warehouse structures transactional facts and dimensional context for low-latency analytical queries:

* **`fact_sales` (Fact Table):**
  * Primary Key: `sales_id`
  * Foreign Keys: `customer_id`, `product_code`, `date_key`
  * Metrics: `quantity`, `unit_price`, `amount_gbp`, `amount_inr`, `is_returned`
* **`dim_customers`:** `customer_id` (PK), `country`
* **`dim_products`:** `product_code` (PK), `description`, `category`
* **`dim_dates`:** `date_key` (PK, YYYYMMDD), `full_date`, `year`, `month`, `quarter`, `day_of_week`

B-Tree indexes are created on `fact_sales(customer_id)`, `fact_sales(product_code)`, and `fact_sales(date_key)` to accelerate join performance.

---

## 4. Key Metrics Summary

| Metric | Measured Value | Description |
| :--- | :--- | :--- |
| **Total Ingested Records** | 541,909 rows | Raw transaction extract |
| **Quarantined Records** | 135,077 rows (24.9%) | Records with missing Customer ID or price <= 0 |
| **Clean Warehouse Line-Items** | 401,564 rows | Verified records stored in `fact_sales` |
| **Completed Orders** | 22,186 orders | Distinct invoices processed |
| **Gross Sales Volume** | Rs. 114.67 Cr | Total sales before return deductions |
| **Return Deductions** | -Rs. 7.85 Cr (6.85%) | Refunds resulting from customer cancellations |
| **Net Realized Revenue** | Rs. 106.82 Cr | Actual cash revenue generated |

---

## 5. Key Findings & Actions

* **Revenue Seasonality:** Sales increase steadily throughout the year and peak in November (Q4 accounts for over 35% of annual revenue). Inventory staging should occur 60 days prior to Q4.
* **Return Concentration:** Kitchen & Dining (3.1%) and Lighting & Decor (2.9%) exhibit the highest return rates. Operations should prioritize supplier quality audits on fragile SKUs in these categories.
* **Customer Retention:** High-frequency buyers (5+ orders) represent 25.5% of accounts but drive the majority of revenue. Marketing should deploy 30-day post-purchase offers to convert single-order buyers into repeat customers.

---

## 6. How to Run

### Local Setup
```bash
# 1. Clone repository and install dependencies
git clone https://github.com/AditiAhuja01/retail-flow.git
cd retail-flow
pip install -r requirements.txt

# 2. Run data pipeline
python src/download_data.py
python src/validation.py
python src/db_pipeline.py
python src/run_analytics.py

# 3. Launch dashboard
streamlit run app.py
```

### Docker Execution
```bash
docker compose up
```
Open `http://localhost:8501` in your browser.
