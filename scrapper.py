import requests
import json
import pandas as pd
import base64
from bs4 import BeautifulSoup

PREFERRED_GENRES = ["Experimental", "Rap", "Electronic"]


def get_urls():
    url_info = []
    for page in range(1, 4):
        url = f"https://pitchfork.com/reviews/albums/?page={page}"
        req = requests.get(url)
        soup = BeautifulSoup(req.content, "html.parser")
        reviews = soup.find_all("div", class_="review")
        for items in reviews:
            try:
                artist = (items.find("li").string).lower()
                title = (items.find("h2").string).lower()
                genre = items.find(class_="genre-list")
                url = items.find("a").get('href')
                final_url = f"https://pitchfork.com{url}"
                preferred_genre = [
                    genre_item
                    for genre_item in PREFERRED_GENRES
                    if (genre_item in genre.text)
                ]
                if genre is not None and preferred_genre:
                    url_info.append({"url": final_url})
            except:
                pass
    return url_info


def get_album_info(url_info):
    album_info = []
    for url in url_info:
        req = requests.get(url['url'])
        soup = BeautifulSoup(req.content, "html.parser")
        main_header = soup.find_all("header", class_="SplitScreenContentHeaderWrapper-bFxPWy")
        for info in main_header:
            artist = info.find("div", class_="SplitScreenContentHeaderArtist-ftloCc").string.lower()
            album_title = info.find("em").string.lower()
            artwork = info.find("img").get("src")
            album_info.append({"artist": artist, "album_title": album_title, "artwork": artwork})
    return album_info
    # print(artwork.get("src"))
    # album_info.append({"artwork": artwork.get("src"),})
