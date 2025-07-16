# Antique Scout AI: Estate Sale Scraper

This repository provides a robust, real-world estate sale and garage sale scraper focused exclusively on EstateSales.net. It is designed for reliability, simplicity, and real address discovery.

## Features
- **EstateSales.net Scraper:** Finds real estate sales and garage sales using dynamic location-based search.
- **Flexible Location Input:** Supports city/state/ZIP combinations, multi-word cities, and ZIP-only searches.
- **Robust HTML Parsing:** Targets Angular components for accurate listing extraction.
- **Integrated Geocoding:** Adds latitude/longitude to each listing using OpenStreetMap.
- **Randomized User Agents & Delays:** Helps avoid rate-limiting and blocking.
- **Debugging Support:** Saves HTML for inspection and troubleshooting.
- **Clean Output:** Results saved as both JSON and TXT files for easy use.

## Usage
Run the scraper from the command line:

```bash
python sale_scraper.py "Grand Blanc, MI 48439"
python sale_scraper.py "New York NY"
python sale_scraper.py "90210"
```

- Results are displayed in the terminal and saved to `scraped_sales.json` and `scraped_sales.txt`.
- The script focuses solely on EstateSales.net for maximum reliability.

## Project Structure
```
EstateSalesScraper/
├── sale_scraper.py         # Main scraper script
├── geocode.py              # Geocoding utility
├── data/
│   └── geocode_cache.json  # Geocoding cache
├── pyproject.toml          # Project configuration
├── uv.lock                 # Dependency lock file
└── README.md               # (This file)
```

## How It Works
- **Location Parsing:** Accepts flexible location formats and constructs the correct EstateSales.net URL.
- **Listing Extraction:** Uses BeautifulSoup to find `app-sale-row` elements and extract sale details.
- **Geocoding:** Each address is geocoded for mapping and analysis.
- **Output:** Listings are saved in both human-readable and machine-readable formats.

## Requirements
- Python 3.12+
- `requests`, `beautifulsoup4`

Install dependencies:
```bash
pip install -r requirements.txt
```

## Customization
- You can adjust the search location, result limit, or output format by editing `sale_scraper.py`.

## License
MIT License

---

**Antique Scout AI** is focused on real, actionable estate sale data. All legacy code and unused features have been removed for clarity and maintainability.
