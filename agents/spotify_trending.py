import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st

def get_trending_tracks(limit=5):
    client_id = st.secrets["SPOTIFY_CLIENT_ID"]
    client_secret = st.secrets["SPOTIFY_CLIENT_SECRET"]
    
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    playlist_id = "37i9dQZEVXbMDoHDwVN2tF"  # Spotify Top 50 Global
    results = sp.playlist_items(playlist_id, limit=limit)
    
    tracks = []
    for item in results["items"]:
        track = item["track"]
        tracks.append({
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "preview_url": track["preview_url"]  # can be None
        })
    return tracks
