import pandas as pd
import numpy as np
from pathlib import Path
import re

class DataProcessor:
    """Clean and process rental data"""
    
    def __init__(self, input_file=None):
        self.input_file = input_file
        self.df = None
        
    def load_data(self, filepath=None):
        """Load raw data"""
        if filepath:
            self.df = pd.read_csv(filepath)
        elif self.input_file:
            self.df = pd.read_csv(self.input_file)
        else:
            raise ValueError("No input file specified")
        return self.df
    
    def remove_duplicates(self):
        """Remove duplicate listings"""
        before = len(self.df)
        self.df = self.df.drop_duplicates(subset=['title', 'location'], keep='first')
        after = len(self.df)
        print(f"Removed {before - after} duplicates")
        return self.df
    
    def handle_missing_values(self):
        """Handle missing values"""
        # Drop rows with missing critical fields
        critical_fields = ['title', 'price', 'location']
        self.df = self.df.dropna(subset=critical_fields)
        
        # Fill missing BHK with mode
        if 'bhk' in self.df.columns:
            self.df['bhk'].fillna(self.df['bhk'].mode()[0], inplace=True)
        
        # Fill missing area with median
        if 'area_sqft' in self.df.columns:
            self.df['area_sqft'].fillna(self.df['area_sqft'].median(), inplace=True)
        
        print(f"Handled missing values. Remaining records: {len(self.df)}")
        return self.df
    
    def clean_price(self):
        """Clean and standardize price"""
        if 'price' not in self.df.columns:
            return self.df
        
        # Remove outliers using IQR method
        Q1 = self.df['price'].quantile(0.25)
        Q3 = self.df['price'].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        
        before = len(self.df)
        self.df = self.df[(self.df['price'] >= lower_bound) & (self.df['price'] <= upper_bound)]
        after = len(self.df)
        
        print(f"Removed {before - after} price outliers")
        return self.df
    
    def clean_text_fields(self):
        """Clean text fields"""
        text_columns = ['title', 'location']
        
        for col in text_columns:
            if col in self.df.columns:
                # Remove extra whitespace
                self.df[col] = self.df[col].str.strip()
                self.df[col] = self.df[col].str.replace(r'\s+', ' ', regex=True)
                
                # Standardize case for location
                if col == 'location':
                    self.df[col] = self.df[col].str.title()
        
        return self.df
    
    def calculate_derived_metrics(self):
        """Calculate additional metrics"""
        if 'price' in self.df.columns and 'area_sqft' in self.df.columns:
            self.df['price_per_sqft'] = (self.df['price'] / self.df['area_sqft']).round(2)
        
        return self.df
    
    def add_furnishing_status(self):
        """Add furnishing status if not present"""
        if 'furnishing' not in self.df.columns:
            furnishing_options = ['Unfurnished', 'Semi-Furnished', 'Fully Furnished']
            self.df['furnishing'] = np.random.choice(furnishing_options, size=len(self.df))
        
        return self.df
    
    def validate_data(self):
        """Validate processed data"""
        issues = []
        
        # Check for negative values
        if (self.df['price'] < 0).any():
            issues.append("Negative prices found")
        
        if 'area_sqft' in self.df.columns and (self.df['area_sqft'] < 0).any():
            issues.append("Negative area values found")
        
        # Check for reasonable ranges
        if (self.df['price'] < 1000).any():
            issues.append("Suspiciously low prices found")
        
        if (self.df['price'] > 10000000).any():
            issues.append("Suspiciously high prices found")
        
        if issues:
            print("Data validation warnings:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("Data validation passed ✓")
        
        return self.df
    
    def process_all(self):
        """Run complete processing pipeline"""
        print("Starting data processing pipeline...")
        
        self.remove_duplicates()
        self.handle_missing_values()
        self.clean_price()
        self.clean_text_fields()
        self.calculate_derived_metrics()
        self.add_furnishing_status()
        self.validate_data()
        
        print(f"Processing complete. Final dataset: {len(self.df)} records")
        return self.df
    
    def save_processed_data(self, filename='rentals_processed.csv'):
        """Save processed data"""
        output_dir = Path('data/processed')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / filename
        self.df.to_csv(filepath, index=False)
        print(f"Processed data saved to {filepath}")
        return filepath

# Example usage
if __name__ == "__main__":
    # Create sample data
    sample_data = pd.DataFrame({
        'title': [
            '2 BHK Apartment in Vasant Kunj',
            '3 BHK Villa in Defence Colony',
            '1 BHK Flat in Karol Bagh',
            '2 BHK Apartment in Dwarka',
            '3 BHK Penthouse in Greater Kailash',
            '1 BHK Studio in Lajpat Nagar',
            '2 BHK Apartment in Rohini',
            '4 BHK Villa in Chanakyapuri'
        ],
        'price': [35000, 75000, 18000, 28000, 95000, 15000, 25000, 150000],
        'location': ['Vasant Kunj', 'Defence Colony', 'Karol Bagh', 'Dwarka', 
                     'Greater Kailash', 'Lajpat Nagar', 'Rohini', 'Chanakyapuri'],
        'bhk': [2, 3, 1, 2, 3, 1, 2, 4],
        'area_sqft': [1200, 2500, 600, 1100, 2800, 500, 1000, 3500]
    })
    
    # Save raw data
    Path('data/raw').mkdir(parents=True, exist_ok=True)
    sample_data.to_csv('data/raw/raw_rentals.csv', index=False)
    
    # Process data
    processor = DataProcessor('data/raw/raw_rentals.csv')
    processor.load_data()
    processor.process_all()
    processor.save_processed_data()
    
    print("\nSample processed data:")
    print(processor.df.head())