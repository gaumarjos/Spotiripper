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

import pyaudio
import wave


class Recorder(object):
    def __init__(self, fname, mode, channels,
                 rate, frames_per_buffer):
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None

    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        self.close()

    def getinfo(self):
        # Version
        print(pyaudio.get_portaudio_version())

        # Default devices
        print(self._pa.get_default_output_device_info())
        print(self._pa.get_default_input_device_info())

        # All devices
        for id in range(self._pa.get_device_count()):
            dev_dict = self._pa.get_device_info_by_index(id)
            for key, value in dev_dict.items():
                print(key, value)

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
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue

        return callback

    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile
