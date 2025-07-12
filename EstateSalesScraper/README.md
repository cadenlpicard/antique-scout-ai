# EstateSales.net RSS Feed Scraper

A Python command-line script that scrapes and parses the EstateSales.net RSS feed to display estate sale listings.

## Features

- Fetches the latest estate sale listings from EstateSales.net RSS feed
- Extracts Title, City, and Date information from each listing
- Displays the first 10 entries in a clean, readable format
- Handles network errors and parsing issues gracefully
- Works in Replit and other Python environments

## Installation

### For Replit

1. Create a new Python Repl
2. Copy the `scraper.py` file to your Repl
3. Install the required dependency by running:
   ```bash
   pip install feedparser
   ```

### For Local Development

1. Ensure you have Python 3.6+ installed
2. Install the required dependency:
   ```bash
   pip install feedparser
   ```

## Usage

### Basic Usage

Run the script from the command line:

```bash
python scraper.py
```

### Using a Different RSS Feed

You can specify a custom RSS feed URL:

```bash
python scraper.py https://your-rss-feed.com/rss
```

### Examples

```bash
# NPR News
python scraper.py https://feeds.npr.org/1001/rss.xml

# CNN News
python scraper.py https://rss.cnn.com/rss/edition.rss

# BBC News
python scraper.py https://feeds.bbci.co.uk/news/rss.xml
```

## Output Format

The script displays entries in the format:
```
Title | City | Date
```

## Important Note

EstateSales.net doesn't currently have a public RSS feed. This script works with any RSS feed and can be adapted for estate sale websites that do provide RSS feeds.

## Customization

To use with a different RSS feed permanently:
1. Edit the `rss_url` variable in `scraper.py`
2. Replace it with your desired RSS feed URL
3. Run the script

## Quick Setup for Replit

1. The script is ready to run - no additional setup needed
2. Dependencies are automatically installed
3. Run with: `python scraper.py`
