import requests
import base64
import streamlit as st

def get_spotify_token():
    auth_str = f"{st.secrets['SPOTIFY_CLIENT_ID']}:{st.secrets['SPOTIFY_CLIENT_SECRET']}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {"Authorization": f"Basic {b64_auth_str}"}
    data = {"grant_type": "client_credentials"}

    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    return response.json()["access_token"]

def get_trending_tracks():
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://api.spotify.com/v1/browse/new-releases?country=US&limit=5", headers=headers)

    items = response.json()["albums"]["items"]
    return [f"{track['name']} by {track['artists'][0]['name']}" for track in items]
