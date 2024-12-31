import os
import sys
import settings_lib
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

MACOSRED = (236, 95, 93)
MACOSORANGE = (232, 135, 58)
MACOSYELLOW = (255, 200, 60)
MACOSGREEN = (120, 183, 86)
MACOSCYAN = (84, 153, 166)
MACOSBLUE = (48, 123, 246)
MACOSMAGENTA = (154, 86, 163)
MACOSDARK = (46, 46, 46)


def get_current_path():
    if getattr(sys, 'frozen', False):
        current_path = os.path.dirname(sys.executable)
        # print("Running as an executable: {}".format(current_path))
    else:
        current_path = str(os.path.dirname(__file__))
        # print("Running as a script: {}".format(current_path))
    return current_path


def help():
    print("Usage:")
    print("    spotiripper <track URI>")
    print("    spotiripper <track URL>")
    print("    spotiripper <list.txt containing track URIs or URLs>")
    print("    spotiripper <playlist URI>    (*)")
    print("    spotiripper <playlist URL>    (*)")
    print("    spotiripper <album URI>       (*)")
    print("    spotiripper <album URL>       (*)")
    print("    spotiripper <artist URI>      Downloads the artist's top 10 tracks. (*)")
    print("    spotiripper <artist URL>      Downloads the artist's top 10 tracks. (*)")
    print()
    print("(*) Note: requires setting Spotify Client ID and Client Secret keys.")
    print("    export SPOTIPY_CLIENT_ID='yourclientid'")
    print("    export SPOTIPY_CLIENT_SECRET='yourclientsecret'")
    return 1


def convert_to_uri(s):
    # It's already an URI
    if s[:14] == "spotify:track:" or s[:17] == "spotify:playlist:":
        return s
    # It's a track URL and must be converted into a track URI
    elif s[:31] == "https://open.spotify.com/track/":
        return "spotify:track:" + s[31:53]
    # It's a playlist URL and must be converted into a playlist URI
    elif s[:34] == "https://open.spotify.com/playlist/":
        return "spotify:playlist:" + s[34:56]
    else:
        return -1


def verify_spotipy_client_credentials():
    # First, check if credentials are stored somewhere
    settings = settings_lib.load_settings()
    spotipy_client_set = (settings["spotipy_client_id"] != "" and settings["spotipy_client_secret"] != "") or (
            os.environ.get("SPOTIPY_CLIENT_ID") is not None and os.environ.get("SPOTIPY_CLIENT_SECRET") is not None)

    if spotipy_client_set:
        # Second, try to authenticate
        # Try with those stored in settings first
        try:
            auth_manager = SpotifyClientCredentials(settings["spotipy_client_id"], settings["spotipy_client_secret"])
            sp = spotipy.Spotify(auth_manager=auth_manager)
            return sp
        except:
            # If they don't work, try with those in env variables
            try:
                auth_manager = SpotifyClientCredentials()
                sp = spotipy.Spotify(auth_manager=auth_manager)
                return sp
            except:
                return None
    else:
        return None


def parse_input(link, start_from=0):
    track_list = []
    error = None

    # A track URI or URL?
    if link.startswith("spotify:track:") or link.startswith("https://open.spotify.com/track/"):
        track_list = [link]

    # A txt list with track URIs or URLs?
    elif link.endswith(".txt"):
        file = open(link)
        track_list = file.readlines()
        file.close()

    # A playlist URI or URL?
    elif link.startswith("spotify:playlist:") or link.startswith("https://open.spotify.com/playlist/"):
        sp = verify_spotipy_client_credentials()
        if sp is not None:
            # Fetching tracks in the playlist
            results = sp.playlist_items(link)
            items = results['items']
            while results['next']:
                results = sp.next(results)
                items.extend(results['items'])
            uris = []
            for item in items:
                track = item['track']
                uris.append(track['uri'])
            track_list = uris
        else:
            track_list = []
            error = 'spotipy_keys'

    # An album URI or URL?
    elif link.startswith("spotify:album:") or link.startswith("https://open.spotify.com/album/"):
        sp = verify_spotipy_client_credentials()
        if sp is not None:
            # Fetching tracks in the album
            results = sp.album_tracks(link)
            items = results['items']
            while results['next']:
                results = sp.next(results)
                items.extend(results['items'])
            urls = []
            for item in items:
                track = item['external_urls']
                urls.append(track['spotify'])
            track_list = urls
        else:
            track_list = []
            error = 'spotipy_keys'

    # An artist URI or URL?
    elif link.startswith("spotify:artist:") or link.startswith("https://open.spotify.com/artist/"):
        sp = verify_spotipy_client_credentials()
        if sp is not None:
            # Fetching this artist's top tracks
            results = sp.artist_top_tracks(link)
            items = results['tracks']
            urls = []
            for item in items:
                track = item['external_urls']
                urls.append(track['spotify'])
            track_list = urls
        else:
            track_list = []
            error = 'spotipy_keys'

    else:
        track_list = []
        error = 'unknown_input'

    if start_from == 0:
        return track_list, error
    else:
        return track_list[start_from:], error


def resource_path(path):
    # Needed only is the path is relative
    if not os.path.isabs(path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, path)
        return os.path.join(os.path.abspath('build'), path)
    else:
        return path


def ms2str(ms):
    # Calculate total seconds and milliseconds
    total_seconds = ms // 1000
    milliseconds = ms % 1000

    # Calculate minutes and seconds
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    # Format the string as mm:ss.ms
    formatted_length = f"{minutes:02}:{seconds:02}.{milliseconds:03}"
    return formatted_length
