import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------------------
# Page Configuration (Full Screen Width)
# -------------------------------------------------------------
st.set_page_config(
    page_title="RetailFlow | E-Commerce Data Pipeline",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------
# Simple Minimalist White & Grey Theme Styling
# -------------------------------------------------------------
st.markdown("""
    <style>
        /* Base page background: clean soft grey/white */
        .stApp {
            background-color: #F8FAFC;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
            max-width: 96% !important;
        }
        /* Top Status Pills (Minimal grey border) */
        .status-pill {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 500;
            background-color: #FFFFFF;
            color: #475569;
            border: 1px solid #E2E8F0;
            margin-right: 8px;
            margin-bottom: 8px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
        }
        /* Minimalist White Metric Cards */
        .kpi-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            min-height: 110px;
        }
        .kpi-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        .kpi-value {
            font-size: 1.85rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.2;
        }
        .kpi-sub {
            font-size: 0.8rem;
            color: #64748B;
            margin-top: 4px;
        }
        .kpi-loss {
            color: #DC2626;
            font-weight: 600;
        }
        .kpi-positive {
            color: #0F172A;
            font-weight: 600;
        }
        /* Chart container card */
        .chart-box {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
            margin-bottom: 12px;
        }
        .chart-title {
            font-size: 0.92rem;
            font-weight: 600;
            color: #1E293B;
            margin-bottom: 10px;
        }
        /* Simple observation box in clean grey */
        .simple-box {
            background-color: #FFFFFF;
            border-left: 4px solid #334155;
            border-radius: 0 6px 6px 0;
            padding: 14px 18px;
            margin-top: 16px;
            font-size: 0.9rem;
            color: #334155;
            line-height: 1.6;
            border-top: 1px solid #E2E8F0;
            border-right: 1px solid #E2E8F0;
            border-bottom: 1px solid #E2E8F0;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
        }
        /* Clean minimalist tabs */
        button[data-baseweb="tab"] {
            font-size: 0.95rem;
            font-weight: 500;
            color: #64748B;
            padding: 0.6rem 1.4rem;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #0F172A !important;
            font-weight: 600;
            border-bottom-color: #0F172A !important;
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
EXCHANGE_PATH = os.path.join(DATA_DIR, 'exchange_rates.txt')

def load_report(filename):
    path = os.path.join(REPORTS_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

def get_forex_rate():
    rate = 129.03
    if os.path.exists(EXCHANGE_PATH):
        with open(EXCHANGE_PATH, 'r') as f:
            for line in f:
                if line.startswith('INR_RATE='):
                    rate = float(line.split('=')[1].strip())
    return rate

def format_inr(val):
    if pd.isna(val) or val == '' or val is None:
        return "--"
    val = float(val)
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1e7:
        return f"{sign}Rs. {abs_val / 1e7:.2f} Cr"
    elif abs_val >= 1e5:
        return f"{sign}Rs. {abs_val / 1e5:.2f} L"
    elif abs_val >= 1e3:
        return f"{sign}Rs. {abs_val / 1e3:.2f} K"
    else:
        return f"{sign}Rs. {abs_val:,.2f}"

df_summary = load_report("financial_summary.csv")
df_monthly = load_report("monthly_trends.csv")
df_category = load_report("category_performance.csv")
df_ltv = load_report("top_10_customers_ltv.csv")
df_rfm = load_report("rfm_segmentation.csv")
forex_rate = get_forex_rate()

# -------------------------------------------------------------
# Classy Header with Logo & Title
# -------------------------------------------------------------
st.markdown("""
    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 12px;">
        <div style="background: linear-gradient(135deg, #1E293B, #334155); width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
        </div>
        <div>
            <div style="font-size: 1.85rem; font-weight: 700; color: #0F172A; line-height: 1.1; letter-spacing: -0.5px;">RetailFlow</div>
            <div style="font-size: 0.86rem; color: #64748B; margin-top: 3px;">Automated E-Commerce Data Pipeline & Dimensional Warehouse</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Status Pills (Minimalist White & Grey)
st.markdown(f"""
    <div>
        <span class="status-pill"><b>Pipeline Status:</b> Active (SQLite Warehouse)</span>
        <span class="status-pill"><b>Data Quality:</b> 401,564 Clean | 135,077 Quarantined (24.9%)</span>
        <span class="status-pill"><b>Live Currency API:</b> 1 GBP = Rs. {forex_rate:.2f}</span>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if df_summary is None:
    st.error("Reports directory is empty. Please run 'python src/run_analytics.py' first.")
    st.stop()

# -------------------------------------------------------------
# Top 4 KPI Metric Cards (White & Grey Minimalist)
# -------------------------------------------------------------
total_orders = int(df_summary.loc[0, 'total_orders'])
gross_sales = float(df_summary.loc[0, 'gross_sales_inr'])
refund_losses = float(df_summary.loc[0, 'refund_losses_inr'])
net_revenue = float(df_summary.loc[0, 'net_revenue_inr'])
refund_rate = (refund_losses / gross_sales) * 100 if gross_sales > 0 else 0

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Orders</div>
            <div class="kpi-value">{total_orders:,}</div>
            <div class="kpi-sub">Completed invoices</div>
        </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Gross Sales</div>
            <div class="kpi-value">{format_inr(gross_sales)}</div>
            <div class="kpi-sub">Total sales before returns</div>
        </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Refund Losses (Returns)</div>
            <div class="kpi-value">{format_inr(-refund_losses)}</div>
            <div class="kpi-sub"><span class="kpi-loss">{refund_rate:.2f}%</span> of gross volume</div>
        </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Net Realized Revenue</div>
            <div class="kpi-value">{format_inr(net_revenue)}</div>
            <div class="kpi-sub"><span class="kpi-positive">Actual money made</span></div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# Navigation Tabs
# -------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "Revenue Trends",
    "Product Returns",
    "Customer Segments"
])

# -------------------------------------------------------------
# Tab 1: Revenue Trends
# -------------------------------------------------------------
with tab1:
    if df_monthly is not None:
        col_m1, col_m2 = st.columns([3, 2])
        
        with col_m1:
            st.markdown('<div class="chart-title">Monthly Net Revenue (INR)</div>', unsafe_allow_html=True)
            fig_monthly = px.area(
                df_monthly,
                x='year_month',
                y='net_revenue_inr',
                labels={'year_month': 'Month', 'net_revenue_inr': 'Net Revenue (INR)'}
            )
            fig_monthly.update_traces(
                line_color='#334155',
                fillcolor='rgba(51, 65, 85, 0.08)',
                hovertemplate="<b>%{x}</b><br>Net Revenue: Rs. %{y:,.2f}<extra></extra>"
            )
            fig_monthly.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#1E293B", family="sans-serif"),
                height=350,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#F1F5F9')
            )
            st.plotly_chart(fig_monthly, use_container_width=True)

        with col_m2:
            st.markdown('<div class="chart-title">Month-by-Month Growth Table</div>', unsafe_allow_html=True)
            disp_m = df_monthly.copy()
            disp_m.columns = ['Month', 'Orders', 'Net Revenue', 'Growth (%)']
            st.dataframe(
                disp_m.style.format({
                    'Net Revenue': format_inr,
                    'Orders': '{:,}',
                    'Growth (%)': '{:+.2f}%'
                }, na_rep="--"),
                use_container_width=True,
                height=350
            )

        st.markdown("""
            <div class="simple-box">
                <b>📌 What this means:</b> Sales grow steadily throughout the year, and <b>November was the biggest month</b> because of holiday shopping.<br>
                <b>💡 What to do:</b> Order extra inventory 2 months before October so products do not run out of stock during the festival rush.
            </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# Tab 2: Product Returns
# -------------------------------------------------------------
with tab2:
    if df_category is not None:
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.markdown('<div class="chart-title">Sales by Product Category (INR)</div>', unsafe_allow_html=True)
            fig_cat_rev = px.bar(
                df_category,
                x='category',
                y='net_revenue_inr',
                labels={'category': 'Category', 'net_revenue_inr': 'Net Revenue'}
            )
            fig_cat_rev.update_traces(
                marker_color='#334155',
                hovertemplate="<b>%{x}</b><br>Sales: Rs. %{y:,.2f}<extra></extra>"
            )
            fig_cat_rev.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#1E293B", family="sans-serif"),
                height=340,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=False, tickangle=-10),
                yaxis=dict(showgrid=True, gridcolor='#F1F5F9')
            )
            st.plotly_chart(fig_cat_rev, use_container_width=True)

        with col_c2:
            st.markdown('<div class="chart-title">Return Rate (%) by Category</div>', unsafe_allow_html=True)
            fig_cat_ret = px.bar(
                df_category.sort_values('return_rate_percent', ascending=True),
                x='return_rate_percent',
                y='category',
                orientation='h',
                labels={'category': 'Category', 'return_rate_percent': 'Return Rate (%)'}
            )
            fig_cat_ret.update_traces(
                marker_color='#64748B',
                hovertemplate="<b>%{y}</b><br>Return Rate: %{x:.2f}%<extra></extra>"
            )
            fig_cat_ret.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#1E293B", family="sans-serif"),
                height=340,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=True, gridcolor='#F1F5F9'),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_cat_ret, use_container_width=True)

        st.markdown('<div class="chart-title">Detailed Category Numbers</div>', unsafe_allow_html=True)
        disp_cat = df_category.copy()
        disp_cat.columns = ['Category', 'Orders Count', 'Net Revenue', 'Return Rate (%)']
        st.dataframe(
            disp_cat.style.format({
                'Net Revenue': format_inr,
                'Orders Count': '{:,}',
                'Return Rate (%)': '{:.2f}%'
            }),
            use_container_width=True
        )

        st.markdown("""
            <div class="simple-box">
                <b>📌 What this means:</b> <i>Kitchen & Dining</i> (3.1%) and <i>Lighting & Decor</i> (2.9%) have the highest return rates.<br>
                <b>💡 What to do:</b> Check product quality and packaging with suppliers for kitchen and light items to prevent damage and reduce returns.
            </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# Tab 3: Customer Segments
# -------------------------------------------------------------
with tab3:
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown('<div class="chart-title">Customer Order Frequency (1 Order vs Multiple)</div>', unsafe_allow_html=True)
        if df_rfm is not None:
            segment_counts = df_rfm['customer_segment'].value_counts().reset_index()
            segment_counts.columns = ['Segment', 'Count']
            
            fig_pie = px.pie(
                segment_counts,
                names='Segment',
                values='Count',
                hole=0.55,
                color='Segment',
                color_discrete_map={
                    'Repeat Customer (2-4 Orders)': '#334155',
                    'One-Time Customer (1 Order)': '#CBD5E1',
                    'VIP Customer (5+ Orders)': '#0F172A'
                }
            )
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<br>Share: %{percent}<extra></extra>"
            )
            fig_pie.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#1E293B", family="sans-serif"),
                height=360,
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_s2:
        st.markdown('<div class="chart-title">Top 10 High-Spending Customers (LTV)</div>', unsafe_allow_html=True)
        if df_ltv is not None:
            disp_ltv = df_ltv.copy()
            disp_ltv.columns = ['Customer ID', 'Country', 'Orders', 'Total Spend']
            st.dataframe(
                disp_ltv.style.format({
                    'Total Spend': format_inr,
                    'Orders': '{:,}'
                }),
                use_container_width=True,
                height=360
            )

    st.markdown("""
        <div class="simple-box">
            <b>📌 What this means:</b> 
            1 out of 4 customers (25.5%) is a VIP who orders frequently. But <b>34% of people only buy once</b> and never return.<br>
            <b>💡 What to do:</b> Send a 10% discount coupon to one-time buyers within 30 days of their first order to turn them into repeat buyers.
        </div>
    """, unsafe_allow_html=True)
