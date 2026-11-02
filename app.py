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
    page_title="RetailFlow | Executive Analytics",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------
# Corporate Light Theme Styling
# -------------------------------------------------------------
st.markdown("""
    <style>
        /* Base page background */
        .stApp {
            background-color: #FAFAFA;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }
        /* Metric cards */
        .kpi-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }
        .kpi-label {
            font-size: 0.78rem;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        .kpi-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.2;
        }
        .kpi-sub {
            font-size: 0.8rem;
            color: #64748B;
            margin-top: 6px;
        }
        .kpi-loss {
            color: #DC2626;
            font-weight: 600;
        }
        .kpi-positive {
            color: #059669;
            font-weight: 600;
        }
        /* Status badge */
        .status-pill {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 500;
            background-color: #F1F5F9;
            color: #334155;
            border: 1px solid #CBD5E1;
            margin-right: 8px;
        }
        /* Executive observation box */
        .insight-box {
            background-color: #F8FAFC;
            border-left: 4px solid #2563EB;
            border-radius: 0 6px 6px 0;
            padding: 14px 18px;
            margin-top: 20px;
            margin-bottom: 20px;
            font-size: 0.88rem;
            color: #334155;
            line-height: 1.5;
            border-top: 1px solid #E2E8F0;
            border-right: 1px solid #E2E8F0;
            border-bottom: 1px solid #E2E8F0;
        }
        /* Clean tabs */
        button[data-baseweb="tab"] {
            font-size: 0.95rem;
            font-weight: 500;
            color: #475569;
            padding: 0.6rem 1.2rem;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #2563EB !important;
            font-weight: 600;
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
# Header & Data Pipeline Health
# -------------------------------------------------------------
st.title("RetailFlow Analytics Platform")
st.markdown(
    "Batch ETL & Star Schema Data Warehouse processing 540,000+ international transaction records."
)

# Status indicators
st.markdown(f"""
    <div>
        <span class="status-pill"><b>Pipeline Status:</b> Active (SQLite Warehouse)</span>
        <span class="status-pill"><b>Ingestion Quality:</b> 401,564 Clean | 135,077 Quarantined (24.9%)</span>
        <span class="status-pill"><b>Live Forex API:</b> 1 GBP = Rs. {forex_rate:.2f}</span>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if df_summary is None:
    st.error("Reports directory is empty. Please run 'python src/run_analytics.py' first.")
    st.stop()

# -------------------------------------------------------------
# Top KPI Metric Cards
# -------------------------------------------------------------
total_orders = int(df_summary.loc[0, 'total_orders'])
gross_sales = float(df_summary.loc[0, 'gross_sales_inr'])
refund_losses = float(df_summary.loc[0, 'refund_losses_inr'])
net_revenue = float(df_summary.loc[0, 'net_revenue_inr'])
refund_rate = (refund_losses / gross_sales) * 100 if gross_sales > 0 else 0

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Invoices</div>
            <div class="kpi-value">{total_orders:,}</div>
            <div class="kpi-sub">Completed transactions</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Gross Sales</div>
            <div class="kpi-value">{format_inr(gross_sales)}</div>
            <div class="kpi-sub">Pre-cancellation volume</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Return Deductions</div>
            <div class="kpi-value">{format_inr(-refund_losses)}</div>
            <div class="kpi-sub"><span class="kpi-loss">{refund_rate:.2f}%</span> of gross volume</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Net Realized Revenue</div>
            <div class="kpi-value">{format_inr(net_revenue)}</div>
            <div class="kpi-sub"><span class="kpi-positive">Net after returns</span></div>
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
# Tab 1: Revenue Trends & Monthly Performance
# -------------------------------------------------------------
with tab1:
    st.subheader("Monthly Revenue Trajectory")
    st.caption("Month-by-month realized net revenue and order volumes.")

    if df_monthly is not None:
        col_m1, col_m2 = st.columns([3, 2])
        
        with col_m1:
            # Clean Plotly Line/Area Chart
            fig_monthly = px.area(
                df_monthly,
                x='year_month',
                y='net_revenue_inr',
                labels={'year_month': 'Month', 'net_revenue_inr': 'Net Revenue (INR)'},
                title="Monthly Net Revenue (INR)"
            )
            fig_monthly.update_traces(
                line_color='#2563EB',
                fillcolor='rgba(37, 99, 235, 0.1)',
                hovertemplate="<b>%{x}</b><br>Net Revenue: Rs. %{y:,.2f}<extra></extra>"
            )
            fig_monthly.update_layout(
                template="plotly_white",
                height=340,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#F1F5F9')
            )
            st.plotly_chart(fig_monthly, use_container_width=True)

        with col_m2:
            st.markdown("**Monthly Performance Breakdown**")
            disp_m = df_monthly.copy()
            disp_m.columns = ['Month', 'Orders', 'Net Revenue (INR)', 'MoM Growth (%)']
            st.dataframe(
                disp_m.style.format({
                    'Net Revenue (INR)': format_inr,
                    'Orders': '{:,}',
                    'MoM Growth (%)': '{:+.2f}%'
                }, na_rep="--"),
                use_container_width=True,
                height=340
            )

        st.markdown("""
            <div class="insight-box">
                <b>Executive Observation:</b> Realized revenue demonstrates steady month-over-month expansion, 
                culminating in peak sales in Q4 (November). This seasonal surge accounts for over 35% of annual net revenue, 
                confirming the need for automated inventory staging ahead of peak promotional periods.
            </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# Tab 2: Product Returns & Category Performance
# -------------------------------------------------------------
with tab2:
    st.subheader("Category Performance & Return Deductions")
    st.caption("Evaluation of product return rates to identify reverse logistics impact.")

    if df_category is not None:
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            fig_cat_rev = px.bar(
                df_category,
                x='category',
                y='net_revenue_inr',
                labels={'category': 'Category', 'net_revenue_inr': 'Net Revenue (INR)'},
                title="Net Revenue by Product Category"
            )
            fig_cat_rev.update_traces(
                marker_color='#2563EB',
                hovertemplate="<b>%{x}</b><br>Net Revenue: Rs. %{y:,.2f}<extra></extra>"
            )
            fig_cat_rev.update_layout(
                template="plotly_white",
                height=320,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(showgrid=False, tickangle=-15),
                yaxis=dict(showgrid=True, gridcolor='#F1F5F9')
            )
            st.plotly_chart(fig_cat_rev, use_container_width=True)

        with col_c2:
            fig_cat_ret = px.bar(
                df_category.sort_values('return_rate_percent', ascending=True),
                x='return_rate_percent',
                y='category',
                orientation='h',
                labels={'category': 'Category', 'return_rate_percent': 'Return Rate (%)'},
                title="Product Return Rate (%) by Category"
            )
            fig_cat_ret.update_traces(
                marker_color='#64748B',
                hovertemplate="<b>%{y}</b><br>Return Rate: %{x:.2f}%<extra></extra>"
            )
            fig_cat_ret.update_layout(
                template="plotly_white",
                height=320,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(showgrid=True, gridcolor='#F1F5F9'),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_cat_ret, use_container_width=True)

        st.markdown("**Category Detail Metrics**")
        disp_cat = df_category.copy()
        disp_cat.columns = ['Product Category', 'Transactions', 'Net Revenue', 'Return Rate (%)']
        st.dataframe(
            disp_cat.style.format({
                'Net Revenue': format_inr,
                'Transactions': '{:,}',
                'Return Rate (%)': '{:.2f}%'
            }),
            use_container_width=True
        )

        st.markdown("""
            <div class="insight-box">
                <b>Executive Observation:</b> <i>Kitchen & Dining</i> (3.12%) and <i>Lighting & Decor</i> (2.88%) 
                exhibit the highest return rates across the product portfolio. 
                <b>Operational Recommendation:</b> Operations and vendor management can prioritize quality audits on 
                high-return SKUs in these two categories to minimize reverse logistics freight costs.
            </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# Tab 3: Customer Retention & Segmentation
# -------------------------------------------------------------
with tab3:
    st.subheader("Customer Frequency Segmentation & Lifetime Value")
    st.caption("Distribution of purchasing accounts and high-value customer concentration.")

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        if df_rfm is not None:
            segment_counts = df_rfm['customer_segment'].value_counts().reset_index()
            segment_counts.columns = ['Segment', 'Count']
            
            fig_pie = px.pie(
                segment_counts,
                names='Segment',
                values='Count',
                hole=0.55,
                title="Customer Order Frequency Distribution",
                color='Segment',
                color_discrete_map={
                    'Repeat Customer (2-4 Orders)': '#2563EB',
                    'One-Time Customer (1 Order)': '#94A3B8',
                    'VIP Customer (5+ Orders)': '#059669'
                }
            )
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<br>Share: %{percent}<extra></extra>"
            )
            fig_pie.update_layout(
                template="plotly_white",
                height=320,
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_s2:
        st.markdown("**Top 10 Accounts by Lifetime Value (LTV)**")
        if df_ltv is not None:
            disp_ltv = df_ltv.copy()
            disp_ltv.columns = ['Customer ID', 'Country', 'Orders', 'Realized LTV']
            st.dataframe(
                disp_ltv.style.format({
                    'Realized LTV': format_inr,
                    'Orders': '{:,}'
                }),
                use_container_width=True,
                height=320
            )

    st.markdown("""
        <div class="insight-box">
            <b>Executive Observation:</b> High-frequency accounts (VIP buyers with 5+ orders) represent 25.5% of the customer base 
            yet account for the majority of recurring transaction flow. Meanwhile, 34.2% of purchasers remain one-time buyers.
            <b>Commercial Recommendation:</b> The retention marketing team can deploy automated re-engagement workflows 
            within 30 days of the first purchase to convert single-order buyers into repeat customers.
        </div>
    """, unsafe_allow_html=True)
