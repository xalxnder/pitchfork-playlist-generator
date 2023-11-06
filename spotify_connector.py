import requests
import base64
import os
import random as rand
import string as string

# Obtained from your app dashboard
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
# Obtained after the initial user authorization request
CODE = os.getenv("CODE")
STATE = os.getenv("STATE")
# Obtained in the response body when requesting the access token
ACCESS_TOKEN = os.getenv("SPOTIFY_ACCESS_TOKEN")

AUTH_URL = "https://accounts.spotify.com/api/token"


class SpotifyConnector:
    def get_auth_base64(self, id, secret):
        """Used to encode our Client ID and Client Secret when retriving your refresh token"""
        message = f"{id}:{secret}"
        message_bytes = message.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode("ascii")
        auth_header = {"Authorization": "Basic" + " " + base64_message}
        return auth_header

    def getToken(self, code):
        """Used to retrieve your access token AFTER the user initially accepts your request"""
        message = f"{CLIENT_ID}:{CLIENT_SECRET}"
        print(f"MESSAGE: {message}")

        message_bytes = message.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode("ascii")
        auth_header = {"Authorization": "Basic" + " " + base64_message}
        print(f"AUTH_HEADER{auth_header}")
        auth_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:5000/callback",
        }
        print(f"AUTH_DATA{auth_data}")
        r = requests.post(AUTH_URL, headers=auth_header, data=auth_data)
        response = r.json()
        print("RESPONSE")
        print(response)
        return response

    def get_refresh_token(self, refresh_token):
        """Used to generate a refresh token"""
        refresh_body = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        headers = self.get_auth_base64(CLIENT_ID, CLIENT_SECRET)
        token = requests.post(AUTH_URL, headers=headers, data=refresh_body).json()
        # print(token)
        return token["access_token"]

    def create_state_key(self, size):
        # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
        return ''.join(rand.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(size))
