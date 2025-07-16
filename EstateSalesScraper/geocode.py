"""
geocode.py – Wrapper around OpenStreetMap Nominatim with disk caching

Milestone #1 for the *antique‑scout‑ai* prototype.

Requirements:
    pip install requests
"""

import os
import json
import time
import requests
from urllib.parse import urlencode

CACHE_FILE = "data/geocode_cache.json"
USER_AGENT = "AntiqueScoutBot/1.0 (contact: your_email@example.com)"
WAIT_BETWEEN_CALLS = 1.1  # seconds

if not os.path.exists("data"):
    os.makedirs("data")

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE) as f:
        cache = json.load(f)
else:
    cache = {}

def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def geocode(address: str):
    if not address:
        return None, None

    if address in cache:
        return cache[address]

    print(f"Geocoding: {address}")
    time.sleep(WAIT_BETWEEN_CALLS)

    query = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    url = f"https://nominatim.openstreetmap.org/search?{urlencode(query)}"
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
        else:
            lat, lon = None, None
    except Exception as e:
        print(f"Geocoding failed: {e}")
        lat, lon = None, None

    cache[address] = (lat, lon)
    save_cache()
    return lat, lon
