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
import numpy  # Make sure NumPy is loaded before it is used in the callback

assert numpy  # avoid "imported but unused" message (W0611)


class Recorder(object):
    def __init__(self, fname=None, mode=None, device=None, channels=None, rate=None, frames_per_buffer=None):

        if fname is None:
            self.fname = tempfile.mktemp(prefix='delme_rec_unlimited_', suffix='.wav', dir='')
        else:
            self.fname = fname

        if mode is None:
            self.mode = 'x'
        else:
            self.mode = mode

        if device is None:
            raw_devices = sd.query_devices()
            default_input_device = sd.query_devices(kind='input')
            self.device = raw_devices.index(default_input_device)
        else:
            self.device = device

        self.device_info = sd.query_devices(self.device, kind='input')

        if channels is None:
            self.channels = int(self.device_info['max_input_channels'])
        else:
            self.channels = channels

        if rate is None:
            self.rate = int(self.device_info['default_samplerate'])
        else:
            self.rate = rate

        self.subtype = None

        self.frames_per_buffer = frames_per_buffer

        self.q = queue.Queue()
        self.t = None

    def getinfo(self):
        # Version
        print(sd.get_portaudio_version())

        # Default devices
        # print(self._pa.get_default_output_device_info())
        # print(self._pa.get_default_input_device_info())

        print("Recording file")
        print(self.fname)

        print("All devices")
        print(sd.query_devices())

        print("Device that will be used:")
        print("Device #: {}".format(self.device))
        print("Channels: {}".format(self.channels))
        print("Rate #: {}".format(self.rate))

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
                    file.write(self.q.get())

    def start_recording(self):
        self.t = threading.Thread(target=self._record, args=("task",))
        self.t.start()

    def stop_recording(self):
        self.t.do_run = False
        self.t.join()
