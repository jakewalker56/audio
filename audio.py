#!/usr/bin/env python
"""Play a fixed frequency sound."""
from __future__ import division
import math

from pyaudio import PyAudio # sudo apt-get install python{,3}-pyaudio
import matplotlib.pyplot as plt
import random

try:
    from itertools import izip
except ImportError: # Python 3
    izip = zip
    xrange = range

class Waveform(object):
    phase = 0.0
    frequency = 0
    amplitude = 1
    start = 0
    duration = 1
   
    # The class "constructor" - It's actually an initializer 
    def __init__(self, frequency, phase, amplitude, start, duration):
        self.phase = phase
        self.frequency = frequency
        self.amplitude = amplitude
        self.start = start
        self.duration = duration

def sample_combined_waveforms(waveforms, t, sample_rate, noise=0):
    value = 0
    for wf in waveforms:
        if (float(t) / float(sample_rate)) > wf.start and (float(t) / float(sample_rate)) < (wf.start + wf.duration):
            value += wf.amplitude * math.sin(2 * math.pi * (wf.frequency * t / sample_rate + wf.phase))
    value = value* (1 + random.random()* noise)
    return value

def play_tone(waveforms, duration, volume, sample_rate, noise):
    n_samples = int(sample_rate * duration)
    restframes = n_samples % sample_rate

    p = PyAudio()
    stream = p.open(format=p.get_format_from_width(1), # 8bit
                    channels=1, 
                    rate=sample_rate,
                    output=True)

    samples = (int(volume * sample_combined_waveforms(waveforms, t, sample_rate, noise) * 0x7f + 0x80) for t in xrange(n_samples))
    stream.write(bytes(bytearray(samples)))
    
    # fill remainder of frameset with silence
    stream.write(b'\x80' * restframes)

    stream.stop_stream()
    stream.close()
    p.terminate()

def graph_tone(waveforms, sample_rate, n_samples=2000, offset=0):
    x = (int(t) for t in xrange(n_samples))
    samples = (int( sample_combined_waveforms(waveforms, t + offset * sample_rate, sample_rate) * 0x7f + 0x80) for t in xrange(n_samples))
    plt.clf()
    plt.plot(list(x), list(samples), 'b-')
    plt.draw()
    plt.pause(0.001)
        

#22050
sample_rate=int(7*22050)
starting = 441.1
increment = 1.0595

waveforms = [
    Waveform(frequency = starting, phase=0, amplitude = 1, start = 0, duration = 1),
    Waveform(frequency = starting * increment ** 4, phase=0, amplitude = 1, start = 0, duration = 1),
    
    Waveform(frequency = starting, phase=0, amplitude = 1, start = 1, duration = 1),
    Waveform(frequency = starting * 2, phase=0, amplitude = 1, start = 1, duration = 1),

    Waveform(frequency = starting , phase=0, amplitude = 1, start = 2, duration = 1),
    Waveform(frequency = starting * 2, phase=0.3, amplitude = 1, start = 2, duration = 1)
]

graph_tone(waveforms, sample_rate, 2000, 2.1)

play_tone(
    waveforms = waveforms, 
    duration=3,
    volume=.01, 
    sample_rate=sample_rate,
    noise = 0
)