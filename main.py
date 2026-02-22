# main.py
import sounddevice as sd
from scipy.io.wavfile import write
from pathlib import Path
import numpy as np

def record_aud():
    duration = 3
    fs = 44100

    print("Recording...", flush=True)
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="float32")  # FIXED: dtype
    sd.wait()

    audio_int16 = np.int16(np.clip(audio, -1.0, 1.0) * 32767)
    out_path = Path(__file__).parent / "out.wav"
    write(str(out_path), fs, audio_int16)

    print("Recording finished:", out_path, flush=True)

if __name__ == "__main__":
    record_aud()