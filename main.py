'''
DOCUMENTATION
https://spotipy.readthedocs.io/en/2.19.0/
https://github.com/skybjohnson/spotipy_examples/blob/master/playlist_tracks_and_genre.py
https://stackoverflow.com/questions/53761033/pydub-play-audio-from-variable
https://betterprogramming.pub/simple-audio-processing-in-python-with-pydub-c3a217dabf11
'''

import subprocess, sys, os, time, shutil, eyed3
from urllib.request import urlopen
from recorder_pyaudio import Recorder
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import colorama
from pydub import AudioSegment

verbose = False


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


class Ripper:
    def __init__(self,
                 ripped_folder_structure='flat',
                 rip_storage_location=os.path.expanduser('~') + '/Downloads/Ripped/'):
        self.ripped_folder_structure = ripped_folder_structure
        self.rip_storage_location = rip_storage_location
        self.recorder = "internal"
        # self.converter = "ffmpeg"
        self.converter = "pydub"
        self.tmp_storage_location = 'tmp/'
        self.tmp_m4a_file_name = "tmp.m4a"
        self.tmp_mp3_file_name = "tmp.mp3"
        self.tmp_wav_file_name = "tmp.wav"
        self.recfile = None

        # Create directory for the ripped tracks
        if not os.path.exists(self.rip_storage_location):
            os.makedirs(self.rip_storage_location)

    def rip(self, track):

        # Clear all previous recordings if they exist
        for f in os.listdir(self.tmp_storage_location):
            os.remove(os.path.join(self.tmp_storage_location, f))

        # Tell Spotify to pause
        subprocess.Popen('osascript -e "tell application \\"Spotify\\" to pause"', shell=True,
                         stdout=subprocess.PIPE).stdout.read()
        time.sleep(.300)

        # Start recorder
        if self.recorder == "PIEZO":
            subprocess.Popen(
                'osascript -e "activate application \\"Piezo\\"" -e "tell application \\"System Events\\"" -e "keystroke \\"r\\" using {command down}" -e "end tell"',
                shell=True, stdout=subprocess.PIPE).stdout.read()

        elif self.recorder == "QT":
            subprocess.Popen(
                'osascript -e "tell application \\"QuickTime Player\\" to activate" -e "tell application \\"QuickTime Player\\" to start (new audio recording)"',
                shell=True, stdout=subprocess.PIPE).stdout.read()

        elif self.recorder == "internal":
            self.recfile = Recorder(self.tmp_storage_location + self.tmp_wav_file_name, 'wb', 2, 44100, 1024)
            self.recfile.start_recording()
            if verbose:
                print("Recording started.")

        # Tell Spotify to play a specified song
        subprocess.Popen(
            'osascript -e "tell application \\"Spotify\\"" -e "play track \\"' + track + '\\"" -e "end tell"',
            shell=True, stdout=subprocess.PIPE).stdout.read()

        time.sleep(1)

        # Get the artist name, track name, album name and album artwork URL from Spotify
        artist = subprocess.Popen(
            'osascript -e "tell application \\"Spotify\\"" -e "current track\'s artist" -e "end tell"', shell=True,
            stdout=subprocess.PIPE).stdout.read().decode('utf-8').rstrip('\r\n')
        track = subprocess.Popen(
            'osascript -e "tell application \\"Spotify\\"" -e "current track\'s name" -e "end tell"',
            shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').rstrip('\r\n')
        album = subprocess.Popen(
            'osascript -e "tell application \\"Spotify\\"" -e "current track\'s album" -e "end tell"',
            shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').rstrip('\r\n')
        artwork = subprocess.Popen(
            'osascript -e "tell application \\"Spotify\\"" -e "current track\'s artwork url" -e "end tell"', shell=True,
            stdout=subprocess.PIPE).stdout.read().decode('utf-8').rstrip('\r\n')
        artworkdata = urlopen(artwork).read()

        try:
            print(colorama.Back.LIGHTGREEN_EX,
                  "{}, {}".format(artist, track),
                  colorama.Style.RESET_ALL)
        except:
            print(colorama.Back.LIGHTGREEN_EX,
                  "{}, {}".format(artist, track).encode('ascii', 'replace'),
                  colorama.Style.RESET_ALL)
            print(colorama.Fore.LIGHTYELLOW_EX,
                  "The song name contains accented characters that cannot be displayed correctly. Make sure you set \"export PYTHONIOENCODING=utf-8\".",
                  colorama.Style.RESET_ALL)

        # Check every 500 milliseconds if Spotify has stopped playing
        while subprocess.Popen('osascript -e "tell application \\"Spotify\\"" -e "player state" -e "end tell"',
                               shell=True,
                               stdout=subprocess.PIPE).stdout.read() == b"playing\n":
            time.sleep(.500)

        # Spotify has stopped playing, stop recording
        if self.recorder == "PIEZO":
            subprocess.Popen(
                'osascript -e "activate application \\"Piezo\\"" -e "tell application \\"System Events\\"" -e "keystroke \\"r\\" using {command down}" -e "end tell"',
                shell=True, stdout=subprocess.PIPE).stdout.read()

        elif self.recorder == "QT":
            command = ["osascript",
                       "-e",
                       "set tFile to \"" + self.tmp_storage_location + self.tmp_m4a_file_name + "\" as posix file",
                       "-e", "do shell script \"touch \" & quoted form of posix path of tFile",
                       "-e", "tell application \"QuickTime Player\"",
                       "-e", "pause document 1",
                       "-e", "save document 1 in tFile",
                       "-e", "stop document 1",
                       "-e", "close document 1 saving no",
                       "-e", "quit",
                       "-e", "end tell"]
            p = subprocess.Popen(command)

            time.sleep(1.000)
            print("Converting to mp3...")

            # Convert m4a to mp3 using ffmpeg
            try:
                subprocess.call(['ffmpeg', '-i', f'{self.tmp_storage_location + self.tmp_m4a_file_name}',
                                 f'{self.tmp_storage_location + self.tmp_mp3_file_name}'])
            except Exception as e:
                print(e)
                print('Error While Converting Audio')

        elif self.recorder == "internal":
            self.recfile.stop_recording()
            if verbose:
                print("Recording stopped.")

            if self.converter == "ffmpeg":
                if verbose:
                    print("Converting to mp3...")
                try:
                    subprocess.call(['ffmpeg',
                                     '-loglevel',
                                     'quiet',
                                     '-channel_layout',
                                     'stereo',
                                     '-i', f'{self.tmp_storage_location + self.tmp_wav_file_name}',
                                     '-af',
                                     'volume=4.0',
                                     f'{self.tmp_storage_location + self.tmp_mp3_file_name}'])
                except Exception as e:
                    print('Error during conversion: {}'.format(e))
                else:
                    if verbose:
                        print("Converted.")

            elif self.converter == "pydub":
                if verbose:
                    print("Converting to mp3...")

                # Remove initial noise and convert
                # For some reason the initial 160ms of the recording are sometimes a very high volume "white" noise
                sound = AudioSegment.from_file(self.tmp_storage_location + self.tmp_wav_file_name, format="wav")
                # start_trim = detect_leading_silence(sound)
                # end_trim = detect_leading_silence(sound.reverse())
                start_trim = 200
                trimmed_sound = sound[start_trim:]
                output = AudioSegment.empty()
                output = trimmed_sound
                output.apply_gain(12.041199826559245)
                output.export(self.tmp_storage_location + self.tmp_mp3_file_name, format="mp3")

                if verbose:
                    print("Converted.")

        time.sleep(.500)

        # Set and/or update ID3 information
        mp3file = eyed3.load(self.tmp_storage_location + self.tmp_mp3_file_name)
        mp3file.tag.images.set(3, artworkdata, "image/jpeg", track)
        mp3file.tag.artist = artist
        mp3file.tag.album = album
        mp3file.tag.title = track
        mp3file.tag.save()

        # Move to final location
        if self.ripped_folder_structure == "flat":
            for f in os.listdir(self.tmp_storage_location):
                if f.endswith(".mp3"):
                    shutil.move(self.tmp_storage_location + f,
                                self.rip_storage_location + artist + ", " + album + ", " + track + ".mp3")

        elif self.ripped_folder_structure == "tree":
            # Create directory for the artist
            if not os.path.exists(self.rip_storage_location + artist):
                os.makedirs(self.rip_storage_location + artist)

            # Create directory for the album
            if not os.path.exists(self.rip_storage_location + artist + "/" + album):
                os.makedirs(self.rip_storage_location + artist + "/" + album)

            # Move MP3 file to the folder containing rips.
            for f in os.listdir(self.tmp_storage_location):
                if f.endswith(".mp3"):
                    shutil.move(self.tmp_storage_location + f,
                                self.rip_storage_location + artist + "/" + album + "/" + track + ".mp3")


def main():
    colorama.init()
    if not os.environ.get('PYTHONIOENCODING'):
        os.environ['PYTHONIOENCODING'] = str("utf-8")

    # Understand what the command line input is
    if len(sys.argv[1]) < 4:
        print("Usage:")
        print("    spotiripper <track URI>")
        print("    spotiripper <track URL>")
        print("    spotiripper <list.txt containing track URIs or URLs>")
        print("    spotiripper <playlist URI>    Note: requires setting Spotify Client ID and Client Secret keys.")
        print("    spotiripper <playlist URL>    Note: requires setting Spotify Client ID and Client Secret keys.")
        return -1

    else:
        # A track URI or URL?
        if sys.argv[1][:14] == "spotify:track:" or sys.argv[1][:31] == "https://open.spotify.com/track/":
            tracks = [sys.argv[1]]

        # A txt list with track URIs or URLs?
        elif sys.argv[1][-4:] == ".txt":
            file = open(sys.argv[1])
            tracks = file.readlines()
            file.close()

        # A playlist URI or URL?
        elif sys.argv[1][:17] == "spotify:playlist:" or sys.argv[1][:34] == "https://open.spotify.com/playlist/":
            print(
                "Fetching a playlist requires user authentication. Make sure Spotify Client ID and Client Secret are set.")

            # Authenticating into spotify
            auth_manager = SpotifyClientCredentials()
            sp = spotipy.Spotify(auth_manager=auth_manager)

            # Fetching tracks in the playlist
            results = sp.playlist_items(sys.argv[1])
            tracks = results['items']
            while results['next']:
                results = sp.next(results)
                tracks.extend(results['items'])
            uris = []
            for item in tracks:
                track = item['track']
                uris.append(track['uri'])
            tracks = uris

        else:
            print("Unknown input")
            tracks = []

        # Rip
        print("Ripping {} tracks.".format(len(tracks)))
        for track in tracks:
            ripper = Ripper()
            track = convert_to_uri(track.rstrip())
            print("Ripping track {}...".format(track))
            ripper.rip(track)


main()
