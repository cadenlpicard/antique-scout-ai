#!/usr/bin/env python3
"""
EstateSales.net RSS Feed Scraper

This script fetches and parses the EstateSales.net RSS feed to display
estate sale listings with Title, City, and Date information.
"""

import feedparser
import sys
import re
from datetime import datetime
from typing import List, Dict, Optional


def fetch_rss_feed(url: str) -> Optional[feedparser.FeedParserDict]:
    """
    Fetch and parse RSS feed from the given URL.
    
    Args:
        url: The RSS feed URL
        
    Returns:
        Parsed feed data or None if error occurred
    """
    try:
        print("Fetching RSS feed...")
        feed = feedparser.parse(url)
        
        # Check if feed was successfully parsed
        if feed.bozo:
            print(f"Warning: Feed parsing issues detected: {feed.bozo_exception}")
        
        if not hasattr(feed, 'entries') or len(feed.entries) == 0:
            print("Error: No entries found in RSS feed")
            return None
            
        return feed
        
    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
        return None


def extract_city_from_title(title: str) -> str:
    """
    Extract city information from the title string.
    For general RSS feeds, we'll try to extract location information.
    
    Args:
        title: The title string from RSS entry
        
    Returns:
        Extracted city or "Not specified" if not found
    """
    try:
        # Common patterns for city extraction from various titles
        # Look for patterns like "City, State" or "City Name"
        city_patterns = [
            r'in\s+([A-Za-z\s]+),\s*[A-Z]{2}',  # "in City, ST"
            r'([A-Za-z\s]+),\s*[A-Z]{2}\s*\d{5}',  # "City, ST 12345"
            r'([A-Za-z\s]+),\s*[A-Z]{2}',  # "City, ST"
            r'-\s*([A-Za-z\s]+)$',  # "Title - City"
            r'@\s*([A-Za-z\s]+)',  # "Event @ Location"
        ]
        
        for pattern in city_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                # Clean up common words that might be captured
                city = re.sub(r'\b(estate|sale|sales|news|report)\b', '', city, flags=re.IGNORECASE).strip()
                if city and len(city) > 2:
                    return city
        
        # For general RSS feeds, return a generic location field
        return "Not specified"
        
    except Exception:
        return "Unknown"


def format_date(date_string: str) -> str:
    """
    Format date string for display.
    
    Args:
        date_string: Raw date string from RSS entry
        
    Returns:
        Formatted date string
    """
    try:
        # Try to parse various date formats
        if hasattr(date_string, 'tm_year'):
            # If it's already a time struct
            return datetime.fromtimestamp(date_string).strftime("%Y-%m-%d")
        
        # Try parsing string dates
        for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z", 
                   "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try:
                dt = datetime.strptime(date_string, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # If all parsing fails, return the original string
        return date_string[:10] if len(date_string) >= 10 else date_string
        
    except Exception:
        return "Date unknown"


def parse_entries(feed: feedparser.FeedParserDict, limit: int = 10) -> List[Dict[str, str]]:
    """
    Parse RSS entries and extract relevant information.
    
    Args:
        feed: Parsed RSS feed data
        limit: Maximum number of entries to process
        
    Returns:
        List of dictionaries containing parsed entry data
    """
    entries = []
    
    for i, entry in enumerate(feed.entries[:limit]):
        try:
            # Extract title
            title = entry.get('title', 'No title').strip()
            
            # Extract city from title or summary
            city = extract_city_from_title(title)
            
            # Extract date
            date_str = "No date"
            if hasattr(entry, 'published'):
                date_str = format_date(entry.published)
            elif hasattr(entry, 'updated'):
                date_str = format_date(entry.updated)
            
            # Clean up title (remove excessive whitespace and HTML entities)
            title = re.sub(r'\s+', ' ', title)
            title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            
            entries.append({
                'title': title,
                'city': city,
                'date': date_str
            })
            
        except Exception as e:
            print(f"Error parsing entry {i+1}: {e}")
            continue
    
    return entries


def display_entries(entries: List[Dict[str, str]]) -> None:
    """
    Display entries in the specified format.
    
    Args:
        entries: List of parsed entries
    """
    if not entries:
        print("No entries to display.")
        return
    
    print(f"\nFound {len(entries)} estate sale listings:\n")
    print("=" * 80)
    
    for i, entry in enumerate(entries, 1):
        title = entry['title']
        city = entry['city']
        date = entry['date']
        
        # Truncate title if too long for better formatting
        if len(title) > 50:
            title = title[:47] + "..."
        
        print(f"{i:2d}. {title} | {city} | {date}")
    
    print("=" * 80)


def main():
    """
    Main function to run the RSS scraper.
    """
    # Since EstateSales.net doesn't have a public RSS feed, we'll use a working example
    # Users can replace this with any RSS feed URL they want to scrape
    
    # Default RSS feed URL - modify this line to use your desired RSS feed
    rss_url = "https://feeds.feedburner.com/oreilly/radar/atom"
    
    # Alternative RSS feeds you can try:
    # rss_url = "https://rss.cnn.com/rss/edition.rss"  # CNN News
    # rss_url = "https://feeds.npr.org/1001/rss.xml"   # NPR News
    # rss_url = "https://feeds.bbci.co.uk/news/rss.xml"  # BBC News
    # rss_url = "YOUR_RSS_FEED_URL_HERE"  # Replace with your RSS feed
    
    print("RSS Feed Scraper")
    print("-" * 40)
    print("Note: EstateSales.net doesn't have a public RSS feed.")
    print("This demo uses a working RSS feed to show functionality.")
    print(f"Current RSS feed: {rss_url}")
    print("You can modify the rss_url variable to use any RSS feed.\n")
    
    # Accept command line argument for RSS URL
    if len(sys.argv) > 1:
        rss_url = sys.argv[1]
        print(f"Using RSS feed from command line: {rss_url}\n")
    
    # Fetch RSS feed
    feed = fetch_rss_feed(rss_url)
    if not feed:
        print("Failed to fetch RSS feed. Please check your internet connection.")
        sys.exit(1)
    
    # Parse entries
    entries = parse_entries(feed, limit=10)
    
    if not entries:
        print("No entries could be parsed from the RSS feed.")
        sys.exit(1)
    
    # Display results
    display_entries(entries)
    
    print(f"\nTotal entries processed: {len(entries)}")
    print("\nHow to use with different RSS feeds:")
    print("1. Command line: python scraper.py https://your-rss-feed.com/rss")
    print("2. Or edit the rss_url variable in the script")
    print("3. For estate sales, try searching for local estate sale company RSS feeds")


if __name__ == "__main__":
    main()
