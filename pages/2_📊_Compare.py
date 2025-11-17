import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Compare - RentMap", page_icon="📊", layout="wide")

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
st.markdown('<h1 style="text-align: center; color: #667eea;">📊 Location & Price Comparison</h1>', unsafe_allow_html=True)
st.markdown("---")

# Comparison selector
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📍 Select Locations to Compare")
    selected_locations = st.multiselect(
        "Choose 2-5 locations",
        options=sorted(df['location'].unique()),
        default=list(sorted(df['location'].unique())[:3]),
        max_selections=5
    )

with col2:
    st.markdown("### 🏠 Select BHK Types")
    selected_bhk = st.multiselect(
        "Filter by BHK",
        options=sorted(df['bhk'].unique()),
        default=sorted(df['bhk'].unique())
    )

if len(selected_locations) < 2:
    st.warning("⚠️ Please select at least 2 locations to compare")
    st.stop()

# Filter data
comparison_df = df[
    (df['location'].isin(selected_locations)) &
    (df['bhk'].isin(selected_bhk))
]

if len(comparison_df) == 0:
    st.error("❌ No data found for selected filters")
    st.stop()

st.markdown("---")

# Summary metrics
st.markdown("## 📈 Comparison Summary")

location_stats = comparison_df.groupby('location').agg({
    'price': ['mean', 'min', 'max', 'count'],
    'area_sqft': 'mean',
    'price_per_sqft': 'mean'
}).round(2)

location_stats.columns = ['Avg Rent', 'Min Rent', 'Max Rent', 'Listings', 'Avg Area', 'Avg Price/sqft']

cols = st.columns(len(selected_locations))
for idx, location in enumerate(selected_locations):
    if location in location_stats.index:
        stats = location_stats.loc[location]
        with cols[idx]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1.5rem; border-radius: 10px; color: white;">
                <h3 style="margin: 0 0 1rem 0;">{location}</h3>
                <p style="font-size: 1.5rem; margin: 0.5rem 0;"><strong>₹{stats['Avg Rent']:,.0f}</strong></p>
                <p style="font-size: 0.9rem; opacity: 0.9; margin: 0;">Average Rent</p>
                <hr style="margin: 1rem 0; opacity: 0.3;">
                <p style="margin: 0.3rem 0;">📋 {int(stats['Listings'])} listings</p>
                <p style="margin: 0.3rem 0;">📏 {stats['Avg Area']:.0f} sq.ft avg</p>
                <p style="margin: 0.3rem 0;">💲 ₹{stats['Avg Price/sqft']:.2f}/sq.ft</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💰 Average Rent Comparison")
    
    avg_rent = comparison_df.groupby('location')['price'].mean().reset_index()
    avg_rent = avg_rent.sort_values('price', ascending=False)
    
    fig1 = px.bar(
        avg_rent,
        x='location',
        y='price',
        color='price',
        color_continuous_scale='Viridis',
        labels={'location': 'Location', 'price': 'Average Rent (₹)'},
        text='price'
    )
    fig1.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
    fig1.update_layout(
        showlegend=False,
        height=400,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### 📊 Rent Distribution by Location")
    
    fig2 = px.box(
        comparison_df,
        x='location',
        y='price',
        color='location',
        labels={'location': 'Location', 'price': 'Rent (₹)'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig2.update_layout(
        showlegend=False,
        height=400,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig2, use_container_width=True)

# BHK-wise comparison
st.markdown("---")
st.markdown("### 🏠 BHK-wise Comparison Across Locations")

bhk_comparison = comparison_df.groupby(['location', 'bhk'])['price'].mean().reset_index()

fig3 = px.bar(
    bhk_comparison,
    x='location',
    y='price',
    color='bhk',
    barmode='group',
    labels={'location': 'Location', 'price': 'Average Rent (₹)', 'bhk': 'BHK Type'},
    color_discrete_sequence=px.colors.qualitative.Pastel,
    text='price'
)
fig3.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
fig3.update_layout(
    height=450,
    xaxis_tickangle=-45,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig3, use_container_width=True)

# Area vs Price comparison
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📏 Average Area Comparison")
    
    avg_area = comparison_df.groupby('location')['area_sqft'].mean().reset_index()
    avg_area = avg_area.sort_values('area_sqft', ascending=True)
    
    fig4 = px.bar(
        avg_area,
        x='area_sqft',
        y='location',
        orientation='h',
        color='area_sqft',
        color_continuous_scale='Blues',
        labels={'location': 'Location', 'area_sqft': 'Average Area (sq.ft)'},
        text='area_sqft'
    )
    fig4.update_traces(texttemplate='%{text:.0f} sq.ft', textposition='outside')
    fig4.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.markdown("### 💲 Price per Sq.Ft Comparison")
    
    avg_price_sqft = comparison_df.groupby('location')['price_per_sqft'].mean().reset_index()
    avg_price_sqft = avg_price_sqft.sort_values('price_per_sqft', ascending=True)
    
    fig5 = px.bar(
        avg_price_sqft,
        x='price_per_sqft',
        y='location',
        orientation='h',
        color='price_per_sqft',
        color_continuous_scale='Reds',
        labels={'location': 'Location', 'price_per_sqft': 'Price per Sq.Ft (₹)'},
        text='price_per_sqft'
    )
    fig5.update_traces(texttemplate='₹%{text:.2f}', textposition='outside')
    fig5.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig5, use_container_width=True)

# Detailed comparison table
st.markdown("---")
st.markdown("### 📋 Detailed Comparison Table")

comparison_table = comparison_df.groupby('location').agg({
    'price': ['mean', 'min', 'max'],
    'area_sqft': 'mean',
    'price_per_sqft': 'mean',
    'title': 'count'
}).round(2)

comparison_table.columns = ['Avg Rent (₹)', 'Min Rent (₹)', 'Max Rent (₹)', 
                           'Avg Area (sq.ft)', 'Avg Price/sq.ft (₹)', 'Total Listings']

st.dataframe(
    comparison_table.style.format({
        'Avg Rent (₹)': '₹{:,.0f}',
        'Min Rent (₹)': '₹{:,.0f}',
        'Max Rent (₹)': '₹{:,.0f}',
        'Avg Area (sq.ft)': '{:.0f}',
        'Avg Price/sq.ft (₹)': '₹{:.2f}',
        'Total Listings': '{:.0f}'
    }).background_gradient(cmap='YlOrRd', subset=['Avg Rent (₹)']),
    use_container_width=True
)

# Insights
st.markdown("---")
st.markdown("### 💡 Key Insights")

most_expensive = comparison_table['Avg Rent (₹)'].idxmax()
least_expensive = comparison_table['Avg Rent (₹)'].idxmin()
largest_area = comparison_table['Avg Area (sq.ft)'].idxmax()
most_listings = comparison_table['Total Listings'].idxmax()

col1, col2 = st.columns(2)

with col1:
    st.info(f"""
    **🏆 Most Expensive:** {most_expensive} (₹{comparison_table.loc[most_expensive, 'Avg Rent (₹)']:,.0f})
    
    **💚 Most Affordable:** {least_expensive} (₹{comparison_table.loc[least_expensive, 'Avg Rent (₹)']:,.0f})
    """)

with col2:
    st.success(f"""
    **📏 Largest Average Area:** {largest_area} ({comparison_table.loc[largest_area, 'Avg Area (sq.ft)']:.0f} sq.ft)
    
    **📋 Most Listings:** {most_listings} ({int(comparison_table.loc[most_listings, 'Total Listings'])} properties)
    """)