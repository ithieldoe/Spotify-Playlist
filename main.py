from bs4 import BeautifulSoup
import requests
import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')

sp = spotipy.oauth2.SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri='http://example.com',
    scope='playlist-modify-private',
    cache_path='token.txt'
)

sp.get_access_token(as_dict=True)
token = open('token.txt', 'r')
cached_token = (eval(token.read())['access_token'])
client = spotipy.client.Spotify(auth=cached_token)
user_id = client.current_user()['id']
print(cached_token)


date = input('Which year do you want to travel to? Type the data in this format YYYY-MM-DD: ')
response = requests.get(f'https://www.billboard.com/charts/hot-100/{date}')
soup = BeautifulSoup(response.text, 'html.parser')
titles = [title.getText() for title in soup.find_all
    (name='span', class_='chart-element__information__song text--truncate color--primary')]
artists = [artist.getText() for artist in soup.find_all
    (name='span', class_='chart-element__information__artist text--truncate color--secondary')]
songs = list(zip(titles, artists))

YYYY = date[0:4]
song_uris = []
for title in titles:
    result = client.search(q=f'track: {title} year: {YYYY}', type='track')
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{title} doesn't exist in Spotify. Skipped.")

playlist = client.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)

client.playlist_add_items(playlist_id=playlist["id"], items=song_uris)