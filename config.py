import os

ENVIRONMENT = "development"
FLASK_DEBUG = True
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"
SCOPE = "playlist-read-private playlist-modify-private playlist-modify-public"
