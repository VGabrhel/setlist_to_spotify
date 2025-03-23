"""
Utility functions for the application
"""

def format_setlist_structure(setlist):
    """Format setlist into Main Set and Encores"""
    formatted_sets = []
    main_set = []
    encores = []
    
    if "sets" in setlist and "set" in setlist["sets"]:
        for set_data in setlist["sets"]["set"]:
            if "name" in set_data and "encore" in set_data["name"].lower():
                encores.append(set_data)
            else:
                main_set.append(set_data)
        
        # Add main set first
        if main_set:
            formatted_sets.append(("Main Set", main_set))
        
        # Add encores with proper numbering
        for i, encore in enumerate(encores, 1):
            name = f"Encore {i}" if len(encores) > 1 else "Encore"
            formatted_sets.append((name, [encore]))
    
    return formatted_sets

def extract_songs_from_setlist(setlist, artist_name):
    """Extract songs from a setlist with proper metadata"""
    songs = []
    if "sets" in setlist and "set" in setlist["sets"]:
        for set_data in setlist["sets"]["set"]:
            if "song" in set_data:
                for song in set_data["song"]:
                    song_info = {
                        "name": song["name"],
                        "original_artist": song.get("cover", {}).get("name", artist_name),
                        "info": song.get("info", ""),
                        "is_tape": song.get("tape", False),
                        "is_cover": "cover" in song
                    }
                    songs.append(song_info)
    return songs

def format_song_display(song_info, index):
    """Format song information for display"""
    extras = []
    if song_info["info"]:
        extras.append(f"*({song_info['info']})*")
    if song_info["is_tape"]:
        extras.append("🎵 (Playback)")
    if song_info["is_cover"]:
        extras.append(f"(Cover of {song_info['original_artist']})")
    
    display_text = f"{index}. {song_info['name']}"
    if extras:
        display_text += f" {' '.join(extras)}"
    
    return display_text 