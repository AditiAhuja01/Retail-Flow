import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------------------
# Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="RetailFlow | E-Commerce Data Pipeline",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------
# Minimalist White & Grey Theme Styling
# -------------------------------------------------------------
st.markdown("""
    <style>
        /* Base page background */
        .stApp {
            background-color: #F8FAFC;
        }
        /* Hide the default empty Streamlit top header bar completely */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        /* Position RetailFlow right at the very top */
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2.5rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
            max-width: 96% !important;
        }
        /* Top Status Pills */
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
        /* Minimalist Metric Cards */
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
        /* Chart Section Titles */
        .chart-title {
            font-size: 0.92rem;
            font-weight: 600;
            color: #1E293B;
            margin-bottom: 10px;
        }
        /* Clean Professional Summary Box (Zero Emojis) */
        .summary-box {
            background-color: #FFFFFF;
            border-left: 3px solid #334155;
            border-radius: 0 6px 6px 0;
            padding: 16px 20px;
            margin-top: 18px;
            border-top: 1px solid #E2E8F0;
            border-right: 1px solid #E2E8F0;
            border-bottom: 1px solid #E2E8F0;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
        }
        .summary-heading {
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #0F172A;
            margin-bottom: 4px;
        }
        .summary-text {
            font-size: 0.9rem;
            color: #475569;
            line-height: 1.5;
            margin-bottom: 12px;
        }
        .summary-text:last-child {
            margin-bottom: 0px;
        }
        /* Clean Minimalist Tabs */
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
# Classy Header with Logo & Title (Proper Spacing)
# -------------------------------------------------------------
st.markdown("""
    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 14px;">
        <div style="background: #1E293B; width: 42px; height: 42px; border-radius: 8px; display: flex; align-items: center; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
        </div>
        <div>
            <div style="font-size: 1.85rem; font-weight: 700; color: #0F172A; line-height: 1.1; letter-spacing: -0.5px;">RetailFlow</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Status Pills
st.markdown(f"""
    <div style="margin-bottom: 18px;">
        <span class="status-pill"><b>Data Quality:</b> 401,564 Clean | 135,077 Quarantined (24.9%)</span>
        <span class="status-pill"><b>Currency Conversion:</b> 1 GBP = Rs. {forex_rate:.2f}</span>
    </div>
""", unsafe_allow_html=True)

if df_summary is None:
    st.error("Reports directory is empty. Please run 'python src/run_analytics.py' first.")
    st.stop()

# -------------------------------------------------------------
# Top 4 KPI Metric Cards
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
            <div class="kpi-label">Completed Orders</div>
            <div class="kpi-value">{total_orders:,}</div>
            <div class="kpi-sub">Across 401,564 purchased items</div>
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
            st.markdown('<div class="chart-title">Monthly Net Revenue (Rs. Cr)</div>', unsafe_allow_html=True)
            df_monthly['net_revenue_cr'] = df_monthly['net_revenue_inr'] / 1e7
            fig_monthly = px.area(
                df_monthly,
                x='year_month',
                y='net_revenue_cr',
                labels={'year_month': 'Month', 'net_revenue_cr': 'Net Revenue (Rs. Cr)'}
            )
            fig_monthly.update_traces(
                line_color='#334155',
                fillcolor='rgba(51, 65, 85, 0.08)',
                hovertemplate="<b>%{x}</b><br>Net Revenue: Rs. %{y:.2f} Cr<extra></extra>"
            )
            fig_monthly.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="sans-serif", size=12),
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(
                    showgrid=False,
                    tickfont=dict(color="#0F172A", size=12, family="sans-serif"),
                    title=dict(text="Transaction Month", font=dict(color="#0F172A", size=13))
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#E2E8F0',
                    ticksuffix=" Cr",
                    tickfont=dict(color="#0F172A", size=12, family="sans-serif"),
                    title=dict(text="Net Revenue (Rs. Cr)", font=dict(color="#0F172A", size=13))
                )
            )
            st.plotly_chart(fig_monthly, use_container_width=True)

        with col_m2:
            st.markdown('<div class="chart-title">Month-by-Month Growth Table</div>', unsafe_allow_html=True)
            disp_m = df_monthly[['year_month', 'total_orders', 'net_revenue_inr', 'mom_growth_percent']].copy()
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
            <div class="summary-box">
                <div class="summary-heading">Key Finding</div>
                <div class="summary-text">Sales increased steadily month-over-month, reaching an annual peak in November due to seasonal holiday demand.</div>
                <div class="summary-heading">Operational Action</div>
                <div class="summary-text">Schedule inventory restocking 60 days prior to Q4 to prevent out-of-stock events during high-volume periods.</div>
            </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# Tab 2: Product Returns
# -------------------------------------------------------------
with tab2:
    if df_category is not None:
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.markdown('<div class="chart-title">Sales by Product Category (Rs. Cr)</div>', unsafe_allow_html=True)
            df_category['net_revenue_cr'] = df_category['net_revenue_inr'] / 1e7
            fig_cat_rev = px.bar(
                df_category,
                x='category',
                y='net_revenue_cr',
                labels={'category': 'Category', 'net_revenue_cr': 'Net Sales (Rs. Cr)'}
            )
            fig_cat_rev.update_traces(
                marker_color='#334155',
                texttemplate="Rs. %{y:.1f} Cr",
                textposition="outside",
                textfont=dict(color="#0F172A", size=11, family="sans-serif"),
                hovertemplate="<b>%{x}</b><br>Sales: Rs. %{y:.2f} Cr<extra></extra>"
            )
            fig_cat_rev.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="sans-serif", size=12),
                height=350,
                margin=dict(l=20, r=20, t=30, b=25),
                xaxis=dict(
                    showgrid=False,
                    tickangle=0,
                    tickfont=dict(color="#0F172A", size=11, family="sans-serif"),
                    title=dict(text="Product Category", font=dict(color="#0F172A", size=13))
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#E2E8F0',
                    ticksuffix=" Cr",
                    tickfont=dict(color="#0F172A", size=11, family="sans-serif"),
                    title=dict(text="Net Sales (Rs. Cr)", font=dict(color="#0F172A", size=13))
                )
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
                marker_color='#475569',
                texttemplate="%{x:.2f}%",
                textposition="outside",
                textfont=dict(color="#0F172A", size=11, family="sans-serif"),
                hovertemplate="<b>%{y}</b><br>Return Rate: %{x:.2f}%<extra></extra>"
            )
            fig_cat_ret.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="sans-serif", size=12),
                height=350,
                margin=dict(l=20, r=40, t=20, b=25),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='#E2E8F0',
                    tickfont=dict(color="#0F172A", size=11, family="sans-serif"),
                    title=dict(text="Return Rate (%)", font=dict(color="#0F172A", size=13))
                ),
                yaxis=dict(
                    showgrid=False,
                    tickfont=dict(color="#0F172A", size=11, family="sans-serif"),
                    title=dict(text="", font=dict(color="#0F172A", size=13))
                )
            )
            st.plotly_chart(fig_cat_ret, use_container_width=True)

        st.markdown('<div class="chart-title">Detailed Category Numbers</div>', unsafe_allow_html=True)
        disp_cat = df_category[['category', 'transactions_count', 'net_revenue_inr', 'return_rate_percent']].copy()
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
            <div class="summary-box">
                <div class="summary-heading">Key Finding</div>
                <div class="summary-text">Kitchen & Dining (3.1%) and Lighting & Decor (2.9%) exhibit the highest return rates across the product portfolio.</div>
                <div class="summary-heading">Operational Action</div>
                <div class="summary-text">Conduct supplier quality reviews and improve packaging for fragile SKUs to reduce return volumes and reverse freight costs.</div>
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
                textfont=dict(color="#FFFFFF", size=12, family="sans-serif"),
                hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<br>Share: %{percent}<extra></extra>"
            )
            fig_pie.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="sans-serif", size=12),
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
        <div class="summary-box">
            <div class="summary-heading">Key Finding</div>
            <div class="summary-text">Repeat and VIP customers make up 65% of accounts, but 34% of customers have made only a single purchase.</div>
            <div class="summary-heading">Operational Action</div>
            <div class="summary-text">Send automated follow-up communications within 30 days of the first transaction to convert one-time buyers into repeat customers.</div>
        </div>
    """, unsafe_allow_html=True)
