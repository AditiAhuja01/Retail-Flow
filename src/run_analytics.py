import os
import pandas as pd
import sqlite3

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

os.makedirs(REPORTS_DIR, exist_ok=True)
db_path = os.path.join(DATA_DIR, "retailflow_data_warehouse.db")

def run_analytical_queries():
    print("Step 3: Connecting to Data Warehouse and running analytical queries...")
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found at {db_path}. Please run db_pipeline.py first.")
        return

    conn = sqlite3.connect(db_path)

    # -------------------------------------------------------------
    # Query 1: Sales & Returns Financial Summary (INR)
    # -------------------------------------------------------------
    print("Running Query 1: Gross Sales vs. Refund Losses...")
    q_summary = """
        SELECT 
            COUNT(DISTINCT invoice_no) AS total_orders,
            
            -- Total Delivered Sales (Positive Quantities)
            ROUND(SUM(CASE WHEN is_returned = 0 THEN amount_inr ELSE 0 END), 2) AS gross_sales_inr,
            
            -- Total Refund Losses (Negative Quantities)
            ROUND(SUM(CASE WHEN is_returned = 1 THEN ABS(amount_inr) ELSE 0 END), 2) AS refund_losses_inr,
            
            -- Net Sales Revenue
            ROUND(SUM(amount_inr), 2) AS net_revenue_inr
        FROM fact_sales;
    """
    df_summary = pd.read_sql(q_summary, conn)
    df_summary.to_csv(os.path.join(REPORTS_DIR, "financial_summary.csv"), index=False)

    # -------------------------------------------------------------
    # Query 2: Monthly Sales Trends
    # -------------------------------------------------------------
    print("Running Query 2: Monthly Net Revenue Trends...")
    q_monthly = """
        SELECT 
            d.year || '-' || printf('%02d', d.month) AS year_month,
            COUNT(DISTINCT f.invoice_no) AS total_orders,
            ROUND(SUM(f.amount_inr), 2) AS net_revenue_inr
        FROM fact_sales f
        JOIN dim_dates d ON f.date_key = d.date_key
        GROUP BY d.year, d.month
        ORDER BY d.year, d.month;
    """
    df_monthly = pd.read_sql(q_monthly, conn)
    # Simple 1-line monthly growth percentage
    df_monthly['mom_growth_percent'] = round(df_monthly['net_revenue_inr'].pct_change() * 100, 2)
    df_monthly.to_csv(os.path.join(REPORTS_DIR, "monthly_trends.csv"), index=False)

    # -------------------------------------------------------------
    # Query 3: Top Selling Categories & Their Return Rates
    # -------------------------------------------------------------
    print("Running Query 3: Product Category Performance...")
    q_category = """
        SELECT 
            p.category,
            COUNT(DISTINCT f.invoice_no) AS transactions_count,
            ROUND(SUM(f.amount_inr), 2) AS net_revenue_inr,
            
            -- Return Rate % (Returned Orders / Total Orders)
            ROUND(
                CAST(SUM(f.is_returned) AS REAL) / COUNT(f.is_returned) * 100, 
                2
            ) AS return_rate_percent
        FROM fact_sales f
        JOIN dim_products p ON f.product_code = p.product_code
        GROUP BY p.category
        ORDER BY net_revenue_inr DESC;
    """
    df_category = pd.read_sql(q_category, conn)
    df_category.to_csv(os.path.join(REPORTS_DIR, "category_performance.csv"), index=False)

    # -------------------------------------------------------------
    # Query 4: Customer Lifetime Value (LTV) - Top 10 Customers
    # -------------------------------------------------------------
    print("Running Query 4: Top 10 Customers by LTV...")
    q_ltv = """
        SELECT 
            f.customer_id,
            c.country,
            COUNT(DISTINCT f.invoice_no) AS total_orders_placed,
            ROUND(SUM(f.amount_inr), 2) AS lifetime_value_inr
        FROM fact_sales f
        JOIN dim_customers c ON f.customer_id = c.customer_id
        WHERE f.is_returned = 0  -- Only count actual delivered purchases
        GROUP BY f.customer_id, c.country
        ORDER BY lifetime_value_inr DESC
        LIMIT 10;
    """
    df_ltv = pd.read_sql(q_ltv, conn)
    df_ltv.to_csv(os.path.join(REPORTS_DIR, "top_10_customers_ltv.csv"), index=False)

    # -------------------------------------------------------------
    # Query 5: Customer Purchase Frequency & Segmentation
    # -------------------------------------------------------------
    print("Running Query 5: Customer Segmentation...")
    q_rfm = """
        SELECT 
            customer_id,
            COUNT(DISTINCT invoice_no) AS frequency,
            ROUND(SUM(amount_inr), 2) AS monetary_value,
            
            -- Simple, intuitive customer categorization
            CASE 
                WHEN COUNT(DISTINCT invoice_no) >= 5 THEN 'VIP Customer (5+ Orders)'
                WHEN COUNT(DISTINCT invoice_no) >= 2 THEN 'Repeat Customer (2-4 Orders)'
                ELSE 'One-Time Customer (1 Order)'
            END AS customer_segment
        FROM fact_sales
        WHERE is_returned = 0
        GROUP BY customer_id
        ORDER BY monetary_value DESC;
    """
    df_rfm = pd.read_sql(q_rfm, conn)
    df_rfm.to_csv(os.path.join(REPORTS_DIR, "rfm_segmentation.csv"), index=False)

    conn.close()
    print("All analytical reports successfully calculated and saved in /reports folder!")

if __name__ == "__main__":
    run_analytical_queries()
