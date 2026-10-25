import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.set_page_config(page_title="Nassau Candy Route Efficiency", layout="wide")
st.title("🍬 Nassau Candy - Shipping Route Efficiency")
st.markdown("### Factory to Customer Analysis")

csv_file = None
for f in os.listdir("."):
    if f.endswith(".csv") or f.endswith(".xlsx") or f.endswith(".xls"):
        csv_file = f
        break

if not csv_file:
    st.warning("Please put CSV file in folder!")
    st.stop()

if csv_file.endswith(".csv"):
    df = pd.read_csv(csv_file)
else:
    df = pd.read_excel(csv_file)

st.success(f"Loaded: {csv_file} - {len(df)} rows")
st.dataframe(df.head(5))

# FIXED DATE FORMAT - THIS IS THE FIX
df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed', dayfirst=True, errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='mixed', dayfirst=True, errors='coerce')
df = df.dropna(subset=['Order Date', 'Ship Date'])

df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
df = df[df['Lead Time'] >= 0]
df['On-Time'] = np.where(df['Lead Time'] <= 5, 1, 0)

st.sidebar.header("Filters")
regions = st.sidebar.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())
ship_modes = st.sidebar.multiselect("Ship Mode", df['Ship Mode'].unique(), default=df['Ship Mode'].unique())
filtered = df[(df['Region'].isin(regions)) & (df['Ship Mode'].isin(ship_modes))]

c1,c2,c3,c4 = st.columns(4)
c1.metric("Shipments", len(filtered))
c2.metric("Avg Lead Time", f"{filtered['Lead Time'].mean():.1f} days")
c3.metric("On-Time %", f"{filtered['On-Time'].mean()*100:.1f}%")
c4.metric("Sales", f"${filtered['Sales'].sum():,.0f}")

state_perf = filtered.groupby('State').agg({'Lead Time':'mean', 'Order ID':'count', 'On-Time':'mean'}).reset_index()
state_perf.columns = ['State','Avg Lead Time','Total Shipments','On-Time Rate']
state_perf = state_perf.sort_values('Avg Lead Time')

st.subheader("Top 10 Fastest Routes")
st.dataframe(state_perf.head(10))

fig1 = px.bar(state_perf.head(15), x='State', y='Avg Lead Time', title="Fastest 15 States")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Bottom 10 Slowest Routes - BOTTLENECK")
st.dataframe(state_perf.tail(10).sort_values('Avg Lead Time', ascending=False))
fig2 = px.bar(state_perf.tail(15).sort_values('Avg Lead Time', ascending=False), x='State', y='Avg Lead Time', title="Slowest 15 States")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Ship Mode Performance")
mode_perf = filtered.groupby('Ship Mode').agg({'Lead Time':'mean', 'Order ID':'count'}).reset_index()
fig3 = px.bar(mode_perf, x='Ship Mode', y='Lead Time', title="Lead Time by Ship Mode")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Bottleneck - Volume vs Delay")
fig4 = px.scatter(state_perf, x='Total Shipments', y='Avg Lead Time', size='Total Shipments', color='State', title="Top Right = Bottleneck!")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("US Map - Avg Lead Time")
fig_map = px.choropleth(state_perf, locations='State', locationmode='USA-states', color='Avg Lead Time', scope="usa", title="Avg Lead Time by State")
st.plotly_chart(fig_map, use_container_width=True)

st.subheader("Key Insights")
st.write(f"1. Slowest State is {state_perf.iloc[-1]['State']} with {state_perf.iloc[-1]['Avg Lead Time']:.1f} days")
st.write(f"2. Fastest State is {state_perf.iloc[0]['State']} with {state_perf.iloc[0]['Avg Lead Time']:.1f} days")
st.write(f"3. Overall On-Time Delivery: {filtered['On-Time'].mean()*100:.1f}%")