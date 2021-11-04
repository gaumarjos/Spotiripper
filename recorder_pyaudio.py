# -*- coding: utf-8 -*-
'''
DOCUMENTATION
https://raspberrypi.stackexchange.com/questions/69611/pyaudio-record-audio-using-non-blocking-callback
https://dolby.io/blog/capturing-high-quality-audio-with-python-and-pyaudio/
'''

'''
Blocking mode (record for a set duration):
rec = Recorder(channels=2)
with rec.open('blocking.wav', 'wb') as recfile:
    recfile.record(duration=5.0)
'''

'''
Non-blocking mode (start and stop recording):
self.recfile = Recorder(filename, 'wb', 2, 44100, 1024)
self.recfile.start_recording()
...
self.recfile.stop_recording()
'''

import tempfile
import colorama
import pyaudio
import wave
from soundbar import SoundBar
import numpy


class Recorder(object):
    def __init__(self, fname=None):

        if fname is None:
            self.fname = tempfile.mktemp(prefix='pyaudio_', suffix='.wav', dir='')
        else:
            self.fname = fname

        self.mode = 'wb'

        self._pa = pyaudio.PyAudio()
        self.default_output_device = self._pa.get_default_output_device_info()
        self.default_input_device = self._pa.get_default_input_device_info()

        if "blackhole" not in self.default_input_device['name'].lower():
            print(colorama.Fore.LIGHTYELLOW_EX,
                  "Warning: the input device '{}' seems not to be 'BlackHole'".format(
                      self.default_input_device['name']),
                  colorama.Style.RESET_ALL)

        self.channels = int(self.default_input_device['maxInputChannels'])
        if self.channels != 2:
            print(colorama.Fore.LIGHTYELLOW_EX,
                  "Warning: the number of channels ({}) is not 2.".format(self.channels),
                  colorama.Style.RESET_ALL)

        self.rate = int(self.default_input_device['defaultSampleRate'])

        # Check output device (not strictly necessary for recording, just making sure output and input parameters
        # correspond)
        if self.default_output_device['maxOutputChannels'] != self.channels:
            print(colorama.Fore.LIGHTYELLOW_EX,
                  "Warning: the number of channels of the output ({}) and input ({}) devices do not correspond.".format(
                      self.default_output_device['maxOutputChannels'], self.channels),
                  colorama.Style.RESET_ALL)
        if self.default_output_device['defaultSampleRate'] != self.rate:
            print(colorama.Fore.LIGHTYELLOW_EX,
                  "Warning: the sample rate of the output ({}) and input ({}) devices do not correspond.".format(
                      self.default_output_device['defaultSampleRate'], self.rate),
                  colorama.Style.RESET_ALL)

        self.frames_per_buffer = 1024

        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None

        self.bar = SoundBar(limitx=1.0)

    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        self.close()

    def getinfo(self):
        print(80 * '*')
        print("Portaudio version")
        print(pyaudio.get_portaudio_version())
        print()

        print("Recording file")
        print(self.fname)
        print()

        print("All devices")
        for id in range(self._pa.get_device_count()):
            dev_dict = self._pa.get_device_info_by_index(id)
            for key, value in dev_dict.items():
                print(key, value)
            print()
        print()

        print("Output device")
        print(self.default_output_device)
        print()

        print("Input device")
        print(self.default_input_device)
        print()

        print("Device that will be used:")
        print("Channels: {}".format(self.channels))
        print("Rate #: {}".format(self.rate))
        print(80 * '*')

    def record(self, duration):
        # Use a stream with no callback function in blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                     channels=self.channels,
                                     rate=self.rate,
                                     input=True,
                                     frames_per_buffer=self.frames_per_buffer)
        for _ in range(int(self.rate / self.frames_per_buffer * duration)):
            audio = self._stream.read(self.frames_per_buffer)
            self.wavefile.writeframes(audio)
        return None

    def start_recording(self):
        # Use a stream with a callback in non-blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                     channels=self.channels,
                                     rate=self.rate,
                                     input=True,
                                     frames_per_buffer=self.frames_per_buffer,
                                     stream_callback=self.get_callback())
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()

        # The following 3 lines seems to be unnecessary. I put them there to be extra sure nothing is left open.
        self._stream.close()
        self.wavefile.close()
        self._pa.terminate()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            self.bar.update(numpy.max(numpy.fromstring(in_data, numpy.int16) / 65535.0))
            return in_data, pyaudio.paContinue

        return callback

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile


# a = Recorder()
# a.getinfo()
