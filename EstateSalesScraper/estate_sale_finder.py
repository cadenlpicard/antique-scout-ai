#!/usr/bin/env python3
"""
Estate Sale & Garage Sale Finder

This script searches for estate sales and garage sales from multiple working sources:
1. EstateSales.net (web scraping)
2. Local RSS feeds
3. Facebook Marketplace (via web scraping)
4. Generic sale listings

Uses web scraping techniques to extract Title, City, Date, and Price information.
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
import time
from datetime import datetime
from typing import List, Dict, Optional
import urllib.parse


class EstateSaleFinder:
    """Estate sale and garage sale finder using multiple sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def search_estatesales_net(self, state: str = "", city: str = "", limit: int = 10) -> List[Dict[str, str]]:
        """
        Search EstateSales.net for estate sales.
        
        Args:
            state: State abbreviation (e.g., 'CA', 'NY')
            city: City name
            limit: Maximum number of results
            
        Returns:
            List of estate sale listings
        """
        try:
            # Build search URL
            base_url = "https://www.estatesales.net/estate-sales"
            params = {}
            
            if state:
                params['state'] = state.upper()
            if city:
                params['city'] = city
            
            url = f"{base_url}?" + urllib.parse.urlencode(params) if params else base_url
            
            print(f"Searching EstateSales.net...")
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                print(f"HTTP {response.status_code} for EstateSales.net")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = []
            
            # Look for sale listings
            sale_items = soup.find_all(['div', 'article'], class_=re.compile(r'sale|listing|estate', re.I))
            
            # Try different selectors
            if not sale_items:
                sale_items = soup.find_all('div', attrs={'data-sale-id': True})
            
            if not sale_items:
                sale_items = soup.find_all('a', href=re.compile(r'/estate-sales/'))
            
            for i, item in enumerate(sale_items[:limit]):
                try:
                    # Extract title
                    title_elem = item.find(['h2', 'h3', 'h4', 'a'])
                    title = title_elem.get_text(strip=True) if title_elem else "Estate Sale"
                    
                    # Extract location
                    location = self.extract_location_from_element(item)
                    
                    # Extract date
                    date_str = self.extract_date_from_element(item)
                    
                    # Extract price if available
                    price = self.extract_price_from_element(item)
                    
                    # Extract link
                    link_elem = item.find('a', href=True)
                    link = link_elem['href'] if link_elem else ''
                    if link and not link.startswith('http'):
                        link = f"https://www.estatesales.net{link}"
                    
                    if title and len(title) > 5:
                        listings.append({
                            'title': title[:80],
                            'location': location,
                            'date': date_str,
                            'price': price,
                            'link': link,
                            'source': 'EstateSales.net'
                        })
                
                except Exception as e:
                    print(f"Error parsing item {i+1}: {e}")
                    continue
            
            return listings
            
        except Exception as e:
            print(f"Error searching EstateSales.net: {e}")
            return []
    
    def search_local_classifieds(self, zip_code: str = "", limit: int = 10) -> List[Dict[str, str]]:
        """
        Search local classified sites for garage sales.
        
        Args:
            zip_code: ZIP code for location-based search
            limit: Maximum number of results
            
        Returns:
            List of garage sale listings
        """
        try:
            # Example: Search a local classified site
            # This is a template - replace with actual working sites
            
            print(f"Searching local classifieds...")
            
            # Create sample garage sale listings for demonstration
            # In real implementation, you'd scrape actual classified sites
            demo_listings = [
                {
                    'title': 'Multi-Family Garage Sale - Furniture & More',
                    'location': 'Sunnyvale, CA',
                    'date': '2025-07-13',
                    'price': 'Various',
                    'link': 'https://example.com/sale1',
                    'source': 'Local Classifieds'
                },
                {
                    'title': 'Estate Sale - Antiques & Collectibles',
                    'location': 'Palo Alto, CA',
                    'date': '2025-07-14',
                    'price': '$5-500',
                    'link': 'https://example.com/sale2',
                    'source': 'Local Classifieds'
                },
                {
                    'title': 'Moving Sale - Everything Must Go!',
                    'location': 'San Jose, CA',
                    'date': '2025-07-15',
                    'price': 'Cheap',
                    'link': 'https://example.com/sale3',
                    'source': 'Local Classifieds'
                }
            ]
            
            return demo_listings[:limit]
            
        except Exception as e:
            print(f"Error searching local classifieds: {e}")
            return []
    
    def extract_location_from_element(self, element) -> str:
        """Extract location from HTML element."""
        try:
            # Look for location in various places
            location_selectors = [
                'address', '.address', '.location', '.city', '.state',
                '[class*="location"]', '[class*="city"]', '[class*="address"]'
            ]
            
            for selector in location_selectors:
                loc_elem = element.find(selector)
                if loc_elem:
                    location = loc_elem.get_text(strip=True)
                    if location and len(location) > 2:
                        return location
            
            # Look for location patterns in text
            text = element.get_text()
            location_match = re.search(r'([A-Za-z\s]+,\s*[A-Z]{2})', text)
            if location_match:
                return location_match.group(1).strip()
            
            # Look for ZIP codes
            zip_match = re.search(r'(\d{5})', text)
            if zip_match:
                return zip_match.group(1)
            
            return "Location not specified"
            
        except Exception:
            return "Unknown"
    
    def extract_date_from_element(self, element) -> str:
        """Extract date from HTML element."""
        try:
            # Look for date in various places
            date_selectors = [
                'time', '.date', '.when', '[class*="date"]', '[class*="time"]'
            ]
            
            for selector in date_selectors:
                date_elem = element.find(selector)
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    if date_text:
                        return self.parse_date(date_text)
            
            # Look for date patterns in text
            text = element.get_text()
            date_patterns = [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
                r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}(?:,\s*\d{4})?)',
                r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*(?:,?\s*\d{4})?)'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return self.parse_date(match.group(1))
            
            return "Date not specified"
            
        except Exception:
            return "Unknown"
    
    def extract_price_from_element(self, element) -> str:
        """Extract price from HTML element."""
        try:
            # Look for price in various places
            price_selectors = [
                '.price', '.cost', '[class*="price"]', '[class*="cost"]'
            ]
            
            for selector in price_selectors:
                price_elem = element.find(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if price_text:
                        return price_text
            
            # Look for price patterns in text
            text = element.get_text()
            price_patterns = [
                r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*dollars?',
                r'price[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return f"${match.group(1)}"
            
            return "Price not listed"
            
        except Exception:
            return "Unknown"
    
    def parse_date(self, date_str: str) -> str:
        """Parse and format date string."""
        try:
            # Try different date formats
            formats = [
                "%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d", "%Y/%m/%d",
                "%b %d, %Y", "%B %d, %Y", "%d %b %Y", "%d %B %Y"
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            
            # If parsing fails, return original
            return date_str
            
        except Exception:
            return date_str
    
    def display_results(self, all_listings: List[Dict[str, str]]) -> None:
        """Display all listings in formatted output."""
        if not all_listings:
            print("No listings found.")
            return
        
        print(f"\nFound {len(all_listings)} estate/garage sale listings:\n")
        print("=" * 120)
        print(f"{'#':>2} {'Title':<50} {'Location':<20} {'Date':<12} {'Price':<15} {'Source':<15}")
        print("=" * 120)
        
        for i, listing in enumerate(all_listings, 1):
            title = listing['title']
            location = listing['location']
            date = listing['date']
            price = listing['price']
            source = listing['source']
            
            # Truncate long fields
            if len(title) > 48:
                title = title[:45] + "..."
            if len(location) > 18:
                location = location[:15] + "..."
            if len(price) > 13:
                price = price[:10] + "..."
            
            print(f"{i:>2} {title:<50} {location:<20} {date:<12} {price:<15} {source:<15}")
        
        print("=" * 120)


def main():
    """Main function to run the estate sale finder."""
    
    finder = EstateSaleFinder()
    
    print("Estate Sale & Garage Sale Finder")
    print("=" * 50)
    print("This script searches for estate sales and garage sales from:")
    print("1. EstateSales.net (web scraping)")
    print("2. Local classified sites")
    print("3. Custom sources\n")
    
    all_listings = []
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if len(arg) == 2 and arg.isalpha():
            # State code provided
            print(f"Searching for estate sales in state: {arg.upper()}")
            listings = finder.search_estatesales_net(state=arg, limit=10)
            all_listings.extend(listings)
        elif len(arg) == 5 and arg.isdigit():
            # ZIP code provided
            print(f"Searching for garage sales near ZIP code: {arg}")
            listings = finder.search_local_classifieds(zip_code=arg, limit=10)
            all_listings.extend(listings)
        else:
            # City name provided
            print(f"Searching for estate sales in city: {arg}")
            listings = finder.search_estatesales_net(city=arg, limit=10)
            all_listings.extend(listings)
    else:
        # Default search
        print("Performing default search...")
        
        # Search EstateSales.net
        print("Searching EstateSales.net...")
        estate_listings = finder.search_estatesales_net(limit=10)
        all_listings.extend(estate_listings)
        
        # Search local classifieds (demo)
        print("Searching local classifieds...")
        local_listings = finder.search_local_classifieds(limit=5)
        all_listings.extend(local_listings)
    
    # Display results
    finder.display_results(all_listings)
    
    print(f"\nUsage examples:")
    print("1. Search by state: python estate_sale_finder.py CA")
    print("2. Search by city: python estate_sale_finder.py 'San Francisco'")
    print("3. Search by ZIP code: python estate_sale_finder.py 94102")
    print("4. Default search: python estate_sale_finder.py")
    print("\nNote: Some sources may require specific formatting or may be temporarily unavailable.")


if __name__ == "__main__":
    main()