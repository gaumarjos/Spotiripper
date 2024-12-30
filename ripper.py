import os
import shutil
import subprocess
import time
from urllib.request import urlopen
import eyed3
import colorama
import csv
# from converter_ffmpeg import convert_to_mp3
from converter_pydub import convert_to_mp3
# from recorder_pyaudio import Recorder
from recorder_sounddevice import Recorder


# from plyer import notification


def push(title, message):
    subprocess.Popen(
        'osascript -e "display notification \\"' + message + '\\" with title \\"' + title + '\\""',
        shell=True, stdout=subprocess.PIPE).stdout.read()

    '''
    notification.notify(
        title=title,
        message=message,
        app_icon="spotiripper.png",
        timeout=50
    )
    '''


def remove_bad_characters(s):
    bad_chars = [';', ':', '!', '*', '/', '\\']
    for i in bad_chars:
        s = s.replace(i, '')
    return s


class Ripper:
    def __init__(self,
                 current_path,
                 rip_dir=os.path.expanduser('~') + '/Downloads/Ripped/',
                 ripped_folder_structure='flat',
                 gui=False,
                 gui_progress_callback=None,
                 gui_soundbar_callback=None):
        self.current_path = current_path
        self.ripped_folder_structure = ripped_folder_structure
        self.rip_dir = rip_dir
        self.tmp_dir = self.rip_dir + '.tmp/'
        self.tmp_wav = "tmp.wav"
        self.tmp_mp3 = "tmp.mp3"
        self.recfile = None
        # self.converter = "ffmpeg"
        self.converter = "pydub"

        # Create directory for the ripped tracks
        if not os.path.exists(self.rip_dir):
            os.makedirs(self.rip_dir)
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)

        # Determine width of terminal window to fit soundbar
        self.terminal_width = shutil.get_terminal_size((80, 20)).columns

        # Taking GUI elements as parameters in order to write on them
        self.gui = gui
        self.gui_progress_callback = gui_progress_callback
        self.gui_soundbar_callback = gui_soundbar_callback

    def rip(self, trackuri):
        toprint = "Track uri: {}".format(trackuri)
        if self.gui:
            self.gui_progress_callback.emit(toprint)
        else:
            print(toprint + (self.terminal_width - len(toprint)) * ' ')

        # Clear all previous recordings if they exist
        for f in os.listdir(self.tmp_dir):
            os.remove(os.path.join(self.tmp_dir, f))

        # Tell Spotify to pause
        subprocess.Popen('osascript -e "tell application \\"Spotify\\" to pause"', shell=True,
                         stdout=subprocess.PIPE).stdout.read()
        time.sleep(.300)

        # Start recorder
        self.recfile = Recorder(self.tmp_dir + self.tmp_wav,
                                terminal_width=self.terminal_width,
                                gui=self.gui,
                                gui_progress_callback=self.gui_progress_callback,
                                gui_soundbar_callback=self.gui_soundbar_callback)
        # self.recfile.getinfo()

        # RECORDING USED TO BE HERE
        # self.recfile.start_recording()

        # Tell Spotify to play a specified song
        subprocess.Popen(
            'osascript -e "tell application \\"Spotify\\"" -e "play track \\"' + trackuri + '\\"" -e "end tell"',
            shell=True, stdout=subprocess.PIPE).stdout.read()

        # RECORDING MOVED HERE
        self.recfile.start_recording()

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

        # Added because this is sometimes empty (debug)
        if artwork is not None and len(artwork) > 0:
            artworkdata = urlopen(artwork).read()
        else:
            artworkdata = None

        # Log to CSV
        with open(os.path.join(self.current_path, "log.csv"), 'a') as logfile:
            log = csv.writer(logfile)
            log.writerow([trackuri, artist, track, album])

        # Print artist and track names extracted from Spotify
        toprint = "Track: {}, {}".format(artist, track)
        if self.gui:
            self.gui_progress_callback.emit(toprint)
        else:
            try:
                print(colorama.Back.LIGHTGREEN_EX,
                      toprint + (self.terminal_width - len(toprint) - 6) * ' ',
                      colorama.Style.RESET_ALL)
                push("Start recording", toprint)
            except:
                toprint = toprint.encode('ascii', 'replace')
                print(colorama.Back.LIGHTGREEN_EX,
                      toprint + (self.terminal_width - len(toprint) - 6) * ' ',
                      colorama.Style.RESET_ALL)
                print(colorama.Fore.LIGHTYELLOW_EX,
                      "The song name contains accented characters that cannot be displayed correctly. Make sure you set \"export PYTHONIOENCODING=utf-8\".",
                      colorama.Style.RESET_ALL)

        # Check every 500ms if Spotify has stopped playing
        while subprocess.Popen('osascript -e "tell application \\"Spotify\\"" -e "player state" -e "end tell"',
                               shell=True,
                               stdout=subprocess.PIPE).stdout.read() == b"playing\n":
            time.sleep(.500)

        # Spotify has stopped playing, stop recording
        self.recfile.stop_recording()
        push("Stop recording", toprint)

        # Convert to mp3 and notify if an error occurs
        if convert_to_mp3(self.tmp_dir + self.tmp_wav,
                          self.tmp_dir + self.tmp_mp3):
            push("Converted", toprint)
        else:
            toprint = "Error in conversion."
            if self.gui:
                self.gui_progress_callback.emit(toprint)
            else:
                print(toprint)

        time.sleep(.500)

        # Set and/or update ID3 information
        mp3file = eyed3.load(self.tmp_dir + self.tmp_mp3)
        if artworkdata is not None:
            mp3file.tag.images.set(3, artworkdata, "image/jpeg", track)
        mp3file.tag.artist = artist
        mp3file.tag.album = album
        mp3file.tag.title = track
        mp3file.tag.save()
        destination_filename = self.rip_dir + remove_bad_characters(artist) + ", " + remove_bad_characters(
            album) + ", " + remove_bad_characters(track) + ".mp3"

        # Move to final location
        if self.ripped_folder_structure == "flat":
            for f in os.listdir(self.tmp_dir):
                if f.endswith(".mp3"):
                    shutil.move(self.tmp_dir + f,
                                destination_filename)

        elif self.ripped_folder_structure == "tree":
            # Create directory for the artist
            if not os.path.exists(self.rip_dir + artist):
                os.makedirs(self.rip_dir + artist)

            # Create directory for the album
            if not os.path.exists(self.rip_dir + artist + "/" + album):
                os.makedirs(self.rip_dir + artist + "/" + album)

            # Move MP3 file to the folder containing rips.
            for f in os.listdir(self.tmp_dir):
                if f.endswith(".mp3"):
                    shutil.move(self.tmp_dir + f,
                                self.rip_dir + artist + "/" + album + "/" + track + ".mp3")
