'''
DOCUMENTATION
https://python-sounddevice.readthedocs.io/en/0.4.3/examples.html
'''

'''
Non-blocking mode (start and stop recording):
self.recfile = Recorder(filename)
self.recfile.start_recording()
...
self.recfile.stop_recording()
'''

import tempfile
import queue
import sys
import sounddevice as sd
import soundfile as sf
import threading
import colorama
import numpy  # Make sure NumPy is loaded before it is used in the callback
from soundbar import SoundBar

assert numpy  # avoid "imported but unused" message (W0611)


class Recorder(object):
    def __init__(self,
                 fname=None,
                 terminal_width=80,
                 gui=False,
                 gui_progress_callback=None,
                 gui_soundbar_callback=None):

        if fname is None:
            self.fname = tempfile.mktemp(prefix='sounddevice_', suffix='.wav', dir='')
        else:
            self.fname = fname

        self.mode = 'x'

        self.terminal_width = terminal_width
        self.gui = gui
        self.gui_progress_callback = gui_progress_callback
        self.gui_soundbar_callback = gui_soundbar_callback

        raw_devices = sd.query_devices()
        self.default_input_device = sd.query_devices(kind='input')
        self.default_output_device = sd.query_devices(kind='output')

        # Check if the input device name seems correct
        if "blackhole" not in self.default_input_device['name'].lower():
            toprint = "Warning: the input device '{}' seems not to be 'BlackHole'".format(
                self.default_input_device['name'])
            if self.gui:
                gui_progress_callback.emit(toprint)
            else:
                print(colorama.Fore.LIGHTYELLOW_EX, toprint, colorama.Style.RESET_ALL)
        self.device = raw_devices.index(self.default_input_device)

        self.device_info = sd.query_devices(self.device, kind='input')

        # Check if the number of input channels seems correct
        self.channels = int(self.device_info['max_input_channels'])
        if self.channels != 2:
            toprint = "Warning: the number of channels ({}) is not 2.".format(self.channels)
            if self.gui:
                gui_progress_callback.emit(toprint)
            else:
                print(colorama.Fore.LIGHTYELLOW_EX, toprint, colorama.Style.RESET_ALL)

        self.rate = int(self.device_info['default_samplerate'])

        # Check if the number of output channels seems correct
        if self.default_output_device['max_output_channels'] != self.channels:
            toprint = "Warning: the numbers of channels of the output ({}) and input ({}) devices do not correspond.".format(
                self.default_output_device['max_output_channels'], self.channels)
            if self.gui:
                gui_progress_callback.emit(toprint)
            else:
                print(colorama.Fore.LIGHTYELLOW_EX, toprint, colorama.Style.RESET_ALL)

        # Check if the sample rate of the output device seems correct
        if self.default_output_device['default_samplerate'] != self.rate:
            toprint = "Warning: the sample rates of the output ({}) and input ({}) devices do not correspond.".format(
                self.default_output_device['default_samplerate'], self.rate)
            if self.gui:
                gui_progress_callback.emit(toprint)
            else:
                print(colorama.Fore.LIGHTYELLOW_EX, toprint, colorama.Style.RESET_ALL)

        self.subtype = None
        self.q = queue.Queue()
        self.t = None

        self.bar = SoundBar(limitx=1.0,
                            terminal_width=self.terminal_width,
                            gui=self.gui,
                            gui_soundbar_callback=self.gui_soundbar_callback)

    def getinfo(self):
        print(self.terminal_width * '*')
        print("Portaudio version")
        print(sd.get_portaudio_version())
        print()

        print("Recording file")
        print(self.fname)
        print()

        print("All devices")
        raw_devices = sd.query_devices()
        print(raw_devices)
        print()

        print("Device that will be used:")
        print("Device #: {}".format(self.device))
        print("Channels: {}".format(self.channels))
        print("Rate #: {}".format(self.rate))
        print(self.terminal_width * '*')

    def _callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    def _record(self, arg):
        t = threading.current_thread()

        with sf.SoundFile(self.fname,
                          mode=self.mode,
                          samplerate=self.rate,
                          channels=self.channels,
                          subtype=self.subtype) as file:
            with sd.InputStream(samplerate=self.rate,
                                device=self.device,
                                channels=self.channels,
                                callback=self._callback):
                while getattr(t, "do_run", True):
                    block = self.q.get()
                    self.bar.update(numpy.mean(numpy.max(block, axis=0)))
                    file.write(block)

    def start_recording(self):
        self.t = threading.Thread(target=self._record, args=("task",))
        self.t.start()

    def stop_recording(self):
        self.t.do_run = False
        self.t.join()

# a = Recorder()
# a.getinfo()
