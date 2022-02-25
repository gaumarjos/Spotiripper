import os
import sys
import traceback
import settings_lib
import colorama
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from ripper import Ripper
import spotiripper_helper

VERSION = "2022-02-25"
DRYRUN = False
PYSIDE_VERSION = 2

if PYSIDE_VERSION == 2:
    from PySide2.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QSpinBox, QLabel, \
        QProgressBar, QDialog, QDialogButtonBox, QVBoxLayout, QGridLayout, QAction
    from PySide2.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QIcon
    from PySide2.QtCore import Qt, QSize, QRunnable, Slot, Signal, QObject, QThreadPool
elif PYSIDE_VERSION == 6:
    from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QSpinBox, QLabel, \
        QProgressBar, QDialog, QDialogButtonBox, QVBoxLayout, QGridLayout
    from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QIcon, QAction
    from PySide6.QtCore import Qt, QSize, QRunnable, Slot, Signal, QObject, QThreadPool

current_path = spotiripper_helper.get_current_path()


def main():
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
            self.trackFormat.setBackground(QColor(spotiripper_helper.MACOSGREEN[0], spotiripper_helper.MACOSGREEN[1],
                                                  spotiripper_helper.MACOSGREEN[2]))

            self.warningFormat = QTextCharFormat()
            self.warningFormat.setForeground(Qt.black)
            self.warningFormat.setBackground(
                QColor(spotiripper_helper.MACOSYELLOW[0], spotiripper_helper.MACOSYELLOW[1],
                       spotiripper_helper.MACOSYELLOW[2]))

            self.errorFormat = QTextCharFormat()
            self.errorFormat.setForeground(Qt.white)
            self.errorFormat.setBackground(
                QColor(spotiripper_helper.MACOSRED[0], spotiripper_helper.MACOSRED[1], spotiripper_helper.MACOSRED[2]))

        def highlightBlock(self, text):
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
            app.setWindowIcon(QIcon(spotiripper_helper.resource_path('spotiripper.png')))

            self.link_widget = QLineEdit(self)
            self.link_widget.setAlignment(Qt.AlignCenter)
            # self.link_widget.setText("Paste link from Spotify")
            # self.link_widget.setText(QApplication.clipboard().text())

            # Useful for debugging
            # self.link_widget.setText("https://open.spotify.com/album/02GEKxoVe5ITAj68mZRAM7?si=Lt987xTASliFEqZAvkTrdw")

            self.link_widget.setPlaceholderText("Paste link from Spotify")
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
            self.detail_widget.setStyleSheet(
                "background-color: rgb{}; color: rgb(255,255,255);".format(str(spotiripper_helper.MACOSDARK)))

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
            # print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

            # Menu bar
            change_settings_action = QAction("&Edit settings", self)
            change_settings_action.setStatusTip("This is your button")
            change_settings_action.triggered.connect(self.settings_menu)
            menu = self.menuBar()
            file_menu = menu.addMenu("&Spotiripper")
            file_menu.addAction(change_settings_action)

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
            tracks, error = spotiripper_helper.parse_input(self.link_widget.text(), int(self.start_spinbox.value()) - 1)
            if error is None:
                progress_callback.emit("Ripping {} track{}.".format(len(tracks), "s" if len(tracks) > 1 else ""))
                for track in tracks:
                    # Load settings (in theory, they could have been changed in the meanwhile)
                    settings = settings_lib.load_settings()
                    if not DRYRUN:
                        ripper = Ripper(current_path=current_path,
                                        rip_dir=settings["rip_dir"],
                                        ripped_folder_structure=settings["ripped_folder_structure"],
                                        gui=True,
                                        gui_progress_callback=progress_callback,
                                        gui_soundbar_callback=soundbar_callback)
                        self.max_volume = 0.0
                        ripper.rip(spotiripper_helper.convert_to_uri(track.rstrip()))
                    else:
                        progress_callback.emit(track)

            elif error == 'spotipy_keys':
                progress_callback.emit(
                    "Error: fetching a playlist requires user authentication. Make sure Spotify Client ID and Client Secret are set.")

            elif error == 'unknown_input':
                progress_callback.emit("Error: unknown input.")

            else:
                pass

        def result_fn(self, s):
            pass

        def finished_fn(self):
            # Re-enable fields
            self.button.setEnabled(True)
            self.link_widget.setReadOnly(False)
            self.start_spinbox.setReadOnly(False)

        def button_clicked(self):
            # Pass the function to execute
            worker = Worker(self.execute_this_fn)  # Any other args, kwargs are passed to the run function
            worker.signals.result.connect(self.result_fn)
            worker.signals.finished.connect(self.finished_fn)
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

        def settings_menu(self):
            dlg = self.SettingsDialog()
            dlg.exec()

        class SettingsDialog(QDialog):
            def __init__(self, parent=None):  # <1>
                super().__init__(parent)

                settings = settings_lib.load_settings()

                self.setWindowTitle("Settings")
                self.setFixedSize(QSize(500, 240))

                grid_layout = QGridLayout()
                grid_layout.rowMinimumHeight(40)

                rip_dir_label = QLabel(self)
                rip_dir_label.setText("Rip directory")
                rip_dir_label.setFixedHeight(25)
                rip_dir_edit = QLineEdit(self)
                rip_dir_edit.setText(settings["rip_dir"])
                rip_dir_edit.setFixedHeight(25)
                grid_layout.addWidget(rip_dir_label, 0, 0)
                grid_layout.addWidget(rip_dir_edit, 0, 1)

                spotipy_client_id_label = QLabel(self)
                spotipy_client_id_label.setText("Spotipy Cliend ID")
                spotipy_client_id_label.setFixedHeight(25)
                spotipy_client_id_edit = QLineEdit(self)
                spotipy_client_id_edit.setText(settings["spotipy_client_id"])
                spotipy_client_id_edit.setFixedHeight(25)
                grid_layout.addWidget(spotipy_client_id_label, 1, 0)
                grid_layout.addWidget(spotipy_client_id_edit, 1, 1)

                spotipy_client_secret_label = QLabel(self)
                spotipy_client_secret_label.setText("Spotipy Cliend Secret")
                spotipy_client_secret_label.setFixedHeight(25)
                spotipy_client_secret_edit = QLineEdit(self)
                spotipy_client_secret_edit.setText(settings["spotipy_client_secret"])
                spotipy_client_secret_edit.setFixedHeight(25)
                grid_layout.addWidget(spotipy_client_secret_label, 2, 0)
                grid_layout.addWidget(spotipy_client_secret_edit, 2, 1)

                spotipy_client_info_label = QLabel(self)
                spotipy_client_info_label.setText(
                    "If left empty, env. variables SPOTIPY_CLIENT_ID\nand SPOTIPY_CLIENT_SECRET will be used.")
                spotipy_client_info_label.setFixedHeight(50)
                grid_layout.addWidget(spotipy_client_info_label, 3, 1)

                buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                buttonbox.accepted.connect(self.accept)
                self.accepted.connect(lambda: settings_lib.write_setting((("rip_dir",
                                                                           rip_dir_edit.text()),
                                                                          ("spotipy_client_id",
                                                                           spotipy_client_id_edit.text()),
                                                                          ("spotipy_client_secret",
                                                                           spotipy_client_secret_edit.text()))))
                buttonbox.rejected.connect(self.reject)

                layout = QVBoxLayout()
                layout.addLayout(grid_layout)
                layout.addWidget(buttonbox)
                self.setLayout(layout)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    if PYSIDE_VERSION == 2:
        sys.exit(app.exec_())
    elif PYSIDE_VERSION == 6:
        sys.exit(app.exec())


if __name__ == "__main__":
    if not os.path.exists(os.path.join(current_path, "settings.json")):
        settings_lib.create_settings()
    main()
