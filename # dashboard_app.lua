# dashboard_app.py
import streamlit as st
import pandas as pd

from local_impact_calculator import RetailerInputs, summarize_retailer

st.set_page_config(page_title="FLX Local Impact – Comparison", layout="wide")

st.title("FLX Goods – Local Impact vs Competitors (MVP)")

st.markdown(
    "Use this simple dashboard to compare **local economic impact** "
    "between FLX Goods and major competitors."
)

# --- Inputs ---
st.sidebar.header("Inputs")

# FLX
st.sidebar.subheader("FLX Goods")
flx_sales = st.sidebar.number_input("FLX Total Sales ($)", value=100000.0, step=1000.0)
flx_taxes = st.sidebar.number_input("FLX Taxes ($)", value=8000.0, step=500.0)
flx_shipping = st.sidebar.number_input("FLX Shipping ($)", value=6000.0, step=500.0)
flx_local_rate = st.sidebar.slider("FLX Local Rate", 0.0, 1.0, 0.65, 0.05)
flx_multiplier = st.sidebar.slider("Multiplier (RIMS-ish)", 1.0, 2.0, 1.6, 0.05)

# Amazon
st.sidebar.subheader("Amazon")
amz_sales = st.sidebar.number_input("Amazon Total Sales ($)", value=100000.0, step=1000.0)
amz_taxes = st.sidebar.number_input("Amazon Taxes ($)", value=8000.0, step=500.0)
amz_shipping = st.sidebar.number_input("Amazon Shipping ($)", value=6000.0, step=500.0)
amz_local_rate = st.sidebar.slider("Amazon Local Rate", 0.0, 1.0, 0.10, 0.05)
amz_multiplier = st.sidebar.slider("Amazon Multiplier", 1.0, 2.0, 1.4, 0.05)

# You can add Walmart, Wegmans later the same way

# --- Build Retailer objects using your calculator code ---
flx = RetailerInputs(
    name="FLX Goods",
    total_sales=flx_sales,
    taxes=flx_taxes,
    shipping=flx_shipping,
    local_rate=flx_local_rate,
    multiplier=flx_multiplier,
)

amazon = RetailerInputs(
    name="Amazon",
    total_sales=amz_sales,
    taxes=amz_taxes,
    shipping=amz_shipping,
    local_rate=amz_local_rate,
    multiplier=amz_multiplier,
)

retailers = [flx, amazon]  # later: add walmart, wegmans, etc.

summaries = [summarize_retailer(r) for r in retailers]

# --- KPIs ---
st.subheader("Key Metrics")

col1, col2 = st.columns(2)
with col1:
    s_flx = summaries[0]
    st.metric(
        "FLX Local Impact ($)",
        f"{s_flx['local_impact_dollars']:,.0f}",
        help="From your calculator formula.",
    )
    st.metric(
        "FLX Local Impact Share",
        f"{s_flx['local_impact_share']*100:.1f}% per $1 sales",
    )

with col2:
    s_amz = summaries[1]
    st.metric(
        "Amazon Local Impact ($)",
        f"{s_amz['local_impact_dollars']:,.0f}",
    )
    st.metric(
        "Amazon Local Impact Share",
        f"{s_amz['local_impact_share']*100:.1f}% per $1 sales",
    )

# --- Comparison chart ---
st.subheader("Local Impact Comparison")

df = pd.DataFrame(
    {
        "Retailer": [s["name"] for s in summaries],
        "Local Impact ($)": [s["local_impact_dollars"] for s in summaries],
    }
)

st.bar_chart(df.set_index("Retailer"))

st.caption(
    "MVP dashboard using the local_impact_calculator engine. "
    "Later we’ll hook this up to real Shopify sales and RIMS II multipliers."
)
