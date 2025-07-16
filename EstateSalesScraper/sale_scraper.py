#!/usr/bin/env python3
"""
Simplified Garage Sale & Estate Sale Scraper

This script finds real garage sales and estate sales from EstateSales.net:
- Dynamic URL construction based on location input  
- Support for city/state/ZIP combinations
- Robust HTML parsing and content filtering
- Integrated geocoding for address validation
- Real-time estate sale discovery

Usage:
    python sale_scraper.py "Grand Blanc, MI 48439"
    python sale_scraper.py "New York NY"
    python sale_scraper.py "90210"

This simplified version focuses only on EstateSales.net for maximum reliability.
Saves all listings as a list of dicts in both a JSON and TXT file.
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
import urllib.parse
import time
# Import geocode function  
from geocode import geocode

class WorkingSaleScraper:
    """Scraper for real garage sale and estate sale data."""

    import random
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.70 Safari/537.36',
    ]

    def __init__(self):
        self.session = requests.Session()
        self.rotate_user_agent()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def rotate_user_agent(self):
        ua = self.USER_AGENTS[self.random.randint(0, len(self.USER_AGENTS)-1)]
        self.session.headers.update({'User-Agent': ua})

    def add_geocode(self, listings: List[Dict[str, str]]):
        """Add latitude and longitude to each listing if possible."""
        for listing in listings:
            address = listing.get('location')
            if address:
                lat, lon = geocode(address)
                listing['latitude'] = str(lat) if lat is not None else ''
                listing['longitude'] = str(lon) if lon is not None else ''
        return listings


    # Removed: search_craigslist method - focusing only on EstateSales.net for reliability

    def search_local_newspapers(self, city: str, state: str = "", limit: int = 10) -> List[Dict[str, str]]:
        """
        This method has been removed - we now focus only on EstateSales.net for reliability.
        """
        print(f"Local newspaper scraping has been disabled. Using EstateSales.net only.")
        return []

    def search_estate_sale_companies(self, location: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search EstateSales.net for estate sales in a given location.
        Supports format: "City, State ZIP" (e.g., "Grand Blanc, MI 48439")
        or "City State" (e.g., "Grand Blanc MI") or ZIP code only.
        """
        print(f"Searching EstateSales.net for sales in {location}...")
        
        # Parse location to extract city, state, and ZIP
        location = location.strip()
        
        # Check if it's just a ZIP code
        if location.isdigit() and len(location) == 5:
            # ZIP code only - we'll need to construct a search URL or use the general format
            # For now, let's try the main site and search
            url = "https://www.estatesales.net"
            search_term = location
        else:
            # Parse city, state, ZIP combination
            if "," in location:
                # Format: "Grand Blanc, MI 48439" or "Grand Blanc, MI"
                city_part, rest = location.split(",", 1)
                city = city_part.strip().replace(" ", "-")
                rest_parts = rest.strip().split()
                
                if len(rest_parts) >= 1:
                    state = rest_parts[0].strip().upper()
                    zip_code = rest_parts[1] if len(rest_parts) > 1 else ""
                else:
                    state = ""
                    zip_code = ""
            else:
                # Format: "Grand Blanc MI" or "Grand Blanc MI 48439"
                location_parts = location.split()
                if len(location_parts) >= 2:
                    # Check if last part is ZIP code
                    if location_parts[-1].isdigit() and len(location_parts[-1]) == 5:
                        # Has ZIP code
                        zip_code = location_parts[-1]
                        state = location_parts[-2].upper() if len(location_parts) > 2 else ""
                        city = "-".join(location_parts[:-2]) if len(location_parts) > 2 else ""
                    else:
                        # No ZIP code
                        state = location_parts[-1].upper()
                        city = "-".join(location_parts[:-1])
                        zip_code = ""
                else:
                    # Single word - treat as city
                    city = location_parts[0] if location_parts else ""
                    state = ""
                    zip_code = ""
            
            # Build URL based on available information
            if city and state and zip_code:
                # Full format: https://www.estatesales.net/MI/Grand-Blanc/48439
                url = f"https://www.estatesales.net/{state}/{city}/{zip_code}"
                search_term = f"{city.replace('-', ' ')}, {state} {zip_code}"
            elif city and state:
                # City and state: https://www.estatesales.net/MI/Grand-Blanc
                url = f"https://www.estatesales.net/{state}/{city}"
                search_term = f"{city.replace('-', ' ')}, {state}"
            elif state:
                # State only: https://www.estatesales.net/MI
                url = f"https://www.estatesales.net/{state}"
                search_term = state
            else:
                # Default to main page
                url = "https://www.estatesales.net"
                search_term = location
                print(f"Warning: Could not parse location '{location}', using main page")
        
        print(f"Constructed URL: {url}")
        
        try:
            # Add random delay
            import random
            import time
            delay = random.uniform(1, 3)
            time.sleep(delay)
            
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            
            # Save HTML for debugging
            try:
                with open("estatesales_debug.html", "w", encoding="utf-8") as f:
                    f.write(resp.text)
                print(f"Saved page HTML to estatesales_debug.html for inspection")
            except Exception as e:
                print(f"Could not save debug HTML: {e}")
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Find app-sale-row elements which contain the actual listings
            sale_elements = soup.select('app-sale-row')
            print(f"Found {len(sale_elements)} app-sale-row elements")
            
            listings = []
            
            for element in sale_elements:
                try:
                    # Extract sale title from h3 element
                    title_elem = element.find('h3')
                    title = title_elem.get_text(strip=True) if title_elem else "Unknown Sale"
                    
                    # Skip if no meaningful title
                    if not title or title == "Unknown Sale":
                        continue
                    
                    # Extract URL from the main link
                    link_elem = element.find('a', class_='sale-row')
                    link = link_elem.get('href', '') if link_elem else ''
                    if link and not link.startswith('http'):
                        link = 'https://www.estatesales.net' + link
                    
                    # Extract location from address element
                    address = "Location not specified"
                    address_elem = element.find('app-sale-address')
                    if address_elem:
                        address_lines = address_elem.find_all(['div', 'span'])
                        location_parts = []
                        for line in address_lines:
                            text = line.get_text(strip=True)
                            if text:
                                location_parts.append(text)
                        if location_parts:
                            address = ', '.join(location_parts)
                    
                    # Extract date information
                    date = "Date not specified"
                    date_elem = element.find('app-sale-date')
                    if date_elem:
                        date_parts = []
                        # Look for date text
                        date_spans = date_elem.find_all(['span', 'div'])
                        for span in date_spans:
                            text = span.get_text(strip=True)
                            if text and any(month in text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                                date_parts.append(text)
                        if date_parts:
                            date = ' '.join(date_parts)
                        else:
                            # Fallback to any text in the date element
                            date = date_elem.get_text(strip=True)
                    
                    # Extract company name
                    company = "Unknown Company"
                    company_elem = element.find(class_='sale-row__listed-by')
                    if company_elem:
                        company_text = company_elem.get_text(strip=True)
                        # Remove "Listed by" prefix if present
                        if 'by ' in company_text:
                            company = company_text.split('by ', 1)[1]
                        else:
                            company = company_text
                    
                    # Extract description/details
                    description = ""
                    desc_elem = element.find(class_='sale-row__recent-info')
                    if desc_elem:
                        description = desc_elem.get_text(strip=True)
                    
                    listing = {
                        'title': title,
                        'location': address,
                        'description': description or f"Estate sale by {company}",
                        'date': date,
                        'price': '',  # EstateSales.net typically doesn't show prices in listings
                        'link': link or url,
                        'source': 'EstateSales.net'
                    }
                    
                    listings.append(listing)
                    
                except Exception as e:
                    print(f"Error extracting sale info from element: {e}")
                    continue
            
            print(f"Successfully extracted {len(listings)} estate sales")
            
            if listings:
                listings = self.add_geocode(listings)
            
            return listings[:limit]
            
        except Exception as e:
            print(f"Error searching EstateSales.net: {e}")
            return []

    # Removed: search_nextdoor_sales method - focusing only on EstateSales.net for reliability

    def display_results(self, all_listings: List[Dict[str, str]]) -> None:
        """Display all listings with full addresses and descriptions."""
        if not all_listings:
            print("No sale listings found.")
            return

        print(f"\nFound {len(all_listings)} garage sale and estate sale listings:\n")
        print("=" * 100)

        for i, listing in enumerate(all_listings, 1):
            title = listing['title']
            address = listing['location']
            description = listing.get('description', 'No description available')
            date = listing['date']
            price = listing['price']
            source = listing['source']
            link = listing.get('link', 'No link available')

            print(f"#{i} - {title}")
            print(f"Address: {address}")
            print(f"Date: {date} | Price: {price} | Source: {source}")
            print(f"Description: {description}")
            if link != 'No link available':
                print(f"Link: {link}")
            print("-" * 100)

        print(f"\nTotal listings: {len(all_listings)}")
        print(f"\nSuccessfully found real estate sales from EstateSales.net!")
        print("These are actual estate sale listings with real addresses and dates.")

    def save_listings(self, listings: List[Dict[str, str]], json_path: str, txt_path: str) -> None:
        """Save listings as JSON and TXT files."""
        with open(json_path, "w", encoding="utf-8") as f_json:
            json.dump(listings, f_json, indent=2, ensure_ascii=False)
        with open(txt_path, "w", encoding="utf-8") as f_txt:
            for entry in listings:
                f_txt.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"\nSaved {len(listings)} listings to {json_path} and {txt_path}")

def main():
    """Main function to run the simplified estate sale scraper."""

    scraper = WorkingSaleScraper()

    print("Simplified Garage Sale & Estate Sale Finder")
    print("=" * 60)
    print("This script searches for real garage sales and estate sales from:")
    print("1. EstateSales.net (primary source)")
    print("Note: Simplified to use only the most reliable source\n")

    all_listings = []

    # Check for command line arguments
    if len(sys.argv) > 1:
        # Join all arguments except the script name to handle multi-word city names
        arg = " ".join(sys.argv[1:])

        print(f"Searching for sales in location: {arg}")
        estate_listings = scraper.search_estate_sale_companies(arg, limit=15)
        all_listings.extend(estate_listings)

    else:
        # Default search - use a sample location
        print("Performing default search for Grand Blanc, MI...")
        estate_listings = scraper.search_estate_sale_companies("Grand Blanc, MI 48439", limit=15)
        all_listings.extend(estate_listings)

    # Display results
    scraper.display_results(all_listings)

    # Save results to files
    scraper.save_listings(all_listings, "scraped_sales.json", "scraped_sales.txt")

    print(f"\nUsage examples:")
    print("1. Search by ZIP code: python sale_scraper.py 48439")
    print("2. Search by city and state: python sale_scraper.py Grand Blanc MI")
    print("3. Search with full format: python sale_scraper.py Grand Blanc, MI 48439")
    print("4. Search by multi-word city: python sale_scraper.py New York NY")
    print("5. Default search: python sale_scraper.py")
    print("\nThis script now focuses solely on EstateSales.net for maximum reliability.")

if __name__ == "__main__":
    main()
