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
from bar import SoundBar

assert numpy  # avoid "imported but unused" message (W0611)


class Recorder(object):
    def __init__(self, fname=None):

        if fname is None:
            self.fname = tempfile.mktemp(prefix='sounddevice_', suffix='.wav', dir='')
        else:
            self.fname = fname

        self.mode = 'x'

        raw_devices = sd.query_devices()
        self.default_input_device = sd.query_devices(kind='input')
        self.default_output_device = sd.query_devices(kind='output')

        if "blackhole" not in self.default_input_device['name'].lower():
            print(colorama.Fore.LIGHTYELLOW_EX,
                  "Warning: the input device '{}' seems not to be 'BlackHole'".format(
                      self.default_input_device['name']),
                  colorama.Style.RESET_ALL)
        self.device = raw_devices.index(self.default_input_device)

        self.device_info = sd.query_devices(self.device, kind='input')

        self.channels = int(self.device_info['max_input_channels'])
        if self.channels != 2:
            print(colorama.Fore.LIGHTYELLOW_EX,
                  "Warning: the number of channels ({}) is not 2.".format(self.channels),
                  colorama.Style.RESET_ALL)

        self.rate = int(self.device_info['default_samplerate'])

        # Check output device (not strictly necessary for recording, just making sure output and input parameters
        # correspond)
        if self.default_output_device['max_output_channels'] != self.channels:
            print(colorama.Fore.LIGHTYELLOW_EX,
                  "Warning: the number of channels of the output ({}) and input ({}) devices do not correspond.".format(
                      self.default_output_device['max_output_channels'], self.channels),
                  colorama.Style.RESET_ALL)
        if self.default_output_device['default_samplerate'] != self.rate:
            print(colorama.Fore.LIGHTYELLOW_EX,
                  "Warning: the sample rate of the output ({}) and input ({}) devices do not correspond.".format(
                      self.default_output_device['default_samplerate'], self.rate),
                  colorama.Style.RESET_ALL)

        self.subtype = None

        self.q = queue.Queue()
        self.t = None

        self.bar = SoundBar(maxvalue=1.0)

    def getinfo(self):
        print(80 * '*')
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
        print(80 * '*')

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
