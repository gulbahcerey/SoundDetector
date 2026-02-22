print("FILE Started", flush=True)
import numpy as np
import sounddevice as sd
import tensorflow_hub as hub
import pandas as pd
from pathlib import Path
import time
from collections import deque, Counter

YAMNET_HANDLE = "https://tfhub.dev/google/yamnet/1"


#category mapping
def map_to_category(label: str) -> str:

    s = label.lower()

    if any(k in s for k in [
        "speech", "conversation", "narration", "whispering", "shout", "yell",
        "scream", "laugh", "giggle", "cough", "sneeze"
    ]):
        return "Person"

    if any(k in s for k in [
        "dog", "bark", "howl", "cat", "meow", "purr", "bird", "chirp", "tweet",
        "rooster", "cow", "sheep", "goat", "horse", "pig", "insect"
    ]):
        return "Animal"

    if any(k in s for k in [
        "siren", "alarm", "smoke alarm", "fire alarm", "bell", "doorbell",
        "knock", "buzzer", "horn", "car alarm"
    ]):
        return "Alarm"

    return "Other"


def run_realtime(output_queue=None, stop_event=None):
    print("Loading YAMNet (first run may take a bit)...", flush=True)
    yamnet = hub.load(YAMNET_HANDLE)
    IGNORE_LABELS = {"Silence", "Inside, small room"}

    def is_ignored(label: str) -> bool:
        return label in IGNORE_LABELS

    model_dir = Path(hub.resolve(YAMNET_HANDLE))
    class_map = model_dir / "assets" / "yamnet_class_map.csv"
    if not class_map.exists():
        found = list(model_dir.rglob("yamnet_class_map.csv"))
        if not found:
            raise FileNotFoundError("yamnet_class_map.csv not found in TFHub cache.")
        class_map = found[0]

    df = pd.read_csv(class_map)
    class_names = df["display_name"].tolist()

    sr = 16000
    chunk_sec = 1.0
    chunk_samples = int(sr * chunk_sec)
    WINDOW = 6
    MIN_STABLE = 2
    history = deque(maxlen=WINDOW)

    stable_category = "Other"
    stable_label = "Unknown"

    print("\nReal-time listening started. Press Ctrl+C to stop.")
    print("Tip: make a sound (talk, clap, play alarm) near mic.\n")

    last_print_time = 0.0

    with sd.InputStream(samplerate=sr, channels=1, dtype="float32", blocksize=chunk_samples) as stream:
        try:
            while True:
                if stop_event and stop_event.is_set():
                    break
                audio, _ = stream.read(chunk_samples)
                waveform = audio[:, 0]

                rms = float(np.sqrt(np.mean(waveform ** 2)))
                print(f"DEBUG rms={rms:.4f}", flush=True)

                if rms < 0.002:
                    if time.time() - last_print_time > 2.0:
                        print("Silence...")
                        last_print_time = time.time()
                    continue

                scores, _, _ = yamnet(waveform)
                scores_np = scores.numpy()
                mean_scores = scores_np.mean(axis=0)

                topN = 5
                top_idxs = mean_scores.argsort()[-topN:][::-1]

                top_label = class_names[int(top_idxs[0])]
                top_score = float(mean_scores[int(top_idxs[0])])
                category = map_to_category(top_label)

                if is_ignored(top_label):
                    for idx in top_idxs[1:]:
                        cand_label = class_names[int(idx)]
                        cand_score = float(mean_scores[int(idx)])

                        cand_cat = map_to_category(cand_label)
                        if cand_cat != "Other" and cand_score >= 0.05:
                            top_label, top_score, category = cand_label, cand_score, cand_cat
                            break

                    if is_ignored(top_label):
                        for idx in top_idxs[1:]:
                            cand_label = class_names[int(idx)]
                            if not is_ignored(cand_label):
                                top_label = cand_label
                                top_score = float(mean_scores[int(idx)])
                                category = map_to_category(top_label)
                                break



                if top_score < 0.03:
                    category = "Other"
                    top_label = "Unknown"
                print(f"DEBUG {category} | {top_label} | score={top_score:.2f}", flush=True)
                history.append(category)

                counts = Counter(history)
                best_cat, best_count = counts.most_common(1)[0]

                if best_count >= MIN_STABLE:
                    stable_category = best_cat
                    if top_label != "Unknown" and map_to_category(top_label) == stable_category:
                        stable_label = top_label

                if output_queue:
                    output_queue.put({
                        "category": stable_category,
                        "label": stable_label,
                        "conf": float(top_score),
                        "rms": float(rms),
                    })
                time.sleep(0.01)

        except KeyboardInterrupt:
            print("\nStopped.", flush=True)





if __name__ == "__main__":
    run_realtime()