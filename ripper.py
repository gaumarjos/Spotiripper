import os
import shutil
import subprocess
import time
import threading
from urllib.request import urlopen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TRCK, TDRC, TPOS, TPE2, APIC, COMM
import colorama
import csv
import helper
# from converter_ffmpeg import convert_to_mp3
from converter_pydub import convert_to_mp3
# from recorder_pyaudio import Recorder
from recorder_sounddevice import Recorder
import player_macos
import pync


def push_notification(title, message):
    '''
    subprocess.Popen(
        'osascript -e "display notification \\"' + message + '\\" with title \\"' + title + '\\""',
        shell=True, stdout=subprocess.PIPE).stdout.read()
    '''
    pync.Notifier.notify(message, title=title, icon='icon.icns')


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

        # Track info
        self.info_title = None
        self.info_artist = None
        self.info_album = None
        self.info_disc_nr = None
        self.info_track_nr = None
        self.info_album_artist = None
        self.info_artworkdata = None

    # Function to be called when the timer expires
    def timer_expired(self):
        # Tell Spotify to pause
        player_macos.pause()

    # Function to start the timer
    def start_timer(self, seconds):
        timer = threading.Timer(seconds, self.timer_expired)
        timer.start()
        return timer

    # Function to check if the track has stopped playing
    def check_condition(self):
        return not player_macos.get_status()

    # Function to check the above condition at intervals
    def check_condition_with_intervals(self, timer, interval, total_duration):
        for _ in range(int(total_duration / interval)):

            # Monitor progress. For some reason, even though the interval time is set to 0.5, the measured average is
            # 0.85 with a minimal jitter.

            if self.check_condition():
                # print("Condition met! Continuing without waiting for the timer.")
                timer.cancel()  # Cancel the timer if the condition is met
                return True  # Indicate that the condition was met
            time.sleep(interval)
        return False  # Indicate that the condition was not met

    # Set ID3 information
    def tag(self):
        '''
        TIT2: Title of the track
        TPE1: Artist name (Lead performer(s))
        TPE2: Band or orchestra (e.g., performing group)
        TALB: Album name
        TCON: Genre (e.g., Rock, Pop)
        TRCK: Track number (e.g., 01)
        TPOS: Part of a set (e.g., Disc number)
        TDRC: Release date (Year)
        COMM: Comments (e.g., additional notes)
        APIC: Attached picture (e.g., album cover art)
        TCOM: Composer
        TPUB: Publisher
        TXXX: User-defined text information frame
        WXXX: User-defined URL link frame
        TXXX: User-defined text information frame
        TLEN: Length of the audio file in milliseconds
        TSSE: Software used to encode the file
        TORY: Original release year
        TSOA: Album sort order
        TSOP: Performer sort order
        TSOT: Title sort order
        '''
        audio = MP3(self.tmp_dir + self.tmp_mp3, ID3=ID3)
        audio.tags.add(TIT2(encoding=3, text=self.info_title))
        audio.tags.add(TPE1(encoding=3, text=self.info_artist))
        audio.tags.add(TALB(encoding=3, text=self.info_album))
        audio.tags.add(TRCK(encoding=3, text=self.info_track_nr))
        audio.tags.add(TPOS(encoding=3, text=self.info_disc_nr))
        audio.tags.add(TPE2(encoding=3, text=self.info_album_artist))
        audio.tags.add(APIC(
            encoding=3,  # UTF-8
            mime='image/jpeg',  # MIME type of the image
            type=3,  # Type 3 is for front cover
            desc='Cover',  # Description of the image
            data=self.info_artworkdata  # The actual image data
        ))
        audio.tags.add(COMM(encoding=3, text='Ripped from Spotify'))
        # audio.tags.add(TDRC(encoding=3, text='2024'))  # Release year
        audio.save()

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
        player_macos.pause()
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
        player_macos.play(trackuri)

        # Start recording
        self.recfile.start_recording()

        time.sleep(1.0)

        # Get track duration in ms asap
        track_duration = int(player_macos.get_duration())

        # Start timer with the same duration of the song. TODO Verify if -1 is ok. Without, it seems 1s too long.
        timer = self.start_timer(track_duration / 1000. - 1.0)
        # timer = self.start_timer(10)

        # Get the artist name, track name, album name and album artwork URL from Spotify
        self.info_title = player_macos.get_title()
        self.info_artist = player_macos.get_artist()
        self.info_album = player_macos.get_album()
        artwork_url = player_macos.get_artwork_url()
        self.info_disc_nr = player_macos.get_disc_nr()
        self.info_track_nr = player_macos.get_track_nr()
        self.info_album_artist = player_macos.get_album_artist()

        # Added because this is sometimes empty (debug)
        if artwork_url is not None and len(artwork_url) > 0:
            self.info_artworkdata = urlopen(artwork_url).read()
        else:
            self.info_artworkdata = None

        # Log to CSV
        with open(os.path.join(self.current_path, "log.csv"), 'a') as logfile:
            log = csv.writer(logfile)
            log.writerow([trackuri, self.info_artist, self.info_title, self.info_album])

        # Print artist and track names extracted from Spotify
        toprint = "{}, {}, {} ({})".format(self.info_artist, self.info_album, self.info_title,
                                           helper.ms2str(track_duration))
        if self.gui:
            self.gui_progress_callback.emit(toprint)
        else:
            try:
                print(colorama.Back.LIGHTGREEN_EX,
                      toprint + (self.terminal_width - len(toprint) - 6) * ' ',
                      colorama.Style.RESET_ALL)
                push_notification("Start recording", toprint)
            except:
                toprint = toprint.encode('ascii', 'replace')
                print(colorama.Back.LIGHTGREEN_EX,
                      toprint + (self.terminal_width - len(toprint) - 6) * ' ',
                      colorama.Style.RESET_ALL)
                print(colorama.Fore.LIGHTYELLOW_EX,
                      "The song name contains accented characters that cannot be displayed correctly. Make sure you set \"export PYTHONIOENCODING=utf-8\".",
                      colorama.Style.RESET_ALL)

        # Sometimes, Spotify does not stop. It's not clear to me if it does with some albums and not with others, but
        # the fact is that sometimes it goes on playing the next song. Therefore, Spotiripper cannot detect the end and
        # keeps on recording. It also doesn't launch the next song.
        # I know the track's duration, so I could record for a definite amount of time and then tell Spotify to stop.

        # Polling solution (solution 1)
        '''
        while player_macos.get_status():
            time.sleep(.500)
        '''

        # Timer solution (solution 2)
        '''
        timer.join()
        '''

        # Timer and polling solution together (solution 3)
        # It polls the spotify app to check if the track is still playing. When the duration of the track is reached,
        # though, it stops recording in any case. This implementation is both responsive to pausing the track or to an
        # early finish and protected against Spotify's tendency to play tracks back to back without interruption.
        if not self.check_condition_with_intervals(timer=timer, interval=0.5,
                                                   total_duration=track_duration / 1000.0 - 1.0):
            # Wait for the timer to finish if condition was not met
            timer.join()

        # Spotify has stopped playing, stop recording
        self.recfile.stop_recording()
        push_notification("Stop recording", toprint)

        # Convert to mp3 and notify if an error occurs
        if convert_to_mp3(self.tmp_dir + self.tmp_wav,
                          self.tmp_dir + self.tmp_mp3):
            push_notification("Converted", toprint)
        else:
            toprint = "Error in conversion."
            if self.gui:
                self.gui_progress_callback.emit(toprint)
            else:
                print(toprint)

        time.sleep(.500)

        # Set and/or update ID3 information
        self.tag()

        # Move to final location
        destination_filename = self.rip_dir + remove_bad_characters(self.info_artist) + ", " + remove_bad_characters(
            self.info_album) + ", " + remove_bad_characters(self.info_title) + ".mp3"

        if self.ripped_folder_structure == "flat":
            for f in os.listdir(self.tmp_dir):
                if f.endswith(".mp3"):
                    shutil.move(self.tmp_dir + f,
                                destination_filename)

        elif self.ripped_folder_structure == "tree":
            # Create directory for the artist
            if not os.path.exists(self.rip_dir + self.info_artist):
                os.makedirs(self.rip_dir + self.info_artist)

            # Create directory for the album
            if not os.path.exists(self.rip_dir + self.info_artist + "/" + self.info_album):
                os.makedirs(self.rip_dir + self.info_artist + "/" + self.info_album)

            # Move MP3 file to the folder containing rips.
            for f in os.listdir(self.tmp_dir):
                if f.endswith(".mp3"):
                    shutil.move(self.tmp_dir + f,
                                self.rip_dir + self.info_artist + "/" + self.info_album + "/" + self.info_title + ".mp3")
