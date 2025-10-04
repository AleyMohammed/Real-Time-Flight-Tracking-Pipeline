import streamlit as st
import pandas as pd
import psycopg2
import folium
from streamlit_folium import st_folium
import ast
from datetime import datetime
import plotly.express as px

# 🎨 Page Configuration
st.set_page_config(
    page_title="FlightRadar Live Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎯 Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .stButton > button {
        background: linear-gradient(90deg, #007bff, #0056b3);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
    }
</style>
""", unsafe_allow_html=True)

# 🎯 Load ALL flights from database (NO CACHE, NO LIMIT)
def load_all_flights():
    """Load ALL flights from database without any limitations"""
    try:
        conn = psycopg2.connect(
            dbname="flights_project",
            user="admin",
            password="admin",
            host="postgres_general"
        )
        # Query to get ALL flights - no LIMIT clause
        query = "SELECT flight_id, origin, destination, status, departure_time, arrival_time FROM flights ORDER BY departure_time DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Show how many flights were loaded
        st.sidebar.success(f"✅ Loaded {len(df)} flights from database")
        return df
    except Exception as e:
        st.sidebar.error(f"❌ Database error: {str(e)}")
        return pd.DataFrame()

# 🎯 Process flight data
def process_flight_data(df):
    if df.empty:
        return df
    
    try:
        # Convert coordinates from string to list
        df["origin_coord"] = df["origin"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        df["destination_coord"] = df["destination"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        
        # Convert timestamps to datetime
        df["departure_datetime"] = df["departure_time"].apply(lambda x: datetime.fromtimestamp(x))
        df["arrival_datetime"] = df["arrival_time"].apply(lambda x: datetime.fromtimestamp(x))
        df["flight_duration"] = (df["arrival_datetime"] - df["departure_datetime"]).dt.total_seconds() / 3600
        
        # Calculate flight progress (simulation)
        now = datetime.now()
        df["progress"] = df.apply(lambda row: min(1.0, max(0.0, 
            (now - row["departure_datetime"]).total_seconds() / 
            (row["arrival_datetime"] - row["departure_datetime"]).total_seconds())), axis=1)
        
        # Calculate current position coordinates
        df["current_lat"] = df.apply(lambda row: 
            row["origin_coord"][0] + (row["destination_coord"][0] - row["origin_coord"][0]) * row["progress"], axis=1)
        df["current_lon"] = df.apply(lambda row: 
            row["origin_coord"][1] + (row["destination_coord"][1] - row["origin_coord"][1]) * row["progress"], axis=1)
        
        return df
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return df

# 🎯 Create static map (NO AUTO-REFRESH)
def create_static_flight_map(df):
    """Create a static map that doesn't refresh automatically"""
    
    # Create base map with dark theme
    m = folium.Map(
        location=[30, 0],  # Center of world
        zoom_start=2,
        tiles='CartoDB dark_matter'
    )
    
    # Flight status colors
    status_colors = {
        "On Time": "green",
        "Delayed": "orange", 
        "Cancelled": "red",
        "In Flight": "blue"
    }
    
    all_coordinates = []
    
    # Add each flight to the map
    for index, flight in df.iterrows():
        color = status_colors.get(flight["status"], "blue")
        current_position = [flight["current_lat"], flight["current_lon"]]
        
        # Add flight path line
        folium.PolyLine(
            locations=[flight["origin_coord"], flight["destination_coord"]],
            color=color,
            weight=2,
            opacity=0.7,
            dash_array="5,5"
        ).add_to(m)
        
        # Add current aircraft position
        folium.Marker(
            location=current_position,
            popup=folium.Popup(f"""
                <div style="width: 250px; font-family: Arial;">
                    <h4 style="margin: 0;">✈️ {flight['flight_id']}</h4>
                    <hr style="margin: 5px 0;">
                    <b>From:</b> {flight['origin']}<br>
                    <b>To:</b> {flight['destination']}<br>
                    <b>Status:</b> <span style="color: {color}; font-weight: bold;">{flight['status']}</span><br>
                    <b>Progress:</b> {flight['progress']:.1%}<br>
                    <b>Departure:</b> {flight['departure_datetime'].strftime('%Y-%m-%d %H:%M')}<br>
                    <b>Arrival:</b> {flight['arrival_datetime'].strftime('%Y-%m-%d %H:%M')}<br>
                    <b>Duration:</b> {flight['flight_duration']:.1f} hours
                </div>
            """, max_width=300),
            icon=folium.Icon(color=color, icon="plane", prefix="fa"),
            tooltip=f"Flight {flight['flight_id']} - {flight['status']}"
        ).add_to(m)
        
        # Add origin airport
        folium.CircleMarker(
            location=flight["origin_coord"],
            radius=4,
            popup=f"🛫 Origin: {flight['origin']}",
            color="white",
            fill=True,
            fillColor="green",
            fillOpacity=0.8
        ).add_to(m)
        
        # Add destination airport
        folium.CircleMarker(
            location=flight["destination_coord"],
            radius=4,
            popup=f"🛬 Destination: {flight['destination']}",
            color="white",
            fill=True,
            fillColor="red", 
            fillOpacity=0.8
        ).add_to(m)
        
        # Collect coordinates for map bounds
        all_coordinates.extend([
            flight["origin_coord"], 
            flight["destination_coord"], 
            current_position
        ])
    
    # Fit map to show all flights
    if all_coordinates:
        m.fit_bounds(all_coordinates)
    
    return m

# 🎯 Create statistics
def create_flight_statistics(df):
    if df.empty:
        return
        
    total = len(df)
    on_time = len(df[df["status"] == "On Time"])
    delayed = len(df[df["status"] == "Delayed"])
    cancelled = len(df[df["status"] == "Cancelled"])
    in_flight = len(df[df["status"] == "In Flight"]) if "In Flight" in df["status"].values else 0
    
    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📊 Total Flights", total)
    with col2:
        st.metric("✅ On Time", on_time, f"{(on_time/total)*100:.1f}%")
    with col3:
        st.metric("⏰ Delayed", delayed, f"{(delayed/total)*100:.1f}%")
    with col4:
        st.metric("❌ Cancelled", cancelled, f"{(cancelled/total)*100:.1f}%")
    with col5:
        st.metric("✈️ In Flight", in_flight, f"{(in_flight/total)*100:.1f}%")

# 🎯 Create charts
def create_flight_charts(df):
    if df.empty:
        return
        
    col1, col2 = st.columns(2)
    
    with col1:
        # Status pie chart
        status_counts = df["status"].value_counts()
        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title=f"Flight Status Distribution ({len(df)} Total Flights)",
            color_discrete_map={
                "On Time": "#28a745",
                "Delayed": "#ffc107", 
                "Cancelled": "#dc3545",
                "In Flight": "#007bff"
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Flights by hour
        df["departure_hour"] = df["departure_datetime"].dt.hour
        hourly_data = df.groupby("departure_hour").size().reset_index(name="flight_count")
        
        fig_bar = px.bar(
            hourly_data,
            x="departure_hour", 
            y="flight_count",
            title="Flights by Departure Hour",
            labels={"departure_hour": "Hour of Day", "flight_count": "Number of Flights"},
            color_discrete_sequence=["#007bff"]
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# 🎯 Main application
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>✈️ FlightRadar Live Dashboard</h1>
        <p>Complete flight tracking system - showing ALL flights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if "flight_data" not in st.session_state:
        st.session_state.flight_data = None
        st.session_state.last_update = None
        st.session_state.data_loaded = False
    
    # Sidebar
    st.sidebar.title("🎛️ Flight Control Panel")
    
    # Load data button
    if st.sidebar.button("🔄 Load All Flight Data", type="primary"):
        with st.spinner("🔄 Loading ALL flights from database..."):
            raw_data = load_all_flights()
            if not raw_data.empty:
                processed_data = process_flight_data(raw_data)
                st.session_state.flight_data = processed_data
                st.session_state.last_update = datetime.now()
                st.session_state.data_loaded = True
                st.sidebar.success(f"✅ Successfully loaded {len(processed_data)} flights!")
            else:
                st.sidebar.error("❌ Failed to load flight data")
                return
    
    # Auto-load data on first run
    if not st.session_state.data_loaded:
        with st.spinner("🔄 Loading initial flight data..."):
            raw_data = load_all_flights()
            if not raw_data.empty:
                processed_data = process_flight_data(raw_data)
                st.session_state.flight_data = processed_data
                st.session_state.last_update = datetime.now()
                st.session_state.data_loaded = True
    
    # Show last update info
    if st.session_state.last_update:
        st.sidebar.info(f"🕒 Last Updated: {st.session_state.last_update.strftime('%H:%M:%S')}")
        minutes_ago = int((datetime.now() - st.session_state.last_update).total_seconds() // 60)
        if minutes_ago > 0:
            st.sidebar.caption(f"Updated {minutes_ago} minutes ago")
    
    # Get data
    df = st.session_state.flight_data
    
    if df is None or df.empty:
        st.warning("⚠️ No flight data loaded. Click 'Load All Flight Data' to start.")
        return
    
    # Filters
    st.sidebar.subheader("🔍 Filter Options")
    
    available_statuses = df["status"].unique().tolist()
    selected_statuses = st.sidebar.multiselect(
        "Select Flight Status:",
        available_statuses,
        default=available_statuses
    )
    
    # Apply filters
    if selected_statuses:
        filtered_df = df[df["status"].isin(selected_statuses)]
    else:
        filtered_df = df
    
    # Show filtered count
    st.sidebar.info(f"📊 Displaying: {len(filtered_df)} / {len(df)} flights")
    
    if filtered_df.empty:
        st.warning("⚠️ No flights match your filter criteria.")
        return
    
    # Flight statistics
    create_flight_statistics(filtered_df)
    
    # Static map (NO AUTO-REFRESH)
    st.subheader("🗺️ Flight Tracking Map")
    st.info("🔒 Map is static - no auto-refresh. Click 'Load All Flight Data' to update.")
    
    flight_map = create_static_flight_map(filtered_df)
    map_data = st_folium(
        flight_map, 
        width=None, 
        height=600,
        key=f"static_map_{len(filtered_df)}"  # Unique key to prevent auto-refresh
    )
    
    # Charts
    st.subheader("📊 Flight Analytics")
    create_flight_charts(filtered_df)
    
    # Flight table
    st.subheader("📋 All Flight Details")
    
    # Prepare table data
    table_data = filtered_df[[
        "flight_id", "origin", "destination", "status", 
        "departure_datetime", "arrival_datetime", "flight_duration", "progress"
    ]].copy()
    
    table_data["departure_datetime"] = table_data["departure_datetime"].dt.strftime("%Y-%m-%d %H:%M")
    table_data["arrival_datetime"] = table_data["arrival_datetime"].dt.strftime("%Y-%m-%d %H:%M")
    table_data["flight_duration"] = table_data["flight_duration"].apply(lambda x: f"{x:.1f}h")
    table_data["progress"] = table_data["progress"].apply(lambda x: f"{x:.0%}")
    
    # Rename columns
    table_data.columns = [
        "Flight ID", "Origin", "Destination", "Status",
        "Departure", "Arrival", "Duration", "Progress"
    ]
    
    # Display table with styling
    st.dataframe(
        table_data,
        use_container_width=True,
        height=400
    )
    
    # Footer
    st.markdown("---")
    st.caption("💡 This dashboard loads ALL flights from your database and updates only when you click the button - no auto-refresh!")

if __name__ == "__main__":
    main()