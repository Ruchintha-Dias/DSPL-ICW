import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data

def load_data():
    df = pd.read_csv("cleaned_dataset.csv")  # Replace with your actual CSV file path
    return df

df = load_data()

st.set_page_config(page_title="Sri Lanka Bus Route Dashboard", layout="wide")

# Sidebar Filters
st.sidebar.header("🔎 Filter Bus Routes")
route_filter = st.sidebar.selectbox("Select Route No:", options=["All"] + sorted(df["Route No."].unique().tolist()))
origin_filter = st.sidebar.multiselect("Select Origin(s):", options=df["Origin"].unique(), default=df["Origin"].unique())
destination_filter = st.sidebar.multiselect("Select Destination(s):", options=df["Destination"].unique(), default=df["Destination"].unique())
distance_range = st.sidebar.slider("Distance Range (Km):", int(df["Distance (Km)"].min()), int(df["Distance (Km)"].max()), (int(df["Distance (Km)"].min()), int(df["Distance (Km)"].max())))
show_raw = st.sidebar.checkbox("Show Raw Data")

# Filter Data
filtered_df = df.copy()
if route_filter != "All":
    filtered_df = filtered_df[filtered_df["Route No."] == route_filter]
filtered_df = filtered_df[
    (filtered_df["Origin"].isin(origin_filter)) &
    (filtered_df["Destination"].isin(destination_filter)) &
    (filtered_df["Distance (Km)"] >= distance_range[0]) &
    (filtered_df["Distance (Km)"] <= distance_range[1])
]

# Dashboard Header
st.title("🚌 Sri Lanka Inter-Provincial Bus Routes Dashboard")
st.markdown("An interactive dashboard analyzing **normal inter-provincial bus operations** in Sri Lanka (as of May 2017).")

# Rawv Data
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df)

# Key Metrics
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Routes", len(filtered_df))
col2.metric("Total Buses/Day", int(filtered_df["Operated Buses Per Day"].sum()))
col3.metric("Avg. Distance (Km)", f"{filtered_df['Distance (Km)'].mean():.2f}")
col4.metric("Avg. Travel Time (hrs)", f"{filtered_df['Travel Time (hours)'].mean():.2f}")
col5.metric("Avg. Trips/Day", f"{filtered_df['No of Trip Per Day (Both Side)'].mean():.2f}")

st.markdown("---")

# Chart 1: Top 10 Frequent Routes
st.subheader("📊 Top 10 Frequent Routes by Buses per Day")
top_routes = filtered_df.sort_values("Operated Buses Per Day", ascending=False).head(10)
fig1 = px.bar(top_routes, x="Route No.", y="Operated Buses Per Day", color="Route No.", title="Top Routes by Daily Bus Operation")
st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Distance vs. Travel Time
st.subheader("⏱️ Distance vs Travel Time")
fig2 = px.scatter(filtered_df, x="Distance (Km)", y="Travel Time (hours)", color="Route No.", hover_data=["Origin", "Destination"], title="Distance vs Travel Time")
st.plotly_chart(fig2, use_container_width=True)

# Chart 3: Origin-Destination Heatmap (Optional Matrix Version)
st.subheader("🌐 Origin vs Destination Trip Density")
heatmap_df = filtered_df.groupby(["Origin", "Destination"]).agg({"No of Trip Per Day (Both Side)": "sum"}).reset_index()
fig3 = px.density_heatmap(heatmap_df, x="Origin", y="Destination", z="No of Trip Per Day (Both Side)", color_continuous_scale="Blues")
st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Operated Kilometers Per Day by Route
st.subheader("🛣️ Operated Kilometers Per Day")
fig4 = px.bar(filtered_df, x="Route No.", y="Operated(KM) per day", color="Route No.", title="Operated KM/Day by Route")
st.plotly_chart(fig4, use_container_width=True)





















