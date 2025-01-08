import os
import sys
import traceback
import settings_lib
import colorama
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from ripper import Ripper
import spotiripper_helper

VERSION = "2024-12-31"
DRYRUN = False

current_path = spotiripper_helper.get_current_path()


def main():
    colorama.init()
    if not os.environ.get('PYTHONIOENCODING'):
        os.environ['PYTHONIOENCODING'] = str("utf-8")

    # Load settings
    settings = settings_lib.load_settings()

    # Understand what the command line input is
    if len(sys.argv) < 2:
        help()
        return
    elif len(sys.argv) == 2:
        tracks, _ = spotiripper_helper.parse_input(sys.argv[1])
    else:
        try:
            start_from = int(sys.argv[2]) - 1
        except:
            start_from = 0
        tracks, _ = spotiripper_helper.parse_input(sys.argv[1], start_from)

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
