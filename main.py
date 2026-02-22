
import sounddevice as sd
from scipy.io.wavfile import write
from pathlib import Path
import realtime_detect

def record_aud():
    duration = 3
    fs = 44100

    print("Recording...", flush=True)
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    out_path = Path(__file__).parent / "out.wav"
    write(str(out_path), fs, audio)
    print("Recording finished:", out_path, flush=True)

def main():

    print("1) Record audio to file")
    print("2) Real-time sound detection")
    choice = input("Select (1/2): ").strip()

    if choice == "1":
        record_aud()
    elif choice == "2":
        realtime_detect.run_realtime()
    else:
        print("Invalid choice")
if __name__ == "__main__":
    main()

