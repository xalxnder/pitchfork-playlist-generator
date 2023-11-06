from flask import Flask, render_template, flash, session, redirect, request, Response, session, make_response, jsonify, \
    abort
import config
from scrapper import get_album_info, get_urls
import urllib.parse as urlparse
from spotify_connector import SpotifyConnector
import base64
import pandas as pd
import requests
import os

SEARCH_URL = "https://api.spotify.com/v1/search"
app = Flask(__name__)
connector = SpotifyConnector()
PLAYLIST_ID = os.getenv("SPOTIFORK_PLAYLIST_ID")

app.secret_key = '123'
app.config.from_pyfile("config.py")
album_search_ids = []
track_ids = []
current_playlist_ids = []
track_info = []


@app.route('/')
def index():
    session.clear()

    print('INDEX')
    print(session)
    return render_template('index.html')


@app.route('/login')
def login():
    client_id = app.config['CLIENT_ID']
    print(client_id)
    print(f"clinet ID is {client_id}")
    redirect_uri = app.config['REDIRECT_URI']
    scope = app.config['SCOPE']
    authorize_url = 'https://accounts.spotify.com/en/authorize?'
    state_key = connector.create_state_key(15)
    session['state_key'] = state_key
    parameters = 'response_type=code&client_id=' + client_id + '&redirect_uri=' + redirect_uri + '&scope=' + scope + '&state=' + state_key
    response = make_response(redirect(authorize_url + parameters))
    return response


@app.route('/callback')
def callback():
    code = request.args.get('code', None)
    print(f"CODE:{code}")
    state = request.args.get('state', None)
    session.pop('state_key', None)
    payload = connector.getToken(code)
    print("PAYLOAD: ")
    print(payload)
    if payload is not None:
        session['access_token'] = payload['access_token']
        session['refresh_token'] = payload['refresh_token']
        return redirect(session['previous_url'])
    else:
        return "FAILURE"


@app.route('/albums')
def get_albums():
    album_info = get_album_info(get_urls())
    return render_template('albums.html', album_info=album_info)


@app.route("/add-albums", methods=['GET'])
def add_albums():
    if session.get('access_token') is None:
        session['previous_url'] = '/albums'
        return redirect('/login')
    else:
        album_data_frame = pd.DataFrame(get_album_info(get_urls()))

        for artist, album_title, artwork in album_data_frame.values:
            # print(f"Searching for......{artist} - {album_title}")
            # print(session['refresh_token'])
            header = {"Authorization": "Bearer" + " " + connector.get_refresh_token(session['refresh_token'])}
            payload = {"q": album_title, "type": "album"}
            r = requests.get(SEARCH_URL, params=payload, headers=header).json()
            results = r["albums"]["items"]

            for i in results:
                album_id = i["id"]
                artists_dict = i["artists"]

                if i["album_type"] == "album" and i["name"].lower() == album_title:
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
            for track_request in playlist_tracks_request:
                print(track_request["track"]["uri"])
                current_playlist_ids.append(track_request["track"]["uri"])

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
    return redirect('/')


if __name__ == "__main__":
    app.run(host="0.0.0.0")
