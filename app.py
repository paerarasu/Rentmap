import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json

# Page config
st.set_page_config(
    page_title="RentMap - Real-Time Rent Explorer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .info-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/processed/rentals_processed.csv')
    except:
        # Create sample data if file doesn't exist
        df = pd.DataFrame({
            'title': ['2 BHK Apartment in Vasant Kunj', '3 BHK Villa in Defence Colony', 
                     '1 BHK Flat in Karol Bagh', '2 BHK Apartment in Dwarka',
                     '3 BHK Penthouse in Greater Kailash', '1 BHK Studio in Lajpat Nagar',
                     '2 BHK Apartment in Rohini', '4 BHK Villa in Chanakyapuri'],
            'bhk': [2, 3, 1, 2, 3, 1, 2, 4],
            'price': [35000, 75000, 18000, 28000, 95000, 15000, 25000, 150000],
            'area_sqft': [1200, 2500, 600, 1100, 2800, 500, 1000, 3500],
            'location': ['Vasant Kunj', 'Defence Colony', 'Karol Bagh', 'Dwarka', 
                        'Greater Kailash', 'Lajpat Nagar', 'Rohini', 'Chanakyapuri'],
            'latitude': [28.5217, 28.5675, 28.6517, 28.5921, 28.5494, 28.5678, 28.7489, 28.5983],
            'longitude': [77.1587, 77.2376, 77.1905, 77.0460, 77.2466, 77.2434, 77.1177, 77.1892],
            'furnishing': ['Semi-Furnished', 'Furnished', 'Unfurnished', 'Semi-Furnished',
                          'Fully Furnished', 'Semi-Furnished', 'Unfurnished', 'Fully Furnished']
        })
        df['price_per_sqft'] = (df['price'] / df['area_sqft']).round(2)
        # Save sample data
        Path('data/processed').mkdir(parents=True, exist_ok=True)
        df.to_csv('data/processed/rentals_processed.csv', index=False)
    return df

df = load_data()

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/home.png", width=80)
    st.title("🏠 RentMap")
    st.markdown("---")
    st.markdown("### 📍 Navigation")
    st.info("Use the sidebar to navigate between pages")
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Stats")
    st.metric("Total Listings", len(df))
    st.metric("Avg Rent", f"₹{df['price'].mean():,.0f}")
    st.metric("Areas Covered", df['location'].nunique())

# Main content
st.markdown('<h1 class="main-header">🏠 RentMap</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Real-Time Rent & Cost of Living Explorer</p>', unsafe_allow_html=True)

st.markdown("---")

# Metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin:0;">₹{df['price'].mean():,.0f}</h3>
        <p style="margin:0; opacity:0.9;">Average Rent</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin:0;">₹{df['price'].min():,.0f} - ₹{df['price'].max():,.0f}</h3>
        <p style="margin:0; opacity:0.9;">Price Range</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin:0;">{df['location'].nunique()}</h3>
        <p style="margin:0; opacity:0.9;">Locations</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin:0;">{len(df)}</h3>
        <p style="margin:0; opacity:0.9;">Total Listings</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("##")

# Overview section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 📊 Rent Distribution by BHK")
    
    # BHK distribution chart
    bhk_data = df.groupby('bhk').agg({
        'price': 'mean',
        'title': 'count'
    }).reset_index()
    bhk_data.columns = ['BHK', 'Avg_Price', 'Count']
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bhk_data['BHK'],
        y=bhk_data['Avg_Price'],
        marker_color='#667eea',
        text=bhk_data['Avg_Price'].apply(lambda x: f'₹{x:,.0f}'),
        textposition='outside',
        name='Avg Price'
    ))
    
    fig.update_layout(
        xaxis_title="BHK Type",
        yaxis_title="Average Rent (₹)",
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("## 🏘️ Top Locations")
    
    top_locations = df.groupby('location')['price'].agg(['mean', 'count']).sort_values('mean', ascending=False).head(5)
    
    for idx, (location, row) in enumerate(top_locations.iterrows(), 1):
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #667eea;">
            <strong>{idx}. {location}</strong><br>
            <span style="color: #667eea; font-size: 1.1rem;">₹{row['mean']:,.0f}</span> 
            <span style="color: #999; font-size: 0.9rem;">({int(row['count'])} listings)</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Feature cards
st.markdown("## 🎯 Explore RentMap Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-card">
        <h3>🗺️ Interactive Explorer</h3>
        <p>Visualize rental listings on an interactive map with heatmaps, filters, and detailed popups</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <h3>📊 Area Comparison</h3>
        <p>Compare rent prices across different locations with detailed charts and analytics</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-card">
        <h3>💡 Smart Insights</h3>
        <p>Get data-driven insights about rental trends, pricing patterns, and market analysis</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("##")

# Recent listings
st.markdown("## 📋 Recent Listings")

display_df = df[['title', 'bhk', 'price', 'area_sqft', 'price_per_sqft', 'location', 'furnishing']].head(10)
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
    }
)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🏠 RentMap - Making Rental Decisions Easier</p>
    <p style="font-size: 0.9rem;">Built with Streamlit • Data updates in real-time</p>
</div>
""", unsafe_allow_html=True)