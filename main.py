import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# Load data with caching
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_dataset.csv")
    return df

# Set page config
st.set_page_config(page_title="Sri Lanka Inter-Provincial Bus Route Dashboard", layout="wide")

# Load dataset
df = load_data()

# Sidebar: Option menu and central filters
with st.sidebar:
    selected = option_menu(
        menu_title="Dashboard Navigation",
        options=["Summary Metrics", "Plots for Routes", "Heatmap", "Plots for Distance", "Plots for Travel Time", "About"],
        orientation="vertical"
    )

    st.header("🔎 Central Filter - This applies to all plots")

    # Route filter
    route_options = sorted(df["Route No."].unique().tolist())
    route_filter = st.multiselect("Select Route No:", ["All"] + route_options, default=["All"])
    filtered_routes = route_options if "All" in route_filter else route_filter

    # Origin filter
    origin_options = sorted(df["Origin"].unique().tolist())
    origin_filter = st.multiselect("Select Origin(s):", ["All"] + origin_options, default=["All"])
    filtered_origins = origin_options if "All" in origin_filter else origin_filter

    # Destination filter
    destination_options = sorted(df["Destination"].unique().tolist())
    destination_filter = st.multiselect("Select Destination(s):", ["All"] + destination_options, default=["All"])
    filtered_destinations = destination_options if "All" in destination_filter else destination_filter

    # Distance range
    distance_range = st.slider("Distance Range (Km):", float(df["Distance (Km)"].min()), float(df["Distance (Km)"].max()), (float(df["Distance (Km)"].min()), float(df["Distance (Km)"].max())))

    # Travel Time range
    travel_time_range = st.slider("Travel Time (hours):", float(df["Travel Time (hours)"].min()), float(df["Travel Time (hours)"].max()), (float(df["Travel Time (hours)"].min()), float(df["Travel Time (hours)"].max())))

# Apply central filters
central_df = df.copy()
central_df = central_df[central_df["Route No."].isin(filtered_routes)]
central_df = central_df[central_df["Origin"].isin(filtered_origins)]
central_df = central_df[central_df["Destination"].isin(filtered_destinations)]
central_df = central_df[(central_df["Distance (Km)"] >= distance_range[0]) & (central_df["Distance (Km)"] <= distance_range[1])]
central_df = central_df[(central_df["Travel Time (hours)"] >= travel_time_range[0]) & (central_df["Travel Time (hours)"] <= travel_time_range[1])]

# Summary metrics
if selected == "Summary Metrics":
    st.title("🚌 Sri Lanka Inter-Provincial Bus Routes Dashboard")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Routes", len(central_df))
    col2.metric("Total Buses Per Day", int(central_df["Operated Buses Per Day"].sum()))
    col3.metric("Avg Distance (Km)", f"{central_df['Distance (Km)'].mean():.2f}")
    col4.metric("Avg Travel Time (Hrs)", f"{central_df['Travel Time (hours)'].mean():.2f}")
    col5.metric("Avg Trips Per Day", f"{central_df['No of Trip Per Day (Both Side)'].mean():.2f}")

    # Raw data checkbox
    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(central_df)

# Top Routes plot
elif selected == "Plots for Routes":
    st.header("Plots for Routes")

    # Sort by operated buses descending
    top_routes = central_df.sort_values("Operated Buses Per Day", ascending=False)

    # Prepare data for grouped bar chart
    grouped_data = top_routes[["Route No.", "No of Busses (Normal)", "Operated Buses Per Day"]].melt(id_vars="Route No.", 
                                            var_name="Bus Type", value_name="Count")
    
    # Calculate the unoperated (allocated but not operated) buses
    top_routes["Unoperated Buses"] = top_routes["No of Busses (Normal)"] - top_routes["Operated Buses Per Day"]

    # Prepare data for stacked bar chart
    stacked_data = top_routes[["Route No.", "Operated Buses Per Day", "Unoperated Buses"]].melt(
        id_vars="Route No.", 
        var_name="Bus Type", 
        value_name="Count"
    )

    # Operated Buses per Route (color scale by count)
    fig1 = px.bar(central_df, x="Route No.", y="Operated Buses Per Day", color="Route No.",
                  title="Operated Buses per Route", color_continuous_scale="Viridis")
    
    # Set y-axis range between 0 and 100
    fig1.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig1, use_container_width=True)

    # Grouped bar chart: Operated + Unoperated Buses
    fig2 = px.bar(
        stacked_data, 
        x="Route No.", 
        y="Count", 
        color="Bus Type",
        barmode="stack", 
        title="Operated vs Unoperated Buses Per Route"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Travel Time per Route (color scale by time)
    fig3 = px.bar(central_df, x="Route No.", y="Travel Time (hours)", color="Route No.",
                  title="Travel Time per Route", color_continuous_scale="Viridis")
    
    # Set y-axis range between 0 and 100
    fig3.update_layout(yaxis_range=[0, 12])
    st.plotly_chart(fig3, use_container_width=True)

# Origin-Destination Heatmap
elif selected == "Heatmap":
    st.title("Heatmap")

    # Aggregate data
    heatmap_df = central_df.groupby(["Origin", "Destination"]).agg(
        {"No of Trip Per Day (Both Side)": "sum"}
    ).reset_index()
    # Create the heatmap with white at 0 using range_color
    fig4 = px.density_heatmap(
        heatmap_df,
        x="Origin",
        y="Destination",
        z="No of Trip Per Day (Both Side)",
        color_continuous_scale=[(0.0, "white"), (1.0, "darkblue")],
        range_color=[0, heatmap_df["No of Trip Per Day (Both Side)"].max()],
        title="Trip Density Between Origins and Destinations"
    )

    st.plotly_chart(fig4, use_container_width=True)

    # Aggregate data2
    heatmap_df1 = central_df.groupby(["Origin", "Destination"]).agg(
        {"Distance (Km)": "mean"}
    ).reset_index()

    # Create the heatmap with white at 0 using range_color
    fig5 = px.density_heatmap(
        heatmap_df1,
        x="Origin",
        y="Destination",
        z="Distance (Km)",
        color_continuous_scale=[(0.0, "white"), (1.0, "darkgreen")],
        range_color=[0, heatmap_df1["Distance (Km)"].max()],
        title="Distance Between Origins and Destinations"
    )

    st.plotly_chart(fig5, use_container_width=True)


# Plots for Distance Page
elif selected == "Plots for Distance":
    st.header("Plots for Distance")

    fig6 = px.scatter(
        central_df,
        x="Distance (Km)",
        y="No of Trip Per Day (Both Side)",
        hover_data=["Route No.", "Origin", "Destination"],
        color="No of Trip Per Day (Both Side)",
        color_continuous_scale="Plasma",
        title="No. of Trips per Distance"
    )
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Travel Time per Distance")
    fig7 = px.scatter(
        central_df,
        x="Distance (Km)",
        y="Travel Time (hours)",
        color="Travel Time (hours)",
        hover_data=["Route No.", "Origin", "Destination"],
        color_continuous_scale="Inferno",
        title="Travel Time per Distance"
    )
    st.plotly_chart(fig7, use_container_width=True)

# Plots for Travel Time Page
elif selected == "Plots for Travel Time":
    st.header("Plots for Travel Time")

    fig8 = px.scatter(
        central_df,
        x="Travel Time (hours)",
        y="No of Trip Per Day (Both Side)",
        hover_data=["Route No.", "Origin", "Destination"],
        color="No of Trip Per Day (Both Side)",
        color_continuous_scale="Plasma",
        title="No. of Trips per Travel Time"
    )
    st.plotly_chart(fig8, use_container_width=True)

elif selected == "About":
    st.header("About")

    st.markdown("""
    This dashboard provides insights into the inter-provincial bus routes for normal buses in Sri Lanka. The data covers routes, travel times, distances and other key details that reflect the transportation system as of May 2017.

    This dataset was sourced from the GitHub repository of Team Watchdog and provides data for this web page.
    
    **Dataset:**
    - **Name:** National Transport Report Tables — 2020_2021 - Inter Provincial Bus Routes – Normal Buses (As at May 2017)
    - **Source:** [National Transport Commission Report 2020-2021](https://github.com/team-watchdog/databank-sri-lanka/blob/main/datasets/transport-sri-lanka/National%20Transport%20Commission%20Report%20(2020-2021)/National%20Transport%20Report%20Tables%20%E2%80%94%202020_2021%20-%20Inter%20Provincial%20Bus%20Routes%20%E2%80%93%20Semi%20Luxury%20Buses%20(As%20at%20May%202017).csv)

    """)