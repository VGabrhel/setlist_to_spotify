"""
Setlist to Spotify - Main application
"""

import streamlit as st
import os
from dotenv import load_dotenv
import logging

from src.spotify import (
    get_spotify_auth_manager,
    get_spotify_client,
    search_track_on_spotify
)
from src.setlistfm import (
    search_artist,
    get_latest_setlist
)
from src.utils import (
    format_setlist_structure,
    extract_songs_from_setlist,
    format_song_display
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Page configuration
st.set_page_config(
    page_title="Setlist to Spotify",
    page_icon="🎵",
    layout="wide"
)

# Check for Spotify authentication callback
if "code" in st.query_params and not "spotify_token_info" in st.session_state:
    try:
        spotify_auth_manager = get_spotify_auth_manager(
            scope="playlist-modify-public playlist-modify-private user-read-private"
        )
        
        auth_code = st.query_params["code"]
        token_info = spotify_auth_manager.get_access_token(auth_code)
        st.session_state["spotify_token_info"] = token_info
        
        # Clear the URL parameters
        st.query_params.clear()
        st.success("Successfully connected to Spotify!")
        
        # Restore the previous state if it exists
        if "pre_auth_state" in st.session_state:
            for key, value in st.session_state["pre_auth_state"].items():
                if value is not None:
                    st.session_state[key] = value
            del st.session_state["pre_auth_state"]
        
        st.rerun()
    except Exception as e:
        st.error(f"""
            Failed to authenticate with Spotify. Please check:
            1. The authorization code is correct
            2. Your Spotify API credentials are correct
            3. The redirect URI (http://localhost:8501) is added to your Spotify app settings
            
            Error: {str(e)}
        """)

# App title and description
st.title("Setlist to Spotify")
st.markdown("Create Spotify playlists from your favorite band's latest tour setlist")

# Sidebar for configuration
with st.sidebar:
    st.header("About")
    st.info("This app creates Spotify playlists based on a band's latest tour setlist using data from Setlist.fm")
    
    st.header("Step 1: Connect to Spotify")
    spotify_connected = False
    
    if "spotify_token_info" in st.session_state:
        spotify_connected = True
        st.success("✓ Connected to Spotify")
        if st.button("Disconnect from Spotify", key="disconnect_button"):
            # Clear all Spotify-related session state
            keys_to_clear = ["spotify_token_info", "selected_artist", "selected_setlist"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            # Remove the cache file if it exists
            if os.path.exists(".spotify_caches"):
                os.remove(".spotify_caches")
            st.rerun()
    else:
        st.warning("⚠️ Not connected to Spotify")
        try:
            spotify_auth_manager = get_spotify_auth_manager(
                scope="playlist-modify-public playlist-modify-private user-read-private"
            )
            
            st.info("👉 Please connect to Spotify before searching for artists")
            if st.button("Connect to Spotify", key="connect_button"):
                # Store current state before authentication
                st.session_state["pre_auth_state"] = {
                    "search_query": st.session_state.get("last_search", ""),
                    "current_artist": st.session_state.get("current_artist", None),
                    "current_setlist": st.session_state.get("current_setlist", None),
                    "selected_artist": st.session_state.get("selected_artist", None),
                    "selected_setlist": st.session_state.get("selected_setlist", None)
                }
                
                # Get authorization URL and redirect
                auth_url = spotify_auth_manager.get_authorize_url()
                st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to initialize Spotify authentication: {str(e)}")

# Main area
st.header("Step 2: Search for an Artist")

if not spotify_connected:
    st.warning("Please connect to Spotify using the sidebar before searching for artists.")
    st.stop()

search_query = st.text_input("Enter artist name:", key="search_input", value=st.session_state.get("last_search", ""))

# Store the search query in session state
if search_query:
    st.session_state["last_search"] = search_query

if search_query:
    with st.spinner("Searching for artist..."):
        artist = search_artist(search_query)
        
        if artist:
            latest_setlist = get_latest_setlist(artist['mbid'])
            
            if latest_setlist:
                # Store the search results in session state
                st.session_state["current_artist"] = artist
                st.session_state["current_setlist"] = latest_setlist
                
                st.subheader(artist["name"])
                if "disambiguation" in artist:
                    st.caption(artist["disambiguation"])
                
                # Display the latest setlist info
                st.write(f"Latest tour: {latest_setlist['eventDate']} at {latest_setlist['venue']['name']}, {latest_setlist['venue']['city']['name']}")
                
                # Store the selected artist and setlist
                st.session_state["selected_artist"] = artist
                st.session_state["selected_setlist"] = latest_setlist
            else:
                st.warning(f"{artist['name']} has not been reported touring in the last 12 months.")
        else:
            st.warning(f"No exact matches found for '{search_query}'. Try searching for the exact artist name.")

# Display stored search results if they exist (after authentication)
elif "current_artist" in st.session_state and "current_setlist" in st.session_state:
    artist = st.session_state["current_artist"]
    latest_setlist = st.session_state["current_setlist"]
    
    st.subheader(artist["name"])
    if "disambiguation" in artist:
        st.caption(artist["disambiguation"])
    
    # Display the latest setlist info
    st.write(f"Latest tour: {latest_setlist['eventDate']} at {latest_setlist['venue']['name']}, {latest_setlist['venue']['city']['name']}")
    
    # Ensure the selected artist and setlist are stored
    st.session_state["selected_artist"] = artist
    st.session_state["selected_setlist"] = latest_setlist

# Create Playlist section (only shown if an artist is selected)
if "selected_setlist" in st.session_state:
    st.markdown("---")
    st.header("Step 3: Create Spotify Playlist")
    
    setlist = st.session_state["selected_setlist"]
    artist = st.session_state["selected_artist"]
    
    # Extract and display setlist
    songs = extract_songs_from_setlist(setlist, artist["name"])
    
    if songs:
        st.subheader("Setlist")
        formatted_sets = format_setlist_structure(setlist)
        song_index = 1
        
        for set_name, set_data_list in formatted_sets:
            st.write(f"**{set_name}:**")
            
            for set_data in set_data_list:
                if "song" in set_data:
                    for song in set_data["song"]:
                        display_text = format_song_display({
                            "name": song["name"],
                            "original_artist": song.get("cover", {}).get("name", artist["name"]),
                            "info": song.get("info", ""),
                            "is_tape": song.get("tape", False),
                            "is_cover": "cover" in song
                        }, song_index)
                        st.write(display_text)
                        song_index += 1
                else:
                    st.write("*No songs listed for this set*")
            
            if set_name != formatted_sets[-1][0]:  # Don't add space after last set
                st.write("")
        
        st.write(f"**Total tracks:** {len(songs)}")
        st.markdown("---")
        
        if "spotify_token_info" not in st.session_state:
            st.warning("Please connect to Spotify using the sidebar before creating a playlist.")
        else:
            playlist_name = st.text_input(
                "Playlist Name:", 
                value=f"{artist['name']} - {setlist['venue']['name']} ({setlist['eventDate']})"
            )
            
            playlist_description = st.text_area(
                "Playlist Description:", 
                value=f"Setlist from {artist['name']} at {setlist['venue']['name']}, {setlist['venue']['city']['name']} on {setlist['eventDate']}. Created with Setlist to Spotify app."
            )
            
            if st.button("Create Playlist"):
                with st.spinner("Creating playlist..."):
                    try:
                        # Initialize Spotify client
                        sp = get_spotify_client(st.session_state["spotify_token_info"]["access_token"])
                        
                        # Get current user info
                        user_info = sp.current_user()
                        user_id = user_info["id"]
                        
                        # Create a new playlist
                        playlist = sp.user_playlist_create(
                            user=user_id,
                            name=playlist_name,
                            public=True,
                            description=playlist_description
                        )
                        
                        # Search for songs and add them to the playlist
                        track_uris = []
                        not_found = []
                        
                        for song in songs:
                            track_uri = search_track_on_spotify(sp, song["name"], song["original_artist"])
                            if track_uri:
                                track_uris.append(track_uri)
                            else:
                                not_found.append(song["name"])
                        
                        if track_uris:
                            sp.playlist_add_items(playlist["id"], track_uris)
                        
                        # Display results
                        st.success(f"Successfully created playlist with {len(track_uris)} songs!")
                        st.write(f"[Open in Spotify](https://open.spotify.com/playlist/{playlist['id']})")
                        
                        if not_found:
                            st.warning(f"Could not find {len(not_found)} songs on Spotify:")
                            st.write(", ".join(not_found))
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("No songs found in this setlist.")

# Footer
st.markdown("---")
st.caption("Created with ❤️ using Streamlit, Setlist.fm API, and Spotify API")
