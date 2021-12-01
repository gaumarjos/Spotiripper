'''
DOCUMENTATION
https://bartsimons.me/ripping-spotify-songs-on-macos/
https://spotipy.readthedocs.io/en/2.19.0/
https://github.com/skybjohnson/spotipy_examples/blob/master/playlist_tracks_and_genre.py
https://stackoverflow.com/questions/53761033/pydub-play-audio-from-variable
https://betterprogramming.pub/simple-audio-processing-in-python-with-pydub-c3a217dabf11
'''

import eyed3
import os
import shutil
import subprocess
import sys
import time
import traceback
from urllib.request import urlopen
import colorama
# from converter_ffmpeg import convert_to_mp3
import spotipy
from PySide6.QtCore import Qt, QSize, QRunnable, Slot, Signal, QObject, QThreadPool
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QSpinBox, QLabel, \
    QProgressBar
from spotipy.oauth2 import SpotifyClientCredentials

from converter_pydub import convert_to_mp3
# from recorder_pyaudio import Recorder
from recorder_sounddevice import Recorder

# from plyer import notification

VERSION = "2021-12-01"
GUI = True
DRYRUN = False

MACOSRED = (236, 95, 93)
MACOSORANGE = (232, 135, 58)
MACOSYELLOW = (255, 200, 60)
MACOSGREEN = (120, 183, 86)
MACOSCYAN = (84, 153, 166)
MACOSBLUE = (48, 123, 246)
MACOSMAGENTA = (154, 86, 163)
MACOSDARK = (46, 46, 46)


def help():
    print("Version: {}".format(VERSION))
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


def parse_input(link, start_from=0):
    tracks = []

    if len(link) < 4:
        help()
    else:
        # A track URI or URL?
        if link.startswith("spotify:track:") or link.startswith("https://open.spotify.com/track/"):
            tracks = [link]

        # A txt list with track URIs or URLs?
        elif link.endswith(".txt"):
            file = open(link)
            tracks = file.readlines()
            file.close()

        # A playlist URI or URL?
        elif link.startswith("spotify:playlist:") or link.startswith(
                "https://open.spotify.com/playlist/"):
            if os.environ.get("SPOTIPY_CLIENT_ID") is not None and os.environ.get(
                    "SPOTIPY_CLIENT_SECRET") is not None:
                # Authenticating into spotify
                auth_manager = SpotifyClientCredentials()
                sp = spotipy.Spotify(auth_manager=auth_manager)

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
                tracks = uris
            else:
                print(colorama.Fore.LIGHTRED_EX,
                      "Error: fetching a playlist requires user authentication. Make sure Spotify Client ID and Client Secret are set.",
                      colorama.Style.RESET_ALL)
                tracks = []

        # An album URI or URL?
        elif link.startswith("spotify:album:") or link.startswith("https://open.spotify.com/album/"):
            if os.environ.get("SPOTIPY_CLIENT_ID") is not None and os.environ.get(
                    "SPOTIPY_CLIENT_SECRET") is not None:
                # Authenticating into spotify
                auth_manager = SpotifyClientCredentials()
                sp = spotipy.Spotify(auth_manager=auth_manager)

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
                tracks = urls
            else:
                print(colorama.Fore.LIGHTRED_EX,
                      "Error: fetching an album requires user authentication. Make sure Spotify Client ID and Client Secret are set.",
                      colorama.Style.RESET_ALL)
                tracks = []

        # An artist URI or URL?
        # https://open.spotify.com/artist/5Pqc0ZFA20Y9zGJZ3ojUin?si=M5y9h5sxTgSnhSf9ZjLcbQ
        elif link.startswith("spotify:artist:") or link.startswith(
                "https://open.spotify.com/artist/"):
            if os.environ.get("SPOTIPY_CLIENT_ID") is not None and os.environ.get(
                    "SPOTIPY_CLIENT_SECRET") is not None:
                # Authenticating into spotify
                auth_manager = SpotifyClientCredentials()
                sp = spotipy.Spotify(auth_manager=auth_manager)

                # Fetching this artist's top tracks
                results = sp.artist_top_tracks(link)
                items = results['tracks']
                urls = []
                for item in items:
                    track = item['external_urls']
                    urls.append(track['spotify'])
                tracks = urls
            else:
                print(colorama.Fore.LIGHTRED_EX,
                      "Error: fetching an album requires user authentication. Make sure Spotify Client ID and Client Secret are set.",
                      colorama.Style.RESET_ALL)
                tracks = []

        else:
            print("Unknown input")

    if start_from == 0:
        return tracks
    else:
        return tracks[start_from:]


def remove_bad_characters(s):
    bad_chars = [';', ':', '!', '*', '/', '\\']
    for i in bad_chars:
        s = s.replace(i, '')
    return s


def resource_path(path):
    # Needed only is the path is relative
    if not os.path.isabs(path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, path)
        return os.path.join(os.path.abspath('.'), path)
    else:
        return path


class Ripper:
    def __init__(self,
                 ripped_folder_structure='flat',
                 rip_dir=os.path.expanduser('~') + '/Downloads/Ripped/',
                 gui=False,
                 gui_progress_callback=None,
                 gui_soundbar_callback=None):
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

    def rip(self, track):
        toprint = "Ripping track {}...".format(track)
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
        self.recfile = Recorder(self.tmp_dir + self.tmp_wav, terminal_width=self.terminal_width,
                                gui=self.gui, gui_soundbar_callback=self.gui_soundbar_callback)
        # self.recfile.getinfo()

        self.recfile.start_recording()

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

        # Print artist and track names extracted from Spotify
        toprint = "Track: {}, {}".format(artist, track)
        if self.gui:
            self.gui_progress_callback.emit(toprint)
        else:
            try:
                print(colorama.Back.LIGHTGREEN_EX,
                      toprint + (self.terminal_width - len(toprint) - 6) * ' ',
                      colorama.Style.RESET_ALL)
                push("Now recording...", toprint)
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

        # Convert to mp3 and notify if an error occurs
        if convert_to_mp3(self.tmp_dir + self.tmp_wav,
                          self.tmp_dir + self.tmp_mp3):
            push("Finished", toprint)
        else:
            toprint = "Error in conversion."
            if self.gui:
                self.gui_progress_callback.emit(toprint)
            else:
                print(toprint)

        time.sleep(.500)

        # Set and/or update ID3 information
        mp3file = eyed3.load(self.tmp_dir + self.tmp_mp3)
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


'''
Command-line version
'''


def main():
    colorama.init()
    if not os.environ.get('PYTHONIOENCODING'):
        os.environ['PYTHONIOENCODING'] = str("utf-8")

    # Understand what the command line input is
    tracks = []
    if len(sys.argv) < 2:
        help()
    elif len(sys.argv) == 2:
        tracks = parse_input(sys.argv[1])
    elif len(sys.argv) == 3:
        try:
            start_from = int(sys.argv[2]) - 1
        except:
            start_from = 0
        tracks = parse_input(sys.argv[1], start_from)

    print("Ripping {} tracks.".format(len(tracks)))
    for track in tracks:
        if not DRYRUN:
            ripper = Ripper()
            ripper.rip(convert_to_uri(track.rstrip()))
        else:
            print(track)


'''
GUI version
'''


def main_gui():
    class WorkerSignals(QObject):
        '''
        Defines the signals available from a running worker thread.

        Supported signals are:

        finished
            No data

        error
            tuple (exctype, value, traceback.format_exc() )

        result
            object data returned from processing, anything

        progress
            int indicating % progress

        '''
        finished = Signal()
        error = Signal(tuple)
        result = Signal(object)
        progress_signal = Signal(str)
        soundbar_signal = Signal(float)

    class Worker(QRunnable):
        '''
        Worker thread

        Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

        :param callback: The function callback to run on this worker thread. Supplied args and
                         kwargs will be passed through to the runner.
        :type callback: function
        :param args: Arguments to pass to the callback function
        :param kwargs: Keywords to pass to the callback function

        '''

        def __init__(self, fn, *args, **kwargs):
            super(Worker, self).__init__()

            # Store constructor arguments (re-used for processing)
            self.fn = fn
            self.args = args
            self.kwargs = kwargs
            self.signals = WorkerSignals()

            # Add the callback to our kwargs
            self.kwargs['progress_callback'] = self.signals.progress_signal
            self.kwargs['soundbar_callback'] = self.signals.soundbar_signal

        @Slot()
        def run(self):
            '''
            Initialise the runner function with passed args, kwargs.
            '''

            # Retrieve args/kwargs here; and fire processing using them
            try:
                result = self.fn(*self.args, **self.kwargs)
            except:
                traceback.print_exc()
                exctype, value = sys.exc_info()[:2]
                self.signals.error.emit((exctype, value, traceback.format_exc()))
            else:
                self.signals.result.emit(result)  # Return the result of the processing
            finally:
                self.signals.finished.emit()  # Done

    class Highlighter(QSyntaxHighlighter):
        def __init__(self, parent):
            super(Highlighter, self).__init__(parent)
            self.trackFormat = QTextCharFormat()
            self.trackFormat.setForeground(Qt.white)
            self.trackFormat.setBackground(QColor(MACOSGREEN[0], MACOSGREEN[1], MACOSGREEN[2]))

            self.warningFormat = QTextCharFormat()
            self.warningFormat.setForeground(Qt.black)
            self.warningFormat.setBackground(QColor(MACOSYELLOW[0], MACOSYELLOW[1], MACOSYELLOW[2]))

            self.errorFormat = QTextCharFormat()
            self.errorFormat.setForeground(Qt.white)
            self.errorFormat.setBackground(QColor(MACOSRED[0], MACOSRED[1], MACOSRED[2]))

        def highlightBlock(self, text):
            # uncomment this line for Python2
            # text = unicode(text)
            if text.startswith('Track'):
                self.setFormat(0, len(text), self.trackFormat)
            elif text.startswith('Warning'):
                self.setFormat(0, len(text), self.warningFormat)
            elif text.startswith('Error'):
                self.setFormat(0, len(text), self.errorFormat)

    class MainWindow(QMainWindow):
        def __init__(self):
            window_w = 700
            window_h = 300

            link_h = 30
            button_w = 60
            label_w = 30
            spinbox_w = 60

            soundbar_h = 10

            volume_h = 20
            volume_w = 70
            margin = 10
            link_w = window_w - 3 * margin - button_w
            soundbar_w = window_w - 3 * margin - volume_w
            detail_h = window_h - 5 * margin - link_h - volume_h - 30

            QMainWindow.__init__(self)

            self.setFixedSize(QSize(window_w, window_h))
            self.setWindowTitle("Spotiripper" + " " + VERSION)
            # app.setWindowIcon(QIcon(resource_path('FotoPDF.png')))

            self.link_widget = QLineEdit(self)
            self.link_widget.setAlignment(Qt.AlignCenter)
            # self.link_widget.setText("Paste link from Spotify")
            # self.link_widget.setText(QApplication.clipboard().text())
            # Useful for debugging
            self.link_widget.setText("https://open.spotify.com/album/02GEKxoVe5ITAj68mZRAM7?si=Lt987xTASliFEqZAvkTrdw")
            # self.link_widget.insertPlainText("Paste link from Spotify")
            self.link_widget.setGeometry(margin, margin, link_w, link_h)

            self.button = QPushButton(self)
            self.button.setText("Rip")
            self.button.setGeometry(margin + link_w + margin, margin, button_w, link_h)
            self.button.clicked.connect(self.button_clicked)

            start_label = QLabel(self)
            start_label.setText("from")
            start_label.setGeometry(margin, margin + link_h + margin, label_w, link_h)

            self.start_spinbox = QSpinBox(self)
            self.start_spinbox.setMinimum(1)
            self.start_spinbox.setMaximum(100)
            self.start_spinbox.setSingleStep(1)
            self.start_spinbox.setValue(1)
            self.start_spinbox.setGeometry(margin + label_w + margin, margin + link_h + margin, spinbox_w, link_h)

            self.detail_widget = QTextEdit(self)
            highlighter = Highlighter(self.detail_widget.document())
            self.detail_widget.setReadOnly(True)
            self.detail_widget.setText("")
            self.detail_widget.setGeometry(margin, 3 * margin + 2 * link_h, margin + link_w + button_w, detail_h)
            self.detail_widget.setStyleSheet("background-color: rgb{}; color: rgb(255,255,255);".format(str(MACOSDARK)))

            self.soundbar = QProgressBar(self)
            self.soundbar.setValue(0)
            self.soundbar.setGeometry(margin, 4 * margin + 2 * link_h + detail_h + 5,
                                      soundbar_w, soundbar_h)

            self.volume = QLineEdit(self)
            self.volume.setFont(QFont("Courier New", 12))
            self.volume.setGeometry(2 * margin + soundbar_w, 4 * margin + 2 * link_h + detail_h,
                                    volume_w, volume_h)
            self.volume.setReadOnly(True)
            self.max_volume = 0.0

            QApplication.clipboard().dataChanged.connect(self.clipboard_changed)

            self.threadpool = QThreadPool()
            print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        def clipboard_changed(self):
            self.link_widget.setText(QApplication.clipboard().text())

        def progress_fn(self, s):
            self.detail_widget.append(s)

        def soundbar_fn(self, x):
            self.soundbar.setValue(x * 100.0)
            if self.max_volume < x:
                self.max_volume = x
            self.volume.setText("{:4.2f}/{:4.2f}".format(x, self.max_volume))

        def execute_this_fn(self, progress_callback, soundbar_callback):
            tracks = parse_input(self.link_widget.text(), int(self.start_spinbox.value()) - 1)
            progress_callback.emit("Ripping {} tracks.".format(len(tracks)))

            for track in tracks:
                if not DRYRUN:
                    ripper = Ripper(gui=True,
                                    gui_progress_callback=progress_callback,
                                    gui_soundbar_callback=soundbar_callback)
                    self.max_volume = 0.0
                    ripper.rip(convert_to_uri(track.rstrip()))
                else:
                    progress_callback.emit(track)

        def print_output(self, s):
            print(s)

        def thread_complete(self):
            # Re-enable fields
            self.button.setEnabled(True)
            self.link_widget.setReadOnly(False)
            self.start_spinbox.setReadOnly(False)

        def button_clicked(self):
            # Pass the function to execute
            worker = Worker(self.execute_this_fn)  # Any other args, kwargs are passed to the run function
            worker.signals.result.connect(self.print_output)
            worker.signals.finished.connect(self.thread_complete)
            worker.signals.progress_signal.connect(self.progress_fn)
            worker.signals.soundbar_signal.connect(self.soundbar_fn)

            # Disable fields
            self.button.setEnabled(False)
            self.link_widget.setReadOnly(True)
            self.start_spinbox.setReadOnly(True)

            # Clear detail widget
            self.detail_widget.setText("")

            # Execute
            self.threadpool.start(worker)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    if GUI:
        main_gui()
    else:
        main()
