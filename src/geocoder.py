import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import json
from pathlib import Path

class LocationGeocoder:
    """Geocode rental listings with caching"""
    
    def __init__(self, cache_file='data/geocode_cache.json'):
        self.geolocator = Nominatim(user_agent="rentmap_geocoder")
        self.cache_file = Path(cache_file)
        self.cache = self.load_cache()
        
    def load_cache(self):
        """Load geocoding cache"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_cache(self):
        """Save geocoding cache"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def geocode_location(self, location, city="Delhi", country="India"):
        """Geocode a single location with retry logic"""
        # Check cache first
        cache_key = f"{location}, {city}, {country}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try geocoding with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                full_address = f"{location}, {city}, {country}"
                location_data = self.geolocator.geocode(full_address, timeout=10)
                
                if location_data:
                    result = {
                        'latitude': location_data.latitude,
                        'longitude': location_data.longitude,
                        'display_name': location_data.address
                    }
                    
                    # Cache the result
                    self.cache[cache_key] = result
                    self.save_cache()
                    
                    time.sleep(1)  # Respect rate limits
                    return result
                else:
                    print(f"Location not found: {location}")
                    return None
                    
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                print(f"Geocoding error (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(2)
                
        return None
    
    def geocode_dataframe(self, df, location_column='location', 
                         city="Delhi", country="India"):
        """Geocode all locations in a dataframe"""
        print(f"Starting geocoding for {len(df)} locations...")
        
        # Initialize columns
        df['latitude'] = None
        df['longitude'] = None
        
        unique_locations = df[location_column].unique()
        print(f"Found {len(unique_locations)} unique locations")
        
        location_coords = {}
        
        for idx, location in enumerate(unique_locations, 1):
            print(f"Geocoding ({idx}/{len(unique_locations)}): {location}")
            
            coords = self.geocode_location(location, city, country)
            
            if coords:
                location_coords[location] = coords
                print(f"  ✓ Found: ({coords['latitude']}, {coords['longitude']})")
            else:
                # Use default Delhi coordinates if geocoding fails
                location_coords[location] = {
                    'latitude': 28.6139 + (idx * 0.01),  # Slight offset for each location
                    'longitude': 77.2090 + (idx * 0.01)
                }
                print(f"  ⚠ Using default coordinates")
        
        # Apply coordinates to dataframe
        for location, coords in location_coords.items():
            mask = df[location_column] == location
            df.loc[mask, 'latitude'] = coords['latitude']
            df.loc[mask, 'longitude'] = coords['longitude']
        
        print(f"Geocoding complete. {len(location_coords)} locations processed.")
        return df
    
    def add_sample_coordinates(self, df, location_column='location'):
        """Add sample coordinates for demo purposes"""
        # Sample coordinates for common Delhi locations
        delhi_coords = {
            'Vasant Kunj': (28.5217, 77.1587),
            'Defence Colony': (28.5675, 77.2376),
            'Karol Bagh': (28.6517, 77.1905),
            'Dwarka': (28.5921, 77.0460),
            'Greater Kailash': (28.5494, 77.2466),
            'Lajpat Nagar': (28.5678, 77.2434),
            'Rohini': (28.7489, 77.1177),
            'Chanakyapuri': (28.5983, 77.1892),
            'Janakpuri': (28.6219, 77.0919),
            'Saket': (28.5244, 77.2066),
            'Connaught Place': (28.6304, 77.2177),
            'Nehru Place': (28.5494, 77.2501),
            'Pitampura': (28.7000, 77.1311),
            'Mayur Vihar': (28.6078, 77.2952),
            'Noida': (28.5355, 77.3910)
        }
        
        df['latitude'] = None
        df['longitude'] = None
        
        for location, (lat, lon) in delhi_coords.items():
            mask = df[location_column] == location
            df.loc[mask, 'latitude'] = lat
            df.loc[mask, 'longitude'] = lon
        
        # For locations not in our sample dict, use approximate coordinates
        missing_coords = df['latitude'].isna()
        if missing_coords.any():
            df.loc[missing_coords, 'latitude'] = 28.6139
            df.loc[missing_coords, 'longitude'] = 77.2090
        
        return df

# Example usage
if __name__ == "__main__":
    # Load processed data
    df = pd.read_csv('data/processed/rentals_processed.csv')
    
    # Initialize geocoder
    geocoder = LocationGeocoder()
    
    # Add coordinates (using sample for demo)
    df = geocoder.add_sample_coordinates(df)
    
    # Save with coordinates
    df.to_csv('data/processed/rentals_processed.csv', index=False)
    print("\nData with coordinates saved!")
    print("\nSample:")
    print(df[['location', 'latitude', 'longitude']].head())