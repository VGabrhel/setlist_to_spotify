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
import streamlit as st

def get_spotify_auth_manager(scope=None, cache_path=None):
    """
    Get a Spotify authentication manager with the specified scope.
    
    Args:
        scope (str, optional): The scope for Spotify authentication.
        cache_path (str, optional): Path to the cache file for storing tokens.
    
    Returns:
        spotipy.oauth2.SpotifyOAuth: The Spotify authentication manager.
    """
    try:
        # Get credentials from Streamlit secrets
        if "spotify" not in st.secrets:
            raise ValueError("Spotify credentials not found in Streamlit secrets")
        
        client_id = st.secrets["spotify"]["client_id"]
        client_secret = st.secrets["spotify"]["client_secret"]
        
        if not client_id or not client_secret:
            raise ValueError("Spotify credentials are empty")
            
        logging.info("Successfully loaded Spotify credentials")
        
    except Exception as e:
        error_msg = f"""
            Failed to load Spotify credentials: {str(e)}
            
            To set up your credentials:
            1. Go to your Streamlit Cloud dashboard
            2. Select your app
            3. Click on "Settings" → "Secrets"
            4. Add your Spotify credentials in this format:
            
            [spotify]
            client_id = "your_client_id"
            client_secret = "your_client_secret"
            
            Make sure to:
            1. Copy the exact credentials from your Spotify Developer Dashboard
            2. Include the quotes around the values
            3. Don't add any extra spaces or newlines
        """
        st.error(error_msg)
        logging.error(f"Spotify credentials error: {str(e)}")
        raise
    
    # Define scopes if not provided
    if scope is None:
        scope = " ".join([
            "playlist-modify-public",
            "playlist-modify-private",
            "user-read-private",
            "user-read-email"
        ])
    
    # Get the current URL for the redirect URI
    if "code" in st.query_params:
        # If we're handling the callback, use the current URL
        redirect_uri = st.query_params.get("redirect_uri", "http://localhost:8501")
    else:
        # Otherwise, use the app's URL
        redirect_uri = "http://localhost:8501"
    
    logging.info(f"Using redirect URI: {redirect_uri}")
    
    # Create the auth manager with all necessary parameters
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path=cache_path,
        show_dialog=True  # Force the consent screen to show
    )
    
    return auth_manager

def get_spotify_client(auth_token):
    """Get an authenticated Spotify client"""
    if isinstance(auth_token, dict):
        auth_token = auth_token.get('access_token')
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