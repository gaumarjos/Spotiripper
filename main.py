import os
import sys
import argparse
import traceback
import settings_lib
import colorama
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from ripper import Ripper
import spotiripper_helper

VERSION = "2025-01-08"
DRYRUN = True

current_path = spotiripper_helper.get_current_path()


def main():
    colorama.init()
    if not os.environ.get('PYTHONIOENCODING'):
        os.environ['PYTHONIOENCODING'] = str("utf-8")

    # Load settings
    settings = settings_lib.load_settings()

    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Record music from Spotify as MP3 files.")
    parser.add_argument('link', type=str,
                        help='Link to the resource to be recorded. It can be a track, a playlist, an album, an artist uri or url, as well as a .txt file containing a list of those.')
    parser.add_argument('-s', '--start_from', type=int, default=1,
                        help='In case a link containing more than one track is provided, from which track of the list to start. The first is 1.')

    # Parse arguments
    args = parser.parse_args()
    tracks, _ = spotiripper_helper.parse_input(args.link, args.start_from-1)

    print("Ripping {} track{}.".format(len(tracks), "s" if len(tracks) > 1 else ""))
    for track in tracks:
        if not DRYRUN:
            ripper = Ripper(current_path=current_path,
                            rip_dir=settings["rip_dir"],
                            ripped_folder_structure=settings["ripped_folder_structure"])
            ripper.rip(spotiripper_helper.convert_to_uri(track.rstrip()))
        else:
            print(track)
    return


if __name__ == "__main__":
    if not os.path.exists(os.path.join(current_path, "settings.json")):
        settings_lib.create_settings()
    main()
