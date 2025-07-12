#!/usr/bin/env python3
"""
Garage Sale & Estate Sale Scraper

This script scrapes garage sale and estate sale listings from multiple sources:
1. Craigslist RSS feeds (official method)
2. Direct web scraping for sites without RSS feeds
3. Generic RSS feed support

Supports Title, Location, Date, and Price extraction.
"""

import requests
import feedparser
import sys
import re
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time
import urllib.parse


class GarageSaleScraper:
    """Main scraper class for garage sales and estate sales."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_craigslist_rss_url(self, city: str, search_term: str = "") -> str:
        """
        Generate Craigslist RSS URL for garage sales.
        
        Args:
            city: City code (e.g., 'sfbay', 'losangeles', 'boston')
            search_term: Optional search term to filter results
            
        Returns:
            RSS URL for Craigslist garage sales
        """
        base_url = f"https://{city}.craigslist.org/search/gms"
        params = {"format": "rss"}
        
        if search_term:
            params["query"] = search_term
        
        url = f"{base_url}?" + urllib.parse.urlencode(params)
        return url
    
    def scrape_craigslist_rss(self, city: str, search_term: str = "", limit: int = 10) -> List[Dict[str, str]]:
        """
        Scrape Craigslist garage sales using RSS feeds.
        
        Args:
            city: City code for Craigslist
            search_term: Optional search filter
            limit: Maximum number of results
            
        Returns:
            List of garage sale listings
        """
        rss_url = self.get_craigslist_rss_url(city, search_term)
        
        try:
            print(f"Fetching Craigslist RSS feed for {city}...")
            # Add headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/rss+xml, application/xml, text/xml',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(rss_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"HTTP {response.status_code} for {city}. Craigslist may be blocking requests.")
                return []
            
            # Check if blocked
            if 'blocked' in response.text.lower() or 'your request has been blocked' in response.text.lower():
                print(f"Craigslist is blocking requests for {city}")
                return []
            
            feed = feedparser.parse(response.text)
            
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                print(f"No entries found for {city}")
                return []
            
            listings = []
            
            for i, entry in enumerate(feed.entries[:limit]):
                try:
                    # Extract basic info
                    title = entry.get('title', 'No title').strip()
                    link = entry.get('link', '')
                    date_str = self.format_date(entry.get('published', ''))
                    
                    # Extract location from title (Craigslist format: "Title (Location)")
                    location = self.extract_location_from_title(title)
                    
                    # Extract price from title
                    price = self.extract_price_from_title(title)
                    
                    # Clean up title (remove price and location)
                    clean_title = self.clean_title(title)
                    
                    listings.append({
                        'title': clean_title,
                        'location': location,
                        'date': date_str,
                        'price': price,
                        'link': link,
                        'source': f'Craigslist-{city}'
                    })
                    
                except Exception as e:
                    print(f"Error parsing entry {i+1}: {e}")
                    continue
            
            return listings
            
        except Exception as e:
            print(f"Error fetching Craigslist RSS for {city}: {e}")
            return []
    
    def scrape_garagesalesfinder(self, zip_code: str = "", limit: int = 10) -> List[Dict[str, str]]:
        """
        Scrape GarageSalesFinder.com using web scraping.
        
        Args:
            zip_code: ZIP code for location-based search
            limit: Maximum number of results
            
        Returns:
            List of garage sale listings
        """
        try:
            if zip_code:
                url = f"https://www.garagesalesfinder.com/search.php?zip={zip_code}"
                print(f"Scraping GarageSalesFinder.com for ZIP {zip_code}...")
            else:
                url = "https://www.garagesalesfinder.com"
                print("Scraping GarageSalesFinder.com...")
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"HTTP {response.status_code} for GarageSalesFinder.com")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = []
            
            # Look for sale listings - adjust selectors based on actual site structure
            sale_items = soup.find_all(['div', 'article', 'li'], class_=re.compile(r'sale|listing|event', re.I))
            
            if not sale_items:
                # Try broader search
                sale_items = soup.find_all('div', string=re.compile(r'sale|garage|estate', re.I))
            
            for i, item in enumerate(sale_items[:limit]):
                try:
                    # Extract text content
                    text = item.get_text(strip=True)
                    
                    if len(text) < 10:  # Skip very short items
                        continue
                    
                    # Extract title (first line or main text)
                    title = text.split('\n')[0] if '\n' in text else text[:100]
                    
                    # Extract location
                    location = self.extract_location_from_text(text)
                    
                    # Extract price
                    price = self.extract_price_from_text(text)
                    
                    # Extract date
                    date_str = self.extract_date_from_text(text)
                    
                    # Find link
                    link_elem = item.find('a', href=True)
                    link = link_elem['href'] if link_elem else ''
                    if link and not link.startswith('http'):
                        link = f"https://www.garagesalesfinder.com{link}"
                    
                    if title and len(title) > 5:  # Only add if we have meaningful content
                        listings.append({
                            'title': title[:100],
                            'location': location,
                            'date': date_str,
                            'price': price,
                            'link': link,
                            'source': 'GarageSalesFinder'
                        })
                
                except Exception as e:
                    print(f"Error parsing item {i+1}: {e}")
                    continue
            
            return listings
            
        except Exception as e:
            print(f"Error scraping GarageSalesFinder.com: {e}")
            return []
    
    def scrape_generic_rss(self, rss_url: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Scrape any RSS feed for sale listings.
        
        Args:
            rss_url: RSS feed URL
            limit: Maximum number of results
            
        Returns:
            List of listings
        """
        try:
            print(f"Fetching RSS feed: {rss_url}")
            feed = feedparser.parse(rss_url)
            
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                print("No entries found in RSS feed")
                return []
            
            listings = []
            
            for i, entry in enumerate(feed.entries[:limit]):
                try:
                    title = entry.get('title', 'No title').strip()
                    link = entry.get('link', '')
                    date_str = self.format_date(entry.get('published', ''))
                    
                    # Try to extract location and price
                    location = self.extract_location_from_title(title)
                    price = self.extract_price_from_title(title)
                    clean_title = self.clean_title(title)
                    
                    listings.append({
                        'title': clean_title,
                        'location': location,
                        'date': date_str,
                        'price': price,
                        'link': link,
                        'source': 'RSS Feed'
                    })
                    
                except Exception as e:
                    print(f"Error parsing entry {i+1}: {e}")
                    continue
            
            return listings
            
        except Exception as e:
            print(f"Error fetching RSS feed: {e}")
            return []
    
    def extract_location_from_title(self, title: str) -> str:
        """Extract location from title using various patterns."""
        try:
            # Craigslist pattern: "Title (Location)"
            location_match = re.search(r'\(([^)]+)\)\s*$', title)
            if location_match:
                return location_match.group(1).strip()
            
            # Other patterns
            patterns = [
                r'in\s+([A-Za-z\s]+),\s*[A-Z]{2}',  # "in City, ST"
                r'([A-Za-z\s]+),\s*[A-Z]{2}',  # "City, ST"
                r'-\s*([A-Za-z\s]+)$',  # "Title - City"
                r'@\s*([A-Za-z\s]+)',  # "Event @ Location"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, title, re.IGNORECASE)
                if match:
                    location = match.group(1).strip()
                    if len(location) > 2:
                        return location
            
            return "Not specified"
            
        except Exception:
            return "Unknown"
    
    def extract_location_from_text(self, text: str) -> str:
        """Extract location from general text content."""
        try:
            # Look for common location patterns
            patterns = [
                r'(?:address|location|where)[:\s]+([A-Za-z\s,]+(?:\d{5})?)',
                r'(\d+\s+[A-Za-z\s]+(?:st|street|ave|avenue|rd|road|blvd|boulevard|dr|drive|ln|lane|way|ct|court))',
                r'([A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5})',
                r'([A-Za-z\s]+,\s*[A-Z]{2})',
                r'(\d{5})',  # ZIP code
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    location = match.group(1).strip()
                    if len(location) > 2:
                        return location
            
            return "Not specified"
            
        except Exception:
            return "Unknown"
    
    def extract_price_from_title(self, title: str) -> str:
        """Extract price from title."""
        try:
            # Look for price patterns
            price_patterns = [
                r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $123.45 or $1,234
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*dollars?',  # 123 dollars
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*\$',  # 123$
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, title, re.IGNORECASE)
                if match:
                    return f"${match.group(1)}"
            
            return "Not listed"
            
        except Exception:
            return "Unknown"
    
    def extract_price_from_text(self, text: str) -> str:
        """Extract price from general text content."""
        try:
            # Look for price patterns in text
            price_patterns = [
                r'price[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*dollars?',
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return f"${match.group(1)}"
            
            return "Not listed"
            
        except Exception:
            return "Unknown"
    
    def extract_date_from_text(self, text: str) -> str:
        """Extract date from general text content."""
        try:
            # Look for date patterns
            date_patterns = [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # MM/DD/YYYY or MM-DD-YYYY
                r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
                r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}(?:,\s*\d{4})?)',  # Jan 15, 2025
                r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*(?:,?\s*\d{4})?)',  # 15 Jan 2025
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return "Not specified"
            
        except Exception:
            return "Unknown"
    
    def clean_title(self, title: str) -> str:
        """Clean title by removing price and location info."""
        try:
            # Remove price
            title = re.sub(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', '', title)
            title = re.sub(r'\d+(?:,\d{3})*(?:\.\d{2})?\s*dollars?', '', title, flags=re.IGNORECASE)
            
            # Remove location in parentheses
            title = re.sub(r'\s*\([^)]+\)\s*$', '', title)
            
            # Remove extra whitespace
            title = re.sub(r'\s+', ' ', title).strip()
            
            return title
            
        except Exception:
            return title
    
    def format_date(self, date_string: str) -> str:
        """Format date string for display."""
        try:
            if not date_string:
                return "No date"
            
            # Try parsing different date formats
            for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z", 
                       "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                try:
                    dt = datetime.strptime(date_string, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            
            # If all parsing fails, return first 10 chars
            return date_string[:10] if len(date_string) >= 10 else date_string
            
        except Exception:
            return "Date unknown"
    
    def display_results(self, all_listings: List[Dict[str, str]]) -> None:
        """Display all listings in formatted output."""
        if not all_listings:
            print("No listings found.")
            return
        
        print(f"\nFound {len(all_listings)} garage sale listings:\n")
        print("=" * 100)
        
        for i, listing in enumerate(all_listings, 1):
            title = listing['title']
            location = listing['location']
            date = listing['date']
            price = listing['price']
            source = listing['source']
            
            # Truncate title if too long
            if len(title) > 40:
                title = title[:37] + "..."
            
            print(f"{i:2d}. {title:<40} | {location:<20} | {date:<12} | {price:<12} | {source}")
        
        print("=" * 100)


def main():
    """Main function to run the garage sale scraper."""
    
    scraper = GarageSaleScraper()
    
    print("Garage Sale & Estate Sale Scraper")
    print("=" * 50)
    print("This script scrapes garage sales from multiple sources:")
    print("1. GarageSalesFinder.com (web scraping)")
    print("2. Craigslist RSS feeds (may be blocked)")
    print("3. Any RSS feed")
    print("4. Custom web scraping\n")
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.startswith('http'):
            # RSS feed URL provided
            print(f"Using custom RSS feed: {arg}")
            listings = scraper.scrape_generic_rss(arg, limit=10)
            scraper.display_results(listings)
        elif arg.isdigit() and len(arg) == 5:
            # ZIP code provided for GarageSalesFinder
            print(f"Searching GarageSalesFinder.com for ZIP code: {arg}")
            listings = scraper.scrape_garagesalesfinder(zip_code=arg, limit=10)
            scraper.display_results(listings)
        else:
            # City code provided for Craigslist
            print(f"Searching Craigslist for city: {arg}")
            listings = scraper.scrape_craigslist_rss(arg, search_term="", limit=10)
            scraper.display_results(listings)
    else:
        # Default: Try GarageSalesFinder first, then working RSS feed
        print("Searching GarageSalesFinder.com...")
        all_listings = []
        
        # Try GarageSalesFinder.com
        gsf_listings = scraper.scrape_garagesalesfinder(limit=10)
        all_listings.extend(gsf_listings)
        
        # If no results, try a working RSS feed as demo
        if not all_listings:
            print("No listings found. Trying demo RSS feed...")
            demo_listings = scraper.scrape_generic_rss("https://feeds.feedburner.com/oreilly/radar/atom", limit=5)
            all_listings.extend(demo_listings)
        
        scraper.display_results(all_listings)
    
    print(f"\nUsage examples:")
    print("1. Search by ZIP code: python garage_sale_scraper.py 90210")
    print("2. Search Craigslist city: python garage_sale_scraper.py sfbay")
    print("3. Use custom RSS feed: python garage_sale_scraper.py https://example.com/rss")
    print("4. Default search: python garage_sale_scraper.py")
    print("\nPopular Craigslist city codes: sfbay, losangeles, boston, seattle, phoenix, chicago, newyork")


if __name__ == "__main__":
    main()