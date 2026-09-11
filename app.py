import os
import sqlite3
import pandas as pd
import streamlit as st

# -------------------------------------------------------------
# Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="RetailFlow Analytics",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------
# Custom Styling for Clean Corporate Interface
# -------------------------------------------------------------
st.markdown("""
    <style>
        /* General page layout */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        /* Custom metric card styling */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 600;
        }
        /* Tab styling */
        button[data-baseweb="tab"] {
            font-size: 1rem;
            font-weight: 500;
            padding: 0.75rem 1.25rem;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# File Paths & Data Loading
# -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
DB_PATH = os.path.join(DATA_DIR, 'retailflow_data_warehouse.db')

def load_report(filename):
    path = os.path.join(REPORTS_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

def format_inr(val):
    if pd.isna(val) or val == '' or val is None:
        return "--"
    val = float(val)
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1e7:
        return f"{sign}₹{abs_val / 1e7:.2f} Cr"
    elif abs_val >= 1e5:
        return f"{sign}₹{abs_val / 1e5:.2f} L"
    elif abs_val >= 1e3:
        return f"{sign}₹{abs_val / 1e3:.2f} K"
    else:
        return f"{sign}₹{abs_val:,.2f}"

df_summary = load_report("financial_summary.csv")
df_monthly = load_report("monthly_trends.csv")
df_category = load_report("category_performance.csv")
df_ltv = load_report("top_10_customers_ltv.csv")
df_rfm = load_report("rfm_segmentation.csv")

# -------------------------------------------------------------
# Header
# -------------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("RetailFlow Analytics Platform")
    st.caption("End-to-end data pipeline processing 540,000+ e-commerce transactions with live currency conversion and Star Schema data modeling.")
with col_h2:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists(DB_PATH):
        st.success("Warehouse Status: Online (SQLite)")
    else:
        st.error("Warehouse Status: Offline")

st.markdown("---")

if df_summary is None:
    st.error("Reports directory is empty. Please run 'python src/run_analytics.py' to generate metrics.")
    st.stop()

# -------------------------------------------------------------
# KPI Overview Bar (Always Visible at Top)
# -------------------------------------------------------------
total_orders = int(df_summary.loc[0, 'total_orders'])
gross_sales = df_summary.loc[0, 'gross_sales_inr']
refund_losses = df_summary.loc[0, 'refund_losses_inr']
net_revenue = df_summary.loc[0, 'net_revenue_inr']

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Invoices", f"{total_orders:,}")
kpi2.metric("Gross Revenue", format_inr(gross_sales))
kpi3.metric("Refund Losses (Returns)", format_inr(-refund_losses), delta=f"-{format_inr(refund_losses)}", delta_color="inverse")
kpi4.metric("Net Sales Revenue", format_inr(net_revenue))

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# Navigation Tabs (Clean & Professional)
# -------------------------------------------------------------
tab_exec, tab_returns, tab_customers = st.tabs([
    "Revenue Trends",
    "Product Returns",
    "Customer Segments"
])

# -------------------------------------------------------------
# Tab 1: Revenue Trends
# -------------------------------------------------------------
with tab_exec:
    st.subheader("Monthly Revenue and Order Volume")
    st.caption("Tracking net revenue performance across transaction months.")
    
    if df_monthly is not None:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("**Net Revenue Trend (INR)**")
            chart_data = df_monthly.set_index('year_month')['net_revenue_inr']
            st.line_chart(chart_data)
        
        with c2:
            st.markdown("**Monthly Breakdown & Growth Table**")
            disp_cols = ['year_month', 'total_orders', 'net_revenue_inr']
            if 'mom_growth_percent' in df_monthly.columns:
                disp_cols.append('mom_growth_percent')
            disp_monthly = df_monthly[disp_cols].copy()
            
            rename_dict = {
                'year_month': 'Month',
                'total_orders': 'Orders',
                'net_revenue_inr': 'Net Revenue',
                'mom_growth_percent': 'MoM Growth (%)'
            }
            disp_monthly = disp_monthly.rename(columns=rename_dict)
            
            format_dict = {
                'Net Revenue': format_inr,
                'Orders': '{:,}'
            }
            if 'MoM Growth (%)' in disp_monthly.columns:
                format_dict['MoM Growth (%)'] = '{:+.2f}%'
                
            st.dataframe(
                disp_monthly.style.format(format_dict, na_rep="--"),
                use_container_width=True,
                height=320
            )
            

# -------------------------------------------------------------
# Tab 2: Product Returns & Reverse Logistics
# -------------------------------------------------------------
with tab_returns:
    st.subheader("Category Performance and Return Rates")
    st.caption("Analysis of returns by merchandise category to identify quality and reverse logistics issues.")
    
    if df_category is not None:
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("**Net Revenue by Category (INR)**")
            cat_rev = df_category.set_index('category')['net_revenue_inr']
            st.bar_chart(cat_rev)
            
        with col_r2:
            st.markdown("**Product Return Rate (%)**")
            cat_returns = df_category.set_index('category')['return_rate_percent']
            st.bar_chart(cat_returns)
            
        st.markdown("**Category Metrics Detail**")
        disp_cat = df_category.copy()
        disp_cat.columns = ['Category', 'Total Transactions', 'Net Revenue', 'Return Rate (%)']
        st.dataframe(
            disp_cat.style.format({
                'Net Revenue': format_inr,
                'Total Transactions': '{:,}',
                'Return Rate (%)': '{:.2f}%'
            }),
            use_container_width=True
        )
        

# -------------------------------------------------------------
# Tab 3: Customer Segments (RFM & LTV)
# -------------------------------------------------------------
with tab_customers:
    st.subheader("Customer Lifetime Value and Purchase Frequency")
    st.caption("Segmentation based on customer purchase frequency and lifetime spending.")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("**Top 10 Customers by Lifetime Value (LTV)**")
        if df_ltv is not None:
            disp_ltv = df_ltv.copy()
            disp_ltv.columns = ['Customer ID', 'Country', 'Orders Placed', 'LTV']
            st.dataframe(
                disp_ltv.style.format({'LTV': format_inr, 'Orders Placed': '{:,}'}),
                use_container_width=True
            )
            
    with col_c2:
        st.markdown("**Customer Purchase Frequency Segments**")
        if df_rfm is not None:
            segment_counts = df_rfm['customer_segment'].value_counts().reset_index()
            segment_counts.columns = ['Segment', 'Customer Count']
            st.dataframe(segment_counts, use_container_width=True)
            
            # Retention Summary Metrics
            repeat_customers = int((df_rfm['frequency'] > 1).sum())
            total_customers = len(df_rfm)
            repeat_rate = (repeat_customers / total_customers) * 100
            avg_frequency = df_rfm['frequency'].mean()
            
            st.markdown(f"""
            - **Repeat Customer Rate:** {repeat_rate:.1f}% ({repeat_customers:,} of {total_customers:,} buyers)
            - **Average Purchase Frequency:** {avg_frequency:.1f} orders per customer
            """)
            

