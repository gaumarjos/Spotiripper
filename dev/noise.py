import subprocess, sys, os, time, shutil, eyed3
from urllib.request import urlopen
import pyaudio
import wave
from recorder_pyaudio import Recorder
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import colorama
from pydub import AudioSegment


def detect_leading_silence(sound, silence_threshold=-200.0, chunk_size=10):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while sound[trim_ms:trim_ms + chunk_size].dBFS > silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms


sound = AudioSegment.from_file("../tmp/tmp.wav", format="wav")

start_trim = detect_leading_silence(sound)
# end_trim = detect_leading_silence(sound.reverse())

print(start_trim)

start_trim = 160
duration = len(sound)
trimmed_sound = sound[start_trim:duration - 0]

print(len(sound))


output = AudioSegment.empty()
output = trimmed_sound
output.export("cacca.mp3", format="mp3")


