import os
import pandas as pd
import streamlit as st

# Configure the Streamlit page layout
st.set_page_config(page_title="RetailFlow Analytics Dashboard", layout="wide")

# Define folder paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

# Helper function to read csv files safely
def load_report(filename):
    path = os.path.join(REPORTS_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

# --- Dashboard Title ---
st.title("🛒 RetailFlow E-Commerce Analytics Dashboard")
st.markdown("This dashboard displays insights processed from **540,000+ real transactions** and currency conversion rates from a **live REST API**.")

# --- Load Data ---
df_summary = load_report("financial_summary.csv")
df_monthly = load_report("monthly_trends.csv")
df_category = load_report("category_performance.csv")
df_ltv = load_report("top_10_customers_ltv.csv")
df_rfm = load_report("rfm_segmentation.csv")

if df_summary is not None:
    # --- 1. KPI Cards Row ---
    total_orders = df_summary.loc[0, 'total_orders']
    gross_sales = df_summary.loc[0, 'gross_sales_inr']
    refund_losses = df_summary.loc[0, 'refund_losses_inr']
    net_revenue = df_summary.loc[0, 'net_revenue_inr']
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders Processed", f"{total_orders:,}")
    col2.metric("Gross Revenue (INR)", f"₹{gross_sales:,.2f}")
    col3.metric("Refund/Return Losses (INR)", f"₹{refund_losses:,.2f}", delta=f"-₹{refund_losses:,.2f}", delta_color="inverse")
    col4.metric("Net Sales Revenue (INR)", f"₹{net_revenue:,.2f}")
    
    st.markdown("---")

    # --- 2. Chart Sections (Columns) ---
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("📈 Monthly Net Revenue Trend")
        if df_monthly is not None:
            # Display simple monthly growth trend
            df_monthly_chart = df_monthly.set_index('year_month')['net_revenue_inr']
            st.line_chart(df_monthly_chart)
        else:
            st.info("Monthly trend report not available.")

    with chart_col2:
        st.subheader("🛍️ Sales Revenue by Product Category")
        if df_category is not None:
            # Display category revenue distribution
            df_cat_chart = df_category.set_index('category')['net_revenue_inr']
            st.bar_chart(df_cat_chart)
        else:
            st.info("Product category report not available.")

    st.markdown("---")

    # --- 3. Tables Row (Columns) ---
    table_col1, table_col2 = st.columns(2)

    with table_col1:
        st.subheader("🏆 Top 10 VIP Customers (Highest Lifetime Value)")
        if df_ltv is not None:
            # Clean up column names for display
            df_ltv_disp = df_ltv.copy()
            df_ltv_disp.columns = ['Customer ID', 'Country', 'Orders Placed', 'LTV (INR)']
            st.dataframe(df_ltv_disp.style.format({'LTV (INR)': '₹{:,.2f}'}), use_container_width=True)
        else:
            st.info("Top customers report not available.")

    with table_col2:
        st.subheader("👥 RFM Customer Segments")
        if df_rfm is not None:
            # Group by segment to show user counts
            segment_counts = df_rfm['customer_segment'].value_counts().reset_index()
            segment_counts.columns = ['Customer Segment', 'Customer Count']
            st.dataframe(segment_counts, use_container_width=True)
        else:
            st.info("RFM segmentation report not available.")

else:
    st.error("⚠️ Reports directory is empty. Please run the data pipelines first (download_data.py -> validation.py -> db_pipeline.py -> run_analytics.py).")
