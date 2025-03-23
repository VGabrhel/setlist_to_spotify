"""
Setlist.fm API integration module
"""

import os
import logging
import requests
from datetime import datetime, timedelta
import time

def handle_rate_limit(response):
    """Handle rate limiting by waiting and retrying"""
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        logging.warning(f"Rate limit reached. Waiting {retry_after} seconds...")
        time.sleep(retry_after)
        return True
    return False

def get_setlistfm_headers():
    """Get headers for Setlist.fm API requests"""
    api_key = os.getenv("SETLISTFM_API_KEY")
    if not api_key:
        raise ValueError(
            "Setlist.fm API key not found. Please make sure SETLISTFM_API_KEY "
            "environment variable is set."
        )
    
    return {
        "x-api-key": api_key,
        "Accept": "application/json"
    }

def is_recent_tour(setlist):
    """Check if the setlist is from the last 12 months"""
    try:
        event_date = datetime.strptime(setlist['eventDate'], '%d-%m-%Y')
        twelve_months_ago = datetime.now() - timedelta(days=365)
        return event_date >= twelve_months_ago
    except ValueError:
        return False

def search_artist(artist_name):
    """Search for an artist on Setlist.fm"""
    url = "https://api.setlist.fm/rest/1.0/search/artists"
    headers = get_setlistfm_headers()
    params = {
        "artistName": artist_name,
        "p": 1,
        "sort": "relevance"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        while handle_rate_limit(response):
            response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if "artist" in data:
                # Filter for exact matches
                exact_matches = [
                    artist for artist in data["artist"]
                    if artist["name"].lower() == artist_name.lower()
                ]
                return exact_matches[0] if exact_matches else None
        else:
            logging.error(f"Error searching for artist: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Error searching for artist: {str(e)}")
    return None

def get_latest_setlist(artist_mbid):
    """Get the most recent setlist for an artist that contains songs"""
    url = f"https://api.setlist.fm/rest/1.0/artist/{artist_mbid}/setlists"
    headers = get_setlistfm_headers()
    page = 1
    max_pages = 5  # Limit how many pages we'll check
    
    while page <= max_pages:
        params = {
            "p": page,
            "sort": "eventDate",
            "order": "desc"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            while handle_rate_limit(response):
                response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if "setlist" in data and data["setlist"]:
                    # Check each setlist for songs
                    for setlist in data["setlist"]:
                        if is_recent_tour(setlist):
                            if "sets" in setlist and "set" in setlist["sets"]:
                                for set_data in setlist["sets"]["set"]:
                                    if "song" in set_data and set_data["song"]:
                                        return setlist  # Found a setlist with songs
                    page += 1
                else:
                    break
            else:
                logging.error(f"Error fetching setlists: {response.status_code} - {response.text}")
                break
        except Exception as e:
            logging.error(f"Error fetching latest setlist: {str(e)}")
            break
    
    return None

def get_artist_image(artist):
    """Get the best quality image for an artist from setlist.fm"""
    if "image" in artist and artist["image"]:
        # Sort images by size (width) and get the largest one
        sorted_images = sorted(artist["image"], key=lambda x: x.get("width", 0), reverse=True)
        return sorted_images[0]["url"]
    return None 