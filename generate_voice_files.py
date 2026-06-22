# generate_voice_files.py
import numpy as np
import soundfile as sf
import os

def generate_tone(freq, duration=3, sr=16000, amplitude=0.5):
    t = np.linspace(0, duration, int(sr * duration))
    return amplitude * np.sin(2 * np.pi * freq * t)

# Ensure directories exist
os.makedirs('voices/default', exist_ok=True)

# Male singer: 110 Hz (A2)
male_audio = generate_tone(110, duration=3)
sf.write('voices/default/male_singer.wav', male_audio, 16000)

# Female singer: 220 Hz (A3)
female_audio = generate_tone(220, duration=3)
sf.write('voices/default/female_singer.wav', female_audio, 16000)

print("✅ Dummy voice files created at voices/default/")
