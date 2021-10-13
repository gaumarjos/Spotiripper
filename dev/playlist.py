import spotipy
from spotipy.oauth2 import SpotifyOAuth


def convert_to_uri(s):
    # It's already an URI
    if s[:14] == "spotify:track:" or s[:17] == "spotify:playlist:":
        return (s)
    # It's a track URL and must be converted into a track URI
    elif s[:31] == "https://open.spotify.com/track/":
        return "spotify:track:" + s[31:53]
    # It's a playlist URL and must be converted into a playlist URI
    elif s[:34] == "https://open.spotify.com/playlist/":
        return "spotify:playlist:" + s[34:56]
    else:
        return -1

'''
scope = "user-library-read"


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="fac9a2b326fc492ab58611d32b2aae09",
                                               client_secret="39f5a3a9f1ba4fb9b4992df531042fbb",
                                               redirect_uri="https://www.stefanosalati.com/",
                                               scope=scope))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])

# redirect_uri="http://localhost:8080",


'''

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import csv







auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)




playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DX3kkOVvCOkIe?si=5da598c4921e44ed"

results = sp.playlist_items(playlist_url)
tracks = results['items']
while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])
uris = []
for item in (tracks):
    track = item['track']
    uris.append(track['uri'])

print(uris)
print(len(uris))

'''
## create a csv of track->genre mappings
with open('irish_tracks_genres.csv', mode='w') as genre_file:
    spotify_writer = csv.writer(genre_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spotify_writer.writerow(['Track URI', 'Genre'])

    for item in (tracks):
        track = item['track']

        if "local" in track['uri']:
            continue

        artist = sp.artist(track['artists'][0]['uri'])

        for g in (artist['genres']):
            # print(g)
            spotify_writer.writerow([track['uri'], g])



# Open and configure output csv
with open('irish_tracks.csv', mode='w') as track_file:
    spotify_writer = csv.writer(track_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # Write csv headers
    spotify_writer.writerow(['Index','Track URI', 'Artist Name', 'Track Name', 'Release Date','Danceability','Energy','Key','Loudness','Mode','Speechiness','Accousticness','Instrumentalness','Liveness','Valence','Tempo','Duration MS','Time Signature','genres','popularity'])

    # index
    i = 0

    # for each track in the playlist, gather more information and write to csv
    for item in (tracks):
        i = i + 1
        track = item['track']

        # if the track is a local file, skip it
        if "local" in track['uri']:
            continue


        # Three more API calls to get more track-related information
        audio_features = sp.audio_features(track['uri'])[0]
        release_date = sp.track(track['uri'])['album']['release_date']
        artist = sp.artist(track['artists'][0]['uri'])


        # popularity
        popularity = track['popularity']
        # print(popularity)
        # print("|".join(artist['genres']))

        # print to console for debugging
        print("   %d %32.32s %s %s" % (i, track['artists'][0]['name'], track['name'],release_date))

        # write to csv
        spotify_writer.writerow([i, track['uri'], track['artists'][0]['name'], track['name'], release_date
                                , audio_features['danceability']
                                , audio_features['energy']
                                , audio_features['key']
                                , audio_features['loudness']
                                , audio_features['mode']
                                , audio_features['speechiness']
                                , audio_features['acousticness']
                                , audio_features['instrumentalness']
                                , audio_features['liveness']
                                , audio_features['valence']
                                , audio_features['tempo']
                                , audio_features['duration_ms']
                                , audio_features['time_signature'],
                                 "|".join(artist['genres']),popularity])
'''

