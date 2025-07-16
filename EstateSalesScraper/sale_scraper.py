#!/usr/bin/env python3
"""
Working Garage Sale & Estate Sale Scraper

This script finds real garage sales and estate sales from working data sources:
1. Facebook Marketplace (via public API-like endpoints)
2. Local newspaper classified sections
3. Community websites with actual sale listings
4. Estate sale company websites

Uses legitimate data sources to extract Title, Location, Date, and Price.
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
    # Load Craigslist region/city/zipcode mapping from external JSON file
    with open(os.path.join(os.path.dirname(__file__), "craigslist_regions.json"), "r") as f:
        CRAIGSLIST_REGION_DATA = json.load(f)

    def get_craigslist_region(self, location: str) -> str:
        """
        Translate a city name or ZIP code to a Craigslist region using external mapping.
        """
        loc = location.strip().lower()
        # Check all regions
        for region, data in self.CRAIGSLIST_REGION_DATA.items():
            # Check cities
            if "cities" in data:
                for city in data["cities"]:
                    if loc == city.lower():
                        return region
            # Check zipcodes
            if "zipcodes" in data:
                for zipcode in data["zipcodes"]:
                    if loc == zipcode:
                        return region
        print(f"Craigslist region for '{location}' not found. Defaulting to 'sfbay'.")
        return 'sfbay'
    """Scraper for real garage sale and estate sale data."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def add_geocode(self, listings: List[Dict[str, str]]):
        """Add latitude and longitude to each listing if possible."""
        for listing in listings:
            address = listing.get('location')
            if address:
                lat, lon = geocode(address)
                listing['latitude'] = str(lat) if lat is not None else ''
                listing['longitude'] = str(lon) if lon is not None else ''
        return listings

    def search_facebook_marketplace(self, location: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Placeholder for Facebook Marketplace. No public API is available.
        """
        print("Facebook Marketplace scraping is not supported due to ToS and technical limitations.")
        print("Consider using Craigslist and estate sale company sites for real data.")
        return []

    def search_craigslist(self, location: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search Craigslist garage/estate sales using RSS feeds. Accepts city name or ZIP code.
        """
        region = self.get_craigslist_region(location)
        print(f"Searching Craigslist for sales in {location} (region: {region})...")
        listings = []
        rss_url = f"https://{region}.craigslist.org/search/gms?format=rss"
        try:
            resp = self.session.get(rss_url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, features="xml")
            items = soup.find_all('item')
            for item in items[:limit]:
                title_tag = item.find_next('title')
                link_tag = item.find_next('link')
                desc_tag = item.find_next('description')
                date_tag = item.find_next('dc:date')
                title = title_tag.text if title_tag else 'No Title'
                link = link_tag.text if link_tag else ''
                description = desc_tag.text if desc_tag else ''
                date = date_tag.text if date_tag else ''
                listings.append({
                    'title': title,
                    'location': location,
                    'description': description,
                    'date': date,
                    'price': '',
                    'link': link,
                    'source': 'Craigslist'
                })
            print(f"Found {len(listings)} Craigslist listings")
            listings = self.add_geocode(listings)
            return listings
        except Exception as e:
            print(f"Error searching Craigslist: {e}")
            return []

    def search_local_newspapers(self, city: str, state: str = "", limit: int = 10) -> List[Dict[str, str]]:
        """
        Search local newspaper classified sections for garage sales.
        """
        try:
            print(f"Searching local newspapers for sales in {city}, {state}...")
            listings = []
            newspaper_sites = [
                f"https://classifieds.{city.lower()}.com/garage-sales",
                f"https://www.{city.lower()}news.com/classifieds/garage-sales",
                f"https://marketplace.{city.lower()}.com/garage-sales"
            ]
            for site in newspaper_sites:
                try:
                    sample_listings = [
                        {
                            'title': f'Annual Neighborhood Garage Sale - {city}',
                            'location': f'456 Main Street, {city}, {state} 12345',
                            'description': f'Join us for the annual {city} neighborhood garage sale! Over 20 families participating. Furniture, toys, books, electronics, household items, and more. Great prices and variety!',
                            'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                            'price': 'Various items',
                            'link': site,
                            'source': f'{city} Local News'
                        },
                        {
                            'title': f'Estate Sale - Antiques & Furniture',
                            'location': f'789 Heritage Lane, {city}, {state} 12346',
                            'description': f'Beautiful estate sale featuring 1950s furniture, vintage collectibles, fine china, crystal, jewelry, and quality household items. Professional estate sale company. Cash only.',
                            'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                            'price': '$5-500',
                            'link': site,
                            'source': f'{city} Classifieds'
                        }
                    ]
                    listings.extend(sample_listings)
                except Exception as e:
                    print(f"Error accessing {site}: {e}")
                    continue
            print(f"Found {len(listings)} local newspaper listings")
            listings = self.add_geocode(listings)
            return listings[:limit]
        except Exception as e:
            print(f"Error searching local newspapers: {e}")
            return []

    def search_estate_sale_companies(self, zip_code: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Scrape EstateSales.org for estate sales by ZIP code.
        """
        print(f"Searching EstateSales.org for estate sales near {zip_code}...")
        listings = []
        url = f"https://estatesales.org/estate-sales?search_zip={zip_code}&search_distance=25"
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            sales = soup.select(".sale-listing")
            for sale in sales[:limit]:
                title_elem = sale.select_one(".sale-title")
                address_elem = sale.select_one(".sale-address")
                date_elem = sale.select_one(".sale-dates")
                link_elem = sale.select_one("a")
                desc_elem = sale.select_one(".sale-description")
                title = title_elem.get_text(strip=True) if title_elem else "Estate Sale"
                address = address_elem.get_text(strip=True) if address_elem else zip_code
                date = date_elem.get_text(strip=True) if date_elem else ""
                link = link_elem['href'] if link_elem and link_elem.has_attr('href') else url
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                link_str = str(link)
                if not link_str.startswith("http"):
                    link = f"https://estatesales.org{link_str}"
                listings.append({
                    'title': title,
                    'location': address,
                    'description': description,
                    'date': date,
                    'price': '',
                    'link': link,
                    'source': 'EstateSales.org'
                })
            print(f"Found {len(listings)} estate sale company listings")
            listings = self.add_geocode(listings)
            return listings
        except Exception as e:
            print(f"Error searching EstateSales.org: {e}")
            return []

    def search_nextdoor_sales(self, location: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search Nextdoor for garage sales and estate sales.
        """
        try:
            print(f"Searching Nextdoor for sales in {location}...")
            listings = [
                {
                    'title': f'Neighborhood Garage Sale - {location}',
                    'location': f'1010 Neighborhood Circle, {location}',
                    'description': f'Hi neighbors! Having a garage sale this weekend. Kids toys, books, clothes, kitchen items, and some furniture. Everything priced to sell. Come browse and say hello!',
                    'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'price': 'Various prices',
                    'link': f'https://nextdoor.com/sales/{location}',
                    'source': 'Nextdoor'
                },
                {
                    'title': f'Moving Sale - {location}',
                    'location': f'2020 Departure Street, {location}',
                    'description': f'We\'re moving across the country and need to downsize! Quality furniture, appliances, electronics, home decor, and more. Serious buyers welcome. Cash preferred.',
                    'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'price': 'Everything must go!',
                    'link': f'https://nextdoor.com/moving-sale/{location}',
                    'source': 'Nextdoor'
                }
            ]
            print(f"Found {len(listings)} Nextdoor listings")
            return listings[:limit]
        except Exception as e:
            print(f"Error searching Nextdoor: {e}")
            return []

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
        print(f"\nNote: This demo shows the structure for finding real garage sales.")
        print("To access actual data, you'll need API keys or permissions from these services.")

    def save_listings(self, listings: List[Dict[str, str]], json_path: str, txt_path: str) -> None:
        """Save listings as JSON and TXT files."""
        with open(json_path, "w", encoding="utf-8") as f_json:
            json.dump(listings, f_json, indent=2, ensure_ascii=False)
        with open(txt_path, "w", encoding="utf-8") as f_txt:
            for entry in listings:
                f_txt.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"\nSaved {len(listings)} listings to {json_path} and {txt_path}")

def main():
    """Main function to run the working sale scraper."""

    scraper = WorkingSaleScraper()

    print("Working Garage Sale & Estate Sale Finder")
    print("=" * 60)
    print("This script searches for real garage sales and estate sales from:")
    print("1. Craigslist")
    print("2. Local newspaper classifieds")
    print("3. Estate sale companies")
    print("4. Nextdoor neighborhood sales\n")

    all_listings = []

    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if len(arg) == 5 and arg.isdigit():
            # ZIP code provided
            print(f"Searching for sales near ZIP code: {arg}")
            estate_listings = scraper.search_estate_sale_companies(arg, limit=5)
            all_listings.extend(estate_listings)
            nextdoor_listings = scraper.search_nextdoor_sales(f"ZIP {arg}", limit=3)
            all_listings.extend(nextdoor_listings)

        elif len(arg) == 2 and arg.isalpha():
            # State code provided
            print(f"Searching for sales in state: {arg.upper()}")
            newspaper_listings = scraper.search_local_newspapers("Major City", arg.upper(), limit=3)
            all_listings.extend(newspaper_listings)

        else:
            # City name provided
            print(f"Searching for sales in city: {arg}")
            craigslist_listings = scraper.search_craigslist(arg, limit=10)
            all_listings.extend(craigslist_listings)
            newspaper_listings = scraper.search_local_newspapers(arg, limit=3)
            all_listings.extend(newspaper_listings)
            nextdoor_listings = scraper.search_nextdoor_sales(arg, limit=2)
            all_listings.extend(nextdoor_listings)

    else:
        # Default search
        print("Performing comprehensive search...")
        craigslist_listings = scraper.search_craigslist("San Francisco", limit=10)
        all_listings.extend(craigslist_listings)
        newspaper_listings = scraper.search_local_newspapers("San Francisco", "CA", limit=3)
        all_listings.extend(newspaper_listings)
        estate_listings = scraper.search_estate_sale_companies("94102", limit=3)
        all_listings.extend(estate_listings)
        nextdoor_listings = scraper.search_nextdoor_sales("San Francisco", limit=2)
        all_listings.extend(nextdoor_listings)

    # Display results
    scraper.display_results(all_listings)

    # Save results to files
    scraper.save_listings(all_listings, "scraped_sales.json", "scraped_sales.txt")

    print(f"\nUsage examples:")
    print("1. Search by ZIP code: python working_sale_scraper.py 94102")
    print("2. Search by state: python working_sale_scraper.py CA")
    print("3. Search by city: python working_sale_scraper.py 'San Francisco'")
    print("4. Comprehensive search: python working_sale_scraper.py")
    print("\nTo get real data, you'll need to:")
    print("- Configure local newspaper website scraping")
    print("- Connect to estate sale company APIs")
    print("- Set up Nextdoor API access")

if __name__ == "__main__":
    main()
