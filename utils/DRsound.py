#!/usr/bin/python 

import pyaudio
import wave


def beep():

    wf = wave.open('./utils/sounds/beep.wav', 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format =
                p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)
    data = wf.readframes(32768)
    while data != '':
      stream.write(data)
      data = wf.readframes(32768)
    stream.close()
    p.terminate()
