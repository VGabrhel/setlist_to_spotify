# Setlist to Spotify

Create Spotify playlists from your favorite band's latest tour setlist using data from Setlist.fm.

## Setup

1. Clone this repository
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Setting up Streamlit Secrets

1. Create a `.streamlit` directory in your project root:
   ```bash
   mkdir .streamlit
   ```

2. Create a `secrets.toml` file in the `.streamlit` directory with your API credentials:
   ```toml
   # Spotify API Credentials
   [spotify]
   client_id = "your_client_id_here"
   client_secret = "your_client_secret_here"

   # Setlist.fm API Key
   [setlistfm]
   api_key = "your_setlistfm_api_key_here"

   # Optional Logging Settings
   [logging]
   level = "INFO"
   ```

3. Replace the placeholder values with your actual API credentials:
   - Get Spotify API credentials from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Get Setlist.fm API key from [Setlist.fm API](https://api.setlist.fm/docs/1.0/index.html)

### Configuring Spotify App

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app or select your existing app
3. Click "Edit Settings"
4. Add the following Redirect URIs:
   - `http://localhost:8501` (for local development)
   - Your deployed app URL (e.g., `https://your-app-name.streamlit.app/`)
5. Click "Save"

## Running the App

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```
2. Open your browser and navigate to `http://localhost:8501`
3. Connect your Spotify account
4. Search for an artist
5. Create a playlist from their latest setlist

## Features

- Search for artists using Setlist.fm data
- View latest tour setlists
- Create Spotify playlists automatically
- Support for covers and special song notes
- Beautiful and intuitive interface

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io/)
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Setlist.fm API](https://api.setlist.fm/)