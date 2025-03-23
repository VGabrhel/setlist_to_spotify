"""
Spotify API integration module
"""

import os
import logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image
import io
import requests
import base64

def get_spotify_auth_manager(scope=None, cache_path=None):
    """
    Get a Spotify authentication manager with the specified scope.
    
    Args:
        scope (str, optional): The scope for Spotify authentication.
        cache_path (str, optional): Path to the cache file for storing tokens.
    
    Returns:
        spotipy.oauth2.SpotifyOAuth: The Spotify authentication manager.
    """
    # Use the deployed app URL as the redirect URI
    redirect_uri = "https://setlist-to-spotify.streamlit.app/"
    
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path=cache_path
    )

def get_spotify_client(auth_token):
    """Get an authenticated Spotify client"""
    return spotipy.Spotify(auth=auth_token)

def search_track_on_spotify(sp, song_name, artist_name=None):
    """Search for a track on Spotify with broader matching"""
    try:
        # First try exact match with artist
        if artist_name:
            query = f"track:\"{song_name}\" artist:\"{artist_name}\""
            result = sp.search(query, type="track", limit=1)
            if result["tracks"]["items"]:
                return result["tracks"]["items"][0]["uri"]
        
        # Then try just the song name with artist
        if artist_name:
            query = f"{song_name} {artist_name}"
            result = sp.search(query, type="track", limit=1)
            if result["tracks"]["items"]:
                return result["tracks"]["items"][0]["uri"]
        
        # Finally try just the song name
        query = song_name
        result = sp.search(query, type="track", limit=1)
        if result["tracks"]["items"]:
            return result["tracks"]["items"][0]["uri"]
        
    except Exception as e:
        logging.error(f"Error searching for track {song_name}: {str(e)}")
    return None

def get_spotify_artist_image(artist_name):
    """Get artist image from Spotify API"""
    try:
        auth_manager = get_spotify_auth_manager()
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Search for the artist
        results = sp.search(q=artist_name, type='artist', limit=1)
        
        if results['artists']['items']:
            artist = results['artists']['items'][0]
            if artist['images']:
                # Get the largest image
                return max(artist['images'], key=lambda x: x['width'])['url']
    except Exception as e:
        logging.error(f"Error fetching Spotify image: {str(e)}")
    return None

def upload_playlist_image(playlist_id, image_url, access_token):
    """Upload an image as playlist cover"""
    try:
        # Download the image
        response = requests.get(image_url)
        if response.status_code != 200:
            raise ValueError(f"Failed to download image: {response.status_code}")
        
        # Process image
        img = Image.open(io.BytesIO(response.content))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if larger than 256KB
        max_size = (800, 800)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
        img_byte_arr = img_byte_arr.getvalue()
        
        # Upload image
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'image/jpeg'
        }
        
        upload_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/images'
        response = requests.put(upload_url, headers=headers, data=img_byte_arr)
        
        if response.status_code != 202:
            raise ValueError(f"Failed to upload image: {response.status_code} - {response.text}")
        
        return True
        
    except Exception as e:
        logging.error(f"Error uploading playlist image: {str(e)}")
        return False 