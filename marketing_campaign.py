
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Marketing Campaign Dashboard",
    layout="wide",
    page_icon="📊"
)

# -----------------------------------
# LOAD DATA
# -----------------------------------
conn = sqlite3.connect("marketing.db")
df = pd.read_sql("SELECT * FROM customer_segments", conn)

st.title("📊 Marketing Campaign Analytics Dashboard")
st.caption("Interactive dashboard with clean visuals and business-focused insights.")

# -----------------------------------
# CREATE SEGMENTS
# -----------------------------------
df['income_segment'] = pd.cut(
    df['Income'],
    bins=[0, 30000, 60000, 100000, df['Income'].max()],
    labels=['Low', 'Middle', 'High', 'Very High']
)

df['age_segment'] = pd.cut(
    df['Age'],
    bins=[0, 30, 45, 60, 100],
    labels=['Young', 'Adult', 'Middle-aged', 'Senior']
)

df['spend_segment'] = pd.cut(
    df['Total_Spend'],
    bins=[0, 200, 500, 1000, df['Total_Spend'].max()],
    labels=['Low', 'Medium', 'High', 'Very High']
)

# -----------------------------------
# SIDEBAR FILTERS
# -----------------------------------
st.sidebar.header("🔎 Filters")

country_filter = st.sidebar.multiselect("Country", sorted(df['Country'].dropna().unique()))
education_filter = st.sidebar.multiselect("Education", sorted(df['Education'].dropna().unique()))
marital_filter = st.sidebar.multiselect("Marital Status", sorted(df['Marital_Status'].dropna().unique()))
age_band_filter = st.sidebar.multiselect("Age Band", df['age_segment'].cat.categories)
income_band_filter = st.sidebar.multiselect("Income Band", df['income_segment'].cat.categories)

filtered_df = df.copy()

if country_filter:
    filtered_df = filtered_df[filtered_df['Country'].isin(country_filter)]
if education_filter:
    filtered_df = filtered_df[filtered_df['Education'].isin(education_filter)]
if marital_filter:
    filtered_df = filtered_df[filtered_df['Marital_Status'].isin(marital_filter)]
if age_band_filter:
    filtered_df = filtered_df[filtered_df['age_segment'].isin(age_band_filter)]
if income_band_filter:
    filtered_df = filtered_df[filtered_df['income_segment'].isin(income_band_filter)]

# -----------------------------------
# KPI METRICS
# -----------------------------------
st.subheader("📌 Key Performance Indicators")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Customers", len(filtered_df))
k2.metric("Avg Spend", round(filtered_df['Total_Spend'].mean(), 2))
k3.metric("Response Rate (%)", round(filtered_df['Response'].mean() * 100, 2))
k4.metric("Avg Web Visits / Month", round(filtered_df['NumWebVisitsMonth'].mean(), 2))

st.divider()

# -----------------------------------
# CHART ROW 1 — BAR + LINE
# -----------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Campaign Response by Income Band")
    response_by_income = filtered_df.groupby("income_segment")['Response'].mean()
    st.bar_chart(response_by_income)

with col2:
    st.subheader("📈 Average Spend by Age Band (Trend View)")
    spend_by_age = filtered_df.groupby("age_segment")['Total_Spend'].mean()
    st.line_chart(spend_by_age)

st.divider()

# -----------------------------------
# CHART ROW 2 — PIE + HORIZONTAL BAR
# -----------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("🥧 Campaign Response Distribution")
    response_counts = filtered_df['Response'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(response_counts, labels=['No Response', 'Response'], autopct='%1.1f%%', startangle=90)
    ax.set_title("Customer Response Share")
    st.pyplot(fig)

with col4:
    st.subheader("📊 Product Category Spend (Horizontal)")
    product_cols = [
        'MntWines', 'MntFruits', 'MntMeatProducts',
        'MntFishProducts', 'MntSweetProducts', 'MntGoldProds'
    ]
    product_means = filtered_df[product_cols].mean().sort_values()
    st.bar_chart(product_means)

st.divider()

# -----------------------------------
# CHART ROW 3 — AREA CHART
# -----------------------------------
st.subheader("📉 Channel Usage by Spend Band (Area Chart)")
channel_by_spend = filtered_df.groupby("spend_segment")['NumWebVisitsMonth'].mean()
st.area_chart(channel_by_spend)

st.divider()

# -----------------------------------
# DATA PREVIEW
# -----------------------------------
st.subheader("📋 Filtered Dataset Preview")
st.dataframe(filtered_df.head(50), use_container_width=True)
