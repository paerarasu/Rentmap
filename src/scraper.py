import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from pathlib import Path

class RentalScraper:
    """Web scraper for rental listings"""
    
    def __init__(self, base_url=None):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        
    def scrape_page(self, url):
        """Scrape a single page"""
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def extract_price(self, text):
        """Extract price from text"""
        if not text:
            return None
        price = re.findall(r'[\d,]+', text.replace(',', ''))
        return int(price[0]) if price else None
    
    def extract_bhk(self, text):
        """Extract BHK from text"""
        if not text:
            return None
        bhk = re.findall(r'(\d+)\s*BHK', text.upper())
        return int(bhk[0]) if bhk else None
    
    def extract_area(self, text):
        """Extract area in sqft"""
        if not text:
            return None
        area = re.findall(r'([\d,]+)\s*(?:sq\.?\s*ft|sqft)', text.lower())
        return int(area[0].replace(',', '')) if area else None
    
    def parse_listing(self, listing_element):
        """Parse individual listing element"""
        try:
            # This is a template - adjust selectors based on actual website
            title = listing_element.select_one('.listing-title')
            price = listing_element.select_one('.price')
            location = listing_element.select_one('.location')
            details = listing_element.select_one('.details')
            
            return {
                'title': title.text.strip() if title else None,
                'price': self.extract_price(price.text) if price else None,
                'location': location.text.strip() if location else None,
                'bhk': self.extract_bhk(details.text) if details else None,
                'area_sqft': self.extract_area(details.text) if details else None,
            }
        except Exception as e:
            print(f"Error parsing listing: {e}")
            return None
    
    def scrape_multiple_pages(self, base_url, num_pages=5):
        """Scrape multiple pages"""
        all_listings = []
        
        for page in range(1, num_pages + 1):
            print(f"Scraping page {page}...")
            url = f"{base_url}?page={page}"
            soup = self.scrape_page(url)
            
            if not soup:
                continue
            
            # Adjust selector based on actual website
            listings = soup.select('.listing-item')
            
            for listing in listings:
                parsed = self.parse_listing(listing)
                if parsed:
                    all_listings.append(parsed)
            
            time.sleep(2)  # Respectful scraping
        
        return pd.DataFrame(all_listings)
    
    def save_data(self, df, filename='raw_rentals.csv'):
        """Save scraped data"""
        output_dir = Path('data/raw')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / filename
        df.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")
        return filepath

# Example usage
if __name__ == "__main__":
    scraper = RentalScraper()
    
    # Generate sample data for testing
    sample_data = pd.DataFrame({
        'title': [
            '2 BHK Apartment in Vasant Kunj',
            '3 BHK Villa in Defence Colony',
            '1 BHK Flat in Karol Bagh',
            '2 BHK Apartment in Dwarka',
            '3 BHK Penthouse in Greater Kailash'
        ],
        'price': [35000, 75000, 18000, 28000, 95000],
        'location': ['Vasant Kunj', 'Defence Colony', 'Karol Bagh', 'Dwarka', 'Greater Kailash'],
        'bhk': [2, 3, 1, 2, 3],
        'area_sqft': [1200, 2500, 600, 1100, 2800]
    })
    
    scraper.save_data(sample_data)
    print("Sample data generated successfully!")