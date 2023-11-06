import http
from spotify_connector import *
import os
import requests
import json
import pandas as pd
from scrapper import get_album_info

PLAYLIST_ID = os.getenv("SPOTIFORK_PLAYLIST_ID")

connector = SpotifyConnector()
SEARCH_URL = "https://api.spotify.com/v1/search"

album_search_ids = []
track_ids = []
current_playlist_ids = []
track_info = []

# Scrape the Pitchfork review pages
album_data_frame = pd.DataFrame(get_album_info())

for artist, album in album_data_frame.values:
    print(f"Searching for......{artist} - {album}")
    header = {"Authorization": "Bearer" + " " + connector.get_refresh_token()}
    payload = {"q": album, "type": "album"}
    r = requests.get(SEARCH_URL, params=payload, headers=header).json()
    results = r["albums"]["items"]
    for i in results:
        album_id = i["id"]
        artists_dict = i["artists"]
        if i["album_type"] == "album" and i["name"].lower() == album:
            # print(album)
            for info in artists_dict:
                artists = info["name"].lower()
                if artists in album_data_frame.values:
                    uri = album_id
                    album_search_ids.append(uri)

# Offset is used for Spotify's 100 song request limit
for i in range(0, 400, 100):
    playlist_tracks_request = requests.get(
        "https://api.spotify.com/v1/playlists/"
        + PLAYLIST_ID
        + "/tracks?offset="
        + str(i),
        headers=header,
    ).json()
    playlist_tracks_request = playlist_tracks_request["items"]
    for i in playlist_tracks_request:
        current_playlist_ids.append(i["track"]["uri"])

for ids in album_search_ids:
    tracks_request = requests.get(
        "https://api.spotify.com/v1/albums/" + ids + "/tracks", headers=header
    ).json()
    for i in tracks_request["items"]:
        track_uri = i["uri"]
        track_name = i["name"]
        explicit = i["explicit"]
        track_info.append(
            {"uri": track_uri, "track_name": track_name, "explicit": explicit}
        )

"""When searching for an album, Spotify returns both explicit and clean versions. I don't want both versions in my
final playlist. To remedy this, I placed my results into a pandas dataframe to drop any duplicates.
"""
track_df = (
    pd.DataFrame(track_info)
    .sort_values(by="explicit")
    .drop_duplicates(subset="track_name", keep="last")
)

# Get Songs from albums, by ID, and add them to my playlist(PLAYLIST_ID).
for track_uri in track_df["uri"]:
    if track_uri not in current_playlist_ids:
        add_request = requests.post(
            "https://api.spotify.com/v1/playlists/" + PLAYLIST_ID + "/tracks",
            params="uris=" + track_uri,
            headers=header,
        )
        print(f"Adding {track_uri}")
    else:
        print("Skipping")
