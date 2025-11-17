import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import folium_static
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Explorer - RentMap", page_icon="🗺️", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .filter-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/processed/rentals_processed.csv')
    except:
        df = pd.DataFrame({
            'title': ['2 BHK Apartment in Vasant Kunj', '3 BHK Villa in Defence Colony', 
                     '1 BHK Flat in Karol Bagh', '2 BHK Apartment in Dwarka',
                     '3 BHK Penthouse in Greater Kailash', '1 BHK Studio in Lajpat Nagar',
                     '2 BHK Apartment in Rohini', '4 BHK Villa in Chanakyapuri',
                     '2 BHK Flat in Janakpuri', '3 BHK Apartment in Saket'],
            'bhk': [2, 3, 1, 2, 3, 1, 2, 4, 2, 3],
            'price': [35000, 75000, 18000, 28000, 95000, 15000, 25000, 150000, 30000, 68000],
            'area_sqft': [1200, 2500, 600, 1100, 2800, 500, 1000, 3500, 1150, 2200],
            'location': ['Vasant Kunj', 'Defence Colony', 'Karol Bagh', 'Dwarka', 
                        'Greater Kailash', 'Lajpat Nagar', 'Rohini', 'Chanakyapuri',
                        'Janakpuri', 'Saket'],
            'latitude': [28.5217, 28.5675, 28.6517, 28.5921, 28.5494, 28.5678, 28.7489, 28.5983, 28.6219, 28.5244],
            'longitude': [77.1587, 77.2376, 77.1905, 77.0460, 77.2466, 77.2434, 77.1177, 77.1892, 77.0919, 77.2066],
            'furnishing': ['Semi-Furnished', 'Furnished', 'Unfurnished', 'Semi-Furnished',
                          'Fully Furnished', 'Semi-Furnished', 'Unfurnished', 'Fully Furnished',
                          'Semi-Furnished', 'Furnished']
        })
        df['price_per_sqft'] = (df['price'] / df['area_sqft']).round(2)
    return df

df = load_data()

# Header
st.markdown('<h1 style="text-align: center; color: #667eea;">🗺️ Interactive Rent Explorer</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar filters
st.sidebar.markdown('<div class="filter-header"><h2 style="margin:0;">🎛️ Filters</h2></div>', unsafe_allow_html=True)

# BHK filter
bhk_options = sorted(df['bhk'].unique())
selected_bhk = st.sidebar.multiselect(
    "🏠 BHK Type",
    options=bhk_options,
    default=bhk_options,
    help="Select apartment types"
)

# Price range filter
min_price, max_price = int(df['price'].min()), int(df['price'].max())
price_range = st.sidebar.slider(
    "💰 Price Range (₹)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=1000,
    format="₹%d"
)

# Location filter
locations = sorted(df['location'].unique())
selected_locations = st.sidebar.multiselect(
    "📍 Locations",
    options=locations,
    default=locations,
    help="Filter by specific locations"
)

# Furnishing filter
furnishing_options = sorted(df['furnishing'].unique())
selected_furnishing = st.sidebar.multiselect(
    "🛋️ Furnishing",
    options=furnishing_options,
    default=furnishing_options
)

# Map visualization type
st.sidebar.markdown("---")
st.sidebar.markdown("### 🗺️ Map Options")
viz_type = st.sidebar.radio(
    "Visualization Type",
    options=["Markers", "Heatmap", "Both"],
    index=2
)

# Apply filters
filtered_df = df[
    (df['bhk'].isin(selected_bhk)) &
    (df['price'] >= price_range[0]) &
    (df['price'] <= price_range[1]) &
    (df['location'].isin(selected_locations)) &
    (df['furnishing'].isin(selected_furnishing))
]

# Display metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("📋 Filtered Listings", len(filtered_df))
col2.metric("💵 Avg Rent", f"₹{filtered_df['price'].mean():,.0f}" if len(filtered_df) > 0 else "N/A")
col3.metric("📏 Avg Area", f"{filtered_df['area_sqft'].mean():,.0f} sq.ft" if len(filtered_df) > 0 else "N/A")
col4.metric("💲 Avg Price/sq.ft", f"₹{filtered_df['price_per_sqft'].mean():.2f}" if len(filtered_df) > 0 else "N/A")

st.markdown("---")

if len(filtered_df) == 0:
    st.warning("⚠️ No listings found matching your filters. Try adjusting the filters.")
else:
    # Create map
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🌍 Map View")
        
        # Calculate center
        center_lat = filtered_df['latitude'].mean()
        center_lon = filtered_df['longitude'].mean()
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        # Add heatmap
        if viz_type in ["Heatmap", "Both"]:
            heat_data = [[row['latitude'], row['longitude'], row['price']/1000] 
                        for idx, row in filtered_df.iterrows()]
            HeatMap(heat_data, radius=15, blur=20, max_zoom=13).add_to(m)
        
        # Add markers
        if viz_type in ["Markers", "Both"]:
            marker_cluster = MarkerCluster().add_to(m)
            
            for idx, row in filtered_df.iterrows():
                popup_html = f"""
                <div style="font-family: Arial; width: 250px;">
                    <h4 style="color: #667eea; margin-bottom: 10px;">{row['title']}</h4>
                    <hr style="margin: 5px 0;">
                    <p><strong>🏠 BHK:</strong> {row['bhk']}</p>
                    <p><strong>💰 Rent:</strong> ₹{row['price']:,}/month</p>
                    <p><strong>📏 Area:</strong> {row['area_sqft']} sq.ft</p>
                    <p><strong>💲 Price/sq.ft:</strong> ₹{row['price_per_sqft']}</p>
                    <p><strong>📍 Location:</strong> {row['location']}</p>
                    <p><strong>🛋️ Furnishing:</strong> {row['furnishing']}</p>
                </div>
                """
                
                # Color code by price
                if row['price'] < 30000:
                    color = 'green'
                elif row['price'] < 60000:
                    color = 'orange'
                else:
                    color = 'red'
                
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"{row['title']} - ₹{row['price']:,}",
                    icon=folium.Icon(color=color, icon='home', prefix='fa')
                ).add_to(marker_cluster)
        
        folium_static(m, width=800, height=600)
    
    with col2:
        st.markdown("### 📊 Price Distribution")
        
        # Price distribution by BHK
        fig = px.box(
            filtered_df,
            x='bhk',
            y='price',
            color='bhk',
            labels={'bhk': 'BHK Type', 'price': 'Rent (₹)'},
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        fig.update_layout(
            showlegend=False,
            height=250,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Area vs Price scatter
        st.markdown("### 📈 Area vs Price")
        fig2 = px.scatter(
            filtered_df,
            x='area_sqft',
            y='price',
            color='bhk',
            size='price',
            hover_data=['location', 'furnishing'],
            labels={'area_sqft': 'Area (sq.ft)', 'price': 'Rent (₹)', 'bhk': 'BHK'},
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig2.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True)

# Listings table
st.markdown("---")
st.markdown("### 📋 Filtered Listings")

display_df = filtered_df[['title', 'bhk', 'price', 'area_sqft', 'price_per_sqft', 'location', 'furnishing']].copy()
display_df['price'] = display_df['price'].apply(lambda x: f"₹{x:,}")
display_df['price_per_sqft'] = display_df['price_per_sqft'].apply(lambda x: f"₹{x}")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "title": "Property",
        "bhk": st.column_config.NumberColumn("BHK", format="%d BHK"),
        "price": "Rent/Month",
        "area_sqft": st.column_config.NumberColumn("Area (sq.ft)", format="%d"),
        "price_per_sqft": "Price/sq.ft",
        "location": "Location",
        "furnishing": "Furnishing"
    },
    height=300
)