# Setlist to Spotify

Create Spotify playlists from your favorite band's latest tour setlist. This application fetches setlist data from Setlist.fm and creates a Spotify playlist with the songs.

## Features

- Search for artists and view their latest tour setlists
- Create Spotify playlists from setlists
- Automatic handling of cover songs
- Support for main sets and encores
- Playlist cover image from artist photos
- Session state preservation during authentication

## Prerequisites

- Python 3.8 or higher
- Spotify Developer Account
- Setlist.fm API Key

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/setlist-to-spotify.git
cd setlist-to-spotify
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API credentials:
```env
# Spotify API Credentials
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret

# Setlist.fm API Key
SETLISTFM_API_KEY=your_setlistfm_api_key

# Optional Debug Settings
LOG_LEVEL=INFO
```

5. Configure Spotify App:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Add `http://localhost:8501` to the Redirect URIs
   - Copy the Client ID and Client Secret to your `.env` file

6. Get Setlist.fm API Key:
   - Go to [Setlist.fm API](https://api.setlist.fm/docs/1.0/index.html)
   - Create an account and request an API key
   - Copy the API key to your `.env` file

## Running the Application

1. Ensure your virtual environment is activated
2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. Open your browser and navigate to `http://localhost:8501`

## Usage

1. Connect to Spotify using the button in the sidebar
2. Search for an artist
3. Review the setlist
4. Click "Create Playlist" to create a Spotify playlist with the songs

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Acknowledgments

- [Streamlit](https://streamlit.io/)
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Setlist.fm API](https://api.setlist.fm/)